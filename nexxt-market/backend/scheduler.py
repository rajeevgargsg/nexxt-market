"""
⚡ NexxtMarket Scheduler — Hourly Engagement Engine
Runs every hour, processes all active listings, generates signals.
"""
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
import redis
import json

from config import get_settings
from database import SyncSessionLocal, sync_engine
from models import Base, Listing, ListingEngagement, ListingStatus, Notification, SavedListing

# Needed for sync-based scheduler
from services.engagement_engine import generate_all_signals

settings = get_settings()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scheduler")


# ─── Redis sync client ────────────────────────────────────────────────────────
redis_sync = redis.from_url(settings.redis_url, decode_responses=True)


# ─── Create tables ────────────────────────────────────────────────────────────
def init_db():
    Base.metadata.create_all(bind=sync_engine)
    logger.info("Database tables ready")


# ─── Main hourly job ──────────────────────────────────────────────────────────
async def run_hourly_engagement_engine():
    """
    Core hourly loop:
    1. Fetch all active listings
    2. Update engagement metrics
    3. Generate AI signals
    4. Store in DB + Redis
    5. Fire notifications for real signals
    """
    logger.info(f"⚡ Running hourly engagement engine at {datetime.now(timezone.utc)}")

    db: Session = SyncSessionLocal()
    try:
        now = datetime.now(timezone.utc)

        # 1. Get all active listings
        active_listings = db.query(Listing).filter(
            and_(
                Listing.status == ListingStatus.ACTIVE,
                Listing.expires_at > now,
            )
        ).all()

        logger.info(f"Processing {len(active_listings)} active listings")

        for listing in active_listings:
            try:
                await process_single_listing(listing, db, now)
            except Exception as e:
                logger.error(f"Error processing listing {listing.id}: {e}")
                continue

        # 2. Expire listings past their deadline
        expired = db.query(Listing).filter(
            and_(
                Listing.status == ListingStatus.ACTIVE,
                Listing.expires_at <= now,
            )
        ).all()

        for listing in expired:
            listing.status = ListingStatus.EXPIRED
            listing.rank_score = 0
            logger.info(f"Expired listing: {listing.id}")

        # 3. Decay rank scores for non-boosted listings
        db.query(Listing).filter(
            Listing.status == ListingStatus.ACTIVE,
            Listing.is_boosted == False,
        ).update(
            {Listing.rank_score: Listing.rank_score * 0.97},  # 3% hourly decay
            synchronize_session=False,
        )

        db.commit()
        logger.info("✅ Hourly engine complete")

    except Exception as e:
        logger.error(f"Hourly engine error: {e}")
        db.rollback()
    finally:
        db.close()


async def process_single_listing(listing: Listing, db: Session, now: datetime):
    """Process one listing: generate signals, store, cache, notify."""

    # Build listing dict for signal generation
    listing_dict = {
        "id": listing.id,
        "title": listing.title,
        "price": listing.price,
        "market_avg_price": listing.market_avg_price,
        "category": listing.category_id,
        "description": listing.description,
        "images": listing.images or [],
        "expires_at": listing.expires_at.isoformat() if listing.expires_at else None,
        "created_at": listing.created_at.isoformat() if listing.created_at else None,
        "total_views": listing.total_views,
        "views_last_hour": listing.views_last_hour,
        "saves_count": listing.saves_count,
        "messages_count": listing.messages_count,
        "active_buyers": listing.active_buyers,
        "is_boosted": listing.is_boosted,
    }

    # Generate all signals (AI + rule-based)
    signals = await generate_all_signals(listing_dict)

    # Store engagement record
    engagement = ListingEngagement(
        listing_id=listing.id,
        price_signal=signals.get("price"),
        time_signal=signals.get("time"),
        social_signal=signals.get("social"),
        competition_signal=signals.get("competition"),
        content_insight=signals.get("content"),
        seller_nudge=signals.get("seller_nudge"),
    )
    db.add(engagement)

    # Reset hourly view counter
    listing.views_last_hour = 0

    # Cache signals in Redis (30-second reads, 70-minute TTL)
    cache_key = f"signals:{listing.id}"
    redis_sync.setex(cache_key, 4200, json.dumps(signals))  # 70 min TTL

    # Fire re-engagement notifications
    await fire_smart_notifications(listing, signals, db, now)


