"""
Data Models — NexxtMarket
"""
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text,
    ForeignKey, JSON, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid
import enum


def gen_uuid():
    return str(uuid.uuid4())


# ─── Enums ────────────────────────────────────────────────────────────────────

class ListingStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    SOLD = "sold"
    PAUSED = "paused"
    PENDING = "pending"


class ListingDuration(int, enum.Enum):
    H24 = 24
    H48 = 48
    H72 = 72


class BoostType(str, enum.Enum):
    STANDARD = "standard"
    FEATURED = "featured"
    URGENT = "urgent"


# ─── User ─────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, unique=True, nullable=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    avatar_url = Column(String)
    bio = Column(Text)

    # Trust metrics
    trust_score = Column(Float, default=50.0)
    total_sales = Column(Integer, default=0)
    total_purchases = Column(Integer, default=0)
    response_rate = Column(Float, default=0.0)
    avg_response_time_mins = Column(Integer, default=0)
    is_verified = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    listings = relationship("Listing", back_populates="seller")
    messages_sent = relationship("Message", back_populates="sender", foreign_keys="Message.sender_id")


# ─── Category ─────────────────────────────────────────────────────────────────

class Category(Base):
    __tablename__ = "categories"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    icon = Column(String)
    parent_id = Column(String, ForeignKey("categories.id"), nullable=True)


# ─── Listing ──────────────────────────────────────────────────────────────────

class Listing(Base):
    __tablename__ = "listings"

    id = Column(String, primary_key=True, default=gen_uuid)
    seller_id = Column(String, ForeignKey("users.id"), nullable=False)
    category_id = Column(String, ForeignKey("categories.id"))

    # Core content
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    location = Column(String)
    condition = Column(String)  # new, like_new, good, fair, poor
    images = Column(JSON, default=list)  # list of image URLs
    tags = Column(JSON, default=list)

    # Lifecycle
    status = Column(SAEnum(ListingStatus), default=ListingStatus.ACTIVE)
    duration_hours = Column(Integer, default=48)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    sold_at = Column(DateTime(timezone=True), nullable=True)

    # AI-generated fields
    ai_title = Column(String)
    ai_description = Column(Text)
    ai_tags = Column(JSON, default=list)
    ai_suggested_price = Column(Float)
    ai_deal_score = Column(Float)  # 0-100

    # Engagement metrics (updated hourly)
    total_views = Column(Integer, default=0)
    views_last_hour = Column(Integer, default=0)
    saves_count = Column(Integer, default=0)
    messages_count = Column(Integer, default=0)
    active_buyers = Column(Integer, default=0)  # currently negotiating

    # Boost
    is_boosted = Column(Boolean, default=False)
    boost_expires_at = Column(DateTime(timezone=True), nullable=True)
    boost_type = Column(SAEnum(BoostType), nullable=True)

    # Market intelligence
    market_avg_price = Column(Float)
    price_percentile = Column(Integer)  # vs similar listings
    price_trend = Column(String)  # rising, falling, stable

    # Ranking
    rank_score = Column(Float, default=50.0)  # decays over time

    # Relationships
    seller = relationship("User", back_populates="listings")
    activity_logs = relationship("ListingActivityLog", back_populates="listing")
    engagements = relationship("ListingEngagement", back_populates="listing")
    messages = relationship("Message", back_populates="listing")


# ─── Listing Activity Log ──────────────────────────────────────────────────────

class ListingActivityLog(Base):
    __tablename__ = "listing_activity_logs"

    id = Column(String, primary_key=True, default=gen_uuid)
    listing_id = Column(String, ForeignKey("listings.id"), nullable=False)
    event_type = Column(String)  # view, save, message, boost, price_change, expiry_warning
    event_data = Column(JSON, default=dict)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    listing = relationship("Listing", back_populates="activity_logs")


# ─── Listing Engagement (Hourly AI Signals) ───────────────────────────────────

class ListingEngagement(Base):
    __tablename__ = "listing_engagements"

    id = Column(String, primary_key=True, default=gen_uuid)
    listing_id = Column(String, ForeignKey("listings.id"), nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Price intelligence
    price_signal = Column(JSON)   # {"message": "...", "type": "good_deal|overpriced|fair"}

    # Time pressure
    time_signal = Column(JSON)    # {"message": "...", "hours_left": N, "urgency": "high|medium|low"}

    # Social proof
    social_signal = Column(JSON)  # {"message": "...", "views": N, "saves": N}

    # Competition
    competition_signal = Column(JSON)  # {"message": "...", "active_buyers": N, "level": "high|medium|low"}

    # Content evolution
    content_insight = Column(JSON)    # {"message": "...", "tip": "..."}

    # Seller nudge
    seller_nudge = Column(JSON)   # {"message": "...", "action": "add_photo|reduce_price|respond"}

    listing = relationship("Listing", back_populates="engagements")


# ─── Message ──────────────────────────────────────────────────────────────────

class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=gen_uuid)
    listing_id = Column(String, ForeignKey("listings.id"), nullable=False)
    sender_id = Column(String, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(String, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    ai_reply_suggestion = Column(Text)  # AI-suggested reply
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    listing = relationship("Listing", back_populates="messages")
    sender = relationship("User", back_populates="messages_sent", foreign_keys=[sender_id])


# ─── Saved Listing (Watchlist) ─────────────────────────────────────────────────

class SavedListing(Base):
    __tablename__ = "saved_listings"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    listing_id = Column(String, ForeignKey("listings.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ─── Notification ─────────────────────────────────────────────────────────────

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    listing_id = Column(String, ForeignKey("listings.id"), nullable=True)
    type = Column(String)  # price_drop, expiry, competition, new_message
    title = Column(String)
    body = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
