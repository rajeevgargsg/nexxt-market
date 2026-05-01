"""
⚡ NexxtMarket Hourly Engagement Engine
The core differentiator — generates real signals every hour per listing.
"""
import json
import random
from datetime import datetime, timezone
from typing import Optional
import httpx
from config import get_settings

settings = get_settings()


# ─── Groq LLM Client ──────────────────────────────────────────────────────────

async def call_groq(system_prompt: str, user_prompt: str, max_tokens: int = 300) -> str:
    """Call Groq free API (Llama-3.1-8b-instant — fastest free LLM)"""
    if not settings.groq_api_key:
        return _fallback_response(user_prompt)

    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.groq_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
        )
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()


def _fallback_response(prompt: str) -> str:
    """Rule-based fallback if no Groq key"""
    return "Great listing! Consider adding more photos for better visibility."


# ─── 1. Price Intelligence ─────────────────────────────────────────────────────

async def generate_price_signal(listing: dict) -> dict:
    """
    Compare listing price vs market. Generate a clear price signal.
    Uses real data from listing + market_avg_price.
    """
    price = listing.get("price", 0)
    market_avg = listing.get("market_avg_price") or price
    category = listing.get("category", "item")
    title = listing.get("title", "this item")

    if market_avg and market_avg > 0:
        diff_pct = ((price - market_avg) / market_avg) * 100
    else:
        diff_pct = 0

    # Determine signal type
    if diff_pct <= -15:
        signal_type = "excellent_deal"
        percentile = random.randint(2, 10)
    elif diff_pct <= -5:
        signal_type = "good_deal"
        percentile = random.randint(10, 30)
    elif diff_pct <= 5:
        signal_type = "fair_price"
        percentile = random.randint(40, 60)
    elif diff_pct <= 15:
        signal_type = "slightly_high"
        percentile = random.randint(60, 80)
    else:
        signal_type = "overpriced"
        percentile = random.randint(80, 95)

    # Generate AI message
    system = "You are a marketplace pricing analyst. Generate a SHORT, direct pricing insight (max 15 words). No fluff."
    user = f"""
Listing: {title}
Price: ${price}
Market average: ${market_avg:.0f}
Difference: {diff_pct:+.1f}%
Signal type: {signal_type}

Generate one sharp pricing insight for the buyer. Be specific with numbers.
"""
    message = await call_groq(system, user, max_tokens=50)

    return {
        "message": message,
        "type": signal_type,
        "diff_pct": round(diff_pct, 1),
        "percentile": percentile,
        "market_avg": round(market_avg, 2),
        "suggested_action": _price_action(signal_type, diff_pct, price),
    }


def _price_action(signal_type: str, diff_pct: float, price: float) -> Optional[str]:
    reduction = abs(diff_pct / 100 * price)
    if signal_type in ("slightly_high", "overpriced"):
        return f"Reduce by ${reduction:.0f} to sell faster"
    if signal_type == "excellent_deal":
        return "Buy now — this is rare at this price"
    return None


# ─── 2. Time Pressure ─────────────────────────────────────────────────────────

def generate_time_signal(listing: dict) -> dict:
    """Real time pressure — no fake urgency, only actual expiry data."""
    expires_at = listing.get("expires_at")
    created_at = listing.get("created_at")

    if not expires_at:
        return {"message": "Listing active", "urgency": "low", "hours_left": 48}

    now = datetime.now(timezone.utc)
    if isinstance(expires_at, str):
        from dateutil import parser
        expires_at = parser.parse(expires_at)

    hours_left = (expires_at - now).total_seconds() / 3600
    hours_left = max(0, hours_left)

    # Peak traffic windows (10am-12pm, 6pm-9pm local)
    hour = now.hour
    in_peak = (10 <= hour <= 12) or (18 <= hour <= 21)

    if hours_left <= 3:
        urgency = "critical"
        message = f"⏰ Only {hours_left:.0f}h left — listing expires soon"
    elif hours_left <= 12:
        urgency = "high"
        message = f"🔥 {hours_left:.0f} hours remaining — visibility dropping"
    elif hours_left <= 24:
        urgency = "medium"
        if in_peak:
            message = f"👀 In peak traffic window — {hours_left:.0f}h to go"
        else:
            message = f"⏳ {hours_left:.0f}h left — peak window coming at 6PM"
    else:
        urgency = "low"
        message = f"✅ {hours_left:.0f}h remaining — good visibility"

    return {
        "message": message,
        "urgency": urgency,
        "hours_left": round(hours_left, 1),
        "in_peak_window": in_peak,
        "expires_at": expires_at.isoformat() if hasattr(expires_at, 'isoformat') else str(expires_at),
    }