async def fire_smart_notifications(
    listing: Listing,
    signals: dict,
    db: Session,
    now: datetime,
):
    """Fire notifications only on REAL signals — no spam."""
    notifications = []

    # Price drop notification → saved users
    price = signals.get("price", {})
    if price.get("type") in ("excellent_deal", "good_deal"):
        saved_users = db.query(SavedListing).filter(
            SavedListing.listing_id == listing.id
        ).all()
        for saved in saved_users:
            notifications.append(Notification(
                user_id=saved.user_id,
                listing_id=listing.id,
                type="great_deal",
                title="🔥 Great deal alert!",
                body=f"{listing.title[:50]} is now priced below market average",
            ))

    # Competition spike → saved users
    comp = signals.get("competition", {})
    if comp.get("level") == "high":
        saved_users = db.query(SavedListing).filter(
            SavedListing.listing_id == listing.id
        ).all()
        for saved in saved_users:
            notifications.append(Notification(
                user_id=saved.user_id,
                listing_id=listing.id,
                type="competition_spike",
                title="⚡ High competition!",
                body=f"Multiple buyers are interested in {listing.title[:40]}",
            ))

    # Expiry warning → seller
    time_sig = signals.get("time", {})
    if time_sig.get("urgency") in ("critical", "high"):
        notifications.append(Notification(
            user_id=listing.seller_id,
            listing_id=listing.id,
            type="expiry_warning",
            title="⏰ Listing expiring soon",
            body=f"Your listing '{listing.title[:40]}' has {time_sig.get('hours_left', 0):.0f}h left",
        ))

    # Seller nudge notification
    nudge = signals.get("seller_nudge")
    if nudge:
        notifications.append(Notification(
            user_id=listing.seller_id,
            listing_id=listing.id,
            type="seller_nudge",
            title="💡 Improve your listing",
            body=nudge.get("message", ""),
        ))

    # Batch insert notifications
    if notifications:
        db.bulk_save_objects(notifications)
        logger.info(f"Fired {len(notifications)} notifications for listing {listing.id}")


# ─── Entrypoint ───────────────────────────────────────────────────────────────

async def main():
    init_db()

    scheduler = AsyncIOScheduler()

    # Run every hour
    scheduler.add_job(
        run_hourly_engagement_engine,
        trigger=IntervalTrigger(hours=1),
        id="hourly_engagement",
        name="Hourly Engagement Engine",
        replace_existing=True,
        next_run_time=datetime.now(timezone.utc),  # Run immediately on start
    )

    # Refresh market price data every 6 hours
    scheduler.add_job(
        refresh_market_data,
        trigger=IntervalTrigger(hours=6),
        id="market_data_refresh",
        name="Market Data Refresh",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("✅ Scheduler started — hourly engagement engine active")

    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


async def refresh_market_data():
    """Update market average prices per category — runs every 6h."""
    logger.info("Refreshing market data...")
    db: Session = SyncSessionLocal()
    try:
        from sqlalchemy import func as sqlfunc
        # For each active listing, update market_avg_price based on similar listings
        result = db.execute("""
            UPDATE listings l
            SET market_avg_price = (
                SELECT AVG(price) FROM listings
                WHERE category_id = l.category_id
                AND status = 'active'
                AND id != l.id
            )
            WHERE status = 'active'
        """)
        db.commit()
        logger.info("Market data refreshed")
    except Exception as e:
        logger.error(f"Market data refresh error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