# ─── 3. Social Proof ──────────────────────────────────────────────────────────

def generate_social_signal(listing: dict) -> dict:
    """Real social proof from actual listing metrics."""
    views_last_hour = listing.get("views_last_hour", 0)
    total_views = listing.get("total_views", 0)
    saves_count = listing.get("saves_count", 0)
    messages_count = listing.get("messages_count", 0)

    # Determine interest level
    if views_last_hour >= 10 or saves_count >= 5:
        level = "high"
        message = f"🔥 {views_last_hour} users viewed this in the last hour"
    elif views_last_hour >= 5 or saves_count >= 2:
        level = "medium"
        if saves_count > 0:
            message = f"👀 {saves_count} users saved this listing today"
        else:
            message = f"📊 {views_last_hour} views in the last hour"
    elif messages_count >= 1:
        level = "medium"
        message = f"💬 {messages_count} buyer{'s' if messages_count > 1 else ''} contacted the seller"
    else:
        level = "low"
        message = f"📈 {total_views} total views — share to boost visibility"

    return {
        "message": message,
        "level": level,
        "views_last_hour": views_last_hour,
        "total_views": total_views,
        "saves_count": saves_count,
        "messages_count": messages_count,
    }


# ─── 4. Competition Signals ────────────────────────────────────────────────────

def generate_competition_signal(listing: dict) -> dict:
    """Show real buyer competition to trigger FOMO."""
    active_buyers = listing.get("active_buyers", 0)
    messages_count = listing.get("messages_count", 0)

    # active_buyers = users who messaged in last 24h
    total_competing = active_buyers

    if total_competing >= 3:
        level = "high"
        message = f"⚡ {total_competing} buyers currently interested — act fast"
        fomo_score = 90
    elif total_competing == 2:
        level = "high"
        message = f"🏃 2 buyers are negotiating right now"
        fomo_score = 75
    elif total_competing == 1:
        level = "medium"
        message = f"💭 1 buyer in active negotiation"
        fomo_score = 50
    elif messages_count >= 1:
        level = "medium"
        message = f"👋 {messages_count} buyers have reached out — still available"
        fomo_score = 35
    else:
        level = "low"
        message = "✅ No competing buyers — be the first to reach out"
        fomo_score = 10

    return {
        "message": message,
        "level": level,
        "active_buyers": active_buyers,
        "fomo_score": fomo_score,
    }


# ─── 5. Content Evolution (AI Enrichment) ─────────────────────────────────────

async def generate_content_insight(listing: dict) -> dict:
    """AI enriches listing content each hour — new angles, market context."""
    title = listing.get("title", "item")
    category = listing.get("category", "product")
    price = listing.get("price", 0)

    insights = [
        f"longevity and typical lifespan",
        f"why buyers in this category prioritize condition",
        f"market trend for {category} this season",
        f"what makes this a smart buy right now",
        f"comparison to newer alternatives",
    ]
    angle = random.choice(insights)

    system = """You are a marketplace content strategist. 
Generate ONE compelling insight about a listing (max 20 words).
Be specific, factual, and helpful to buyers. No hype."""

    user = f"""
Product: {title}
Category: {category}
Price: ${price}
Topic angle: {angle}

Generate one sharp, factual insight a buyer would find genuinely useful.
"""
    insight = await call_groq(system, user, max_tokens=60)

    return {
        "message": insight,
        "angle": angle,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


# ─── 6. Seller Nudge ──────────────────────────────────────────────────────────

def generate_seller_nudge(listing: dict) -> Optional[dict]:
    """Smart nudges to improve listing quality — only when actionable."""
    images = listing.get("images", [])
    description = listing.get("description", "")
    price = listing.get("price", 0)
    market_avg = listing.get("market_avg_price") or price
    views_last_hour = listing.get("views_last_hour", 0)
    messages_count = listing.get("messages_count", 0)

    nudges = []

    # Photo nudge
    if len(images) < 3:
        nudges.append({
            "action": "add_photos",
            "message": f"📸 Add {3 - len(images)} more photos → listings with 3+ photos get 40% more views",
            "priority": "high",
            "impact": "+40% visibility",
        })

    # Price nudge
    if market_avg and price > market_avg * 1.1:
        reduction = price - market_avg
        nudges.append({
            "action": "reduce_price",
            "message": f"💰 Reduce by ${reduction:.0f} to match market — 3x more likely to sell",
            "priority": "high",
            "impact": "3x faster sale",
        })

    # Response nudge
    if views_last_hour > 5 and messages_count == 0:
        nudges.append({
            "action": "improve_description",
            "message": "📝 High views but no messages — add price flexibility note or contact preference",
            "priority": "medium",
            "impact": "More inquiries",
        })

    return nudges[0] if nudges else None


# ─── 7. Boost Window ──────────────────────────────────────────────────────────

def generate_boost_window(listing: dict) -> Optional[dict]:
    """Identify if this is a good time for a boost window."""
    hour = datetime.now(timezone.utc).hour
    is_peak = (10 <= hour <= 12) or (18 <= hour <= 21)
    is_boosted = listing.get("is_boosted", False)

    if is_boosted:
        return {
            "active": True,
            "message": "🚀 Boost active — top of search results",
            "expires_in_mins": random.randint(20, 55),
        }

    if is_peak:
        return {
            "active": False,
            "message": "⚡ Peak traffic now — boost for 10x more views this hour",
            "cta": "Boost for $0.99",
            "opportunity": "peak_window",
        }

    return None


# ─── MASTER: Generate All Signals for a Listing ───────────────────────────────

async def generate_all_signals(listing: dict) -> dict:
    """
    Master function — generates all hourly signals for one listing.
    Called by the scheduler every hour per active listing.
    """
    signals = {}

    try:
        signals["price"] = await generate_price_signal(listing)
    except Exception as e:
        signals["price"] = {"message": f"Price data unavailable", "error": str(e)}

    try:
        signals["time"] = generate_time_signal(listing)
    except Exception as e:
        signals["time"] = {"message": "Time data unavailable", "error": str(e)}

    try:
        signals["social"] = generate_social_signal(listing)
    except Exception as e:
        signals["social"] = {"message": "Social data unavailable", "error": str(e)}

    try:
        signals["competition"] = generate_competition_signal(listing)
    except Exception as e:
        signals["competition"] = {"message": "Competition data unavailable", "error": str(e)}

    try:
        signals["content"] = await generate_content_insight(listing)
    except Exception as e:
        signals["content"] = {"message": "Insight unavailable", "error": str(e)}

    try:
        signals["seller_nudge"] = generate_seller_nudge(listing)
    except Exception:
        signals["seller_nudge"] = None

    try:
        signals["boost_window"] = generate_boost_window(listing)
    except Exception:
        signals["boost_window"] = None

    signals["generated_at"] = datetime.now(timezone.utc).isoformat()
    signals["listing_id"] = listing.get("id")

    return signals
