"""
NexxtMarket Backend Test Suite
Run: cd backend && pytest tests/ -v
"""
import pytest
import sys
import os
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def make_listing(**kwargs):
    base = {
        "id": "test-1",
        "title": "Sony WH-1000XM4 Headphones",
        "description": "Excellent condition",
        "price": 180.0,
        "market_avg_price": 210.0,
        "price_percentile": 15,
        "category": "Electronics",
        "status": "active",
        "views": 120,
        "views_last_hour": 15,
        "total_views": 120,
        "saves": 8,
        "saves_count": 8,
        "messages_count": 3,
        "active_buyers": 4,
        "ai_deal_score": 78,
        "rank_score": 85.0,
        "is_boosted": False,
        "images": [],
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat(),
    }
    base.update(kwargs)
    return base


# ────────────────────────────── Price Intelligence ──────────────────────────────

@pytest.mark.asyncio
async def test_price_signal_below_market():
    from backend.services.engagement_engine import generate_price_signal
    r = await generate_price_signal(make_listing(price=150.0, market_avg_price=200.0))
    assert r["type"] in ["excellent_deal", "good_deal"]
    assert r["diff_pct"] == pytest.approx(-25.0, abs=0.1)


@pytest.mark.asyncio
async def test_price_signal_above_market():
    from backend.services.engagement_engine import generate_price_signal
    r = await generate_price_signal(make_listing(price=260.0, market_avg_price=200.0))
    assert r["diff_pct"] > 0


@pytest.mark.asyncio
async def test_price_signal_no_market_data():
    from backend.services.engagement_engine import generate_price_signal
    r = await generate_price_signal(make_listing(price=100.0, market_avg_price=None))
    assert isinstance(r, dict)
    assert "type" in r


@pytest.mark.asyncio
async def test_price_signal_zero_market():
    from backend.services.engagement_engine import generate_price_signal
    r = await generate_price_signal(make_listing(price=100.0, market_avg_price=0))
    assert isinstance(r, dict)


# ────────────────────────────── Time Pressure ──────────────────────────────────

def test_time_signal_critical():
    from backend.services.engagement_engine import generate_time_signal
    r = generate_time_signal(make_listing(
        expires_at=(datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
    ))
    assert r["urgency"] == "critical"
    assert r["hours_left"] <= 3


def test_time_signal_low():
    from backend.services.engagement_engine import generate_time_signal
    r = generate_time_signal(make_listing(
        expires_at=(datetime.now(timezone.utc) + timedelta(hours=48)).isoformat()
    ))
    assert r["urgency"] == "low"


def test_time_signal_has_keys():
    from backend.services.engagement_engine import generate_time_signal
    r = generate_time_signal(make_listing())
    for k in ["urgency", "hours_left", "in_peak_window"]:
        assert k in r, f"Missing key: {k}"


def test_time_signal_expired():
    from backend.services.engagement_engine import generate_time_signal
    r = generate_time_signal(make_listing(
        expires_at=(datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    ))
    assert isinstance(r, dict)
    assert r["hours_left"] == 0


# ────────────────────────────── Social Proof ───────────────────────────────────

def test_social_high():
    from backend.services.engagement_engine import generate_social_signal
    r = generate_social_signal(make_listing(views_last_hour=50, saves_count=25, messages_count=10))
    assert r["level"] in ["high", "very_high"]


def test_social_zero():
    from backend.services.engagement_engine import generate_social_signal
    r = generate_social_signal(make_listing(views_last_hour=0, saves_count=0, messages_count=0))
    assert r["level"] in ["low", "medium"]


def test_social_has_keys():
    from backend.services.engagement_engine import generate_social_signal
    r = generate_social_signal(make_listing())
    for k in ["level", "views_last_hour", "saves_count", "messages_count"]:
        assert k in r


# ────────────────────────────── Competition ────────────────────────────────────

def test_competition_high():
    from backend.services.engagement_engine import generate_competition_signal
    r = generate_competition_signal(make_listing(active_buyers=8, messages_count=5))
    assert r["level"] in ["high", "very_high"]
    assert r["fomo_score"] >= 70


def test_competition_low():
    from backend.services.engagement_engine import generate_competition_signal
    r = generate_competition_signal(make_listing(active_buyers=0, messages_count=0))
    assert r["level"] == "low"


def test_fomo_score_range():
    from backend.services.engagement_engine import generate_competition_signal
    r = generate_competition_signal(make_listing(active_buyers=3))
    assert 0 <= r["fomo_score"] <= 100


# ────────────────────────────── Full Signal Bundle ─────────────────────────────

@pytest.mark.asyncio
async def test_all_signals_has_all_keys():
    from backend.services.engagement_engine import generate_all_signals
    s = await generate_all_signals(make_listing())
    for k in ["price", "time", "social",
              "competition", "content", "seller_nudge", "boost_window"]:
        assert k in s, f"Missing: {k}"


@pytest.mark.asyncio
async def test_all_signals_minimal_input():
    from backend.services.engagement_engine import generate_all_signals
    s = await generate_all_signals({"id": "x", "title": "T", "price": 50.0})
    assert isinstance(s, dict)


@pytest.mark.asyncio
async def test_signal_performance():
    import time
    from backend.services.engagement_engine import generate_all_signals
    start = time.time()
    await generate_all_signals(make_listing())
    assert (time.time() - start) < 2.0


# ────────────────────────────── Seller Nudge ───────────────────────────────────

def test_nudge_no_images():
    from backend.services.engagement_engine import generate_seller_nudge
    r = generate_seller_nudge(make_listing(images=[]))
    if r:
        assert "action" in r or "message" in r


# ────────────────────────────── Pydantic Validators ────────────────────────────

def test_price_validator():
    from pydantic import BaseModel, validator, ValidationError
    class M(BaseModel):
        price: float
        @validator("price")
        def pos(cls, v):
            if v <= 0: raise ValueError("must be > 0")
            return v
    with pytest.raises(ValidationError):
        M(price=-1)
    assert M(price=5).price == 5.0


def test_duration_validator():
    from pydantic import BaseModel, validator, ValidationError
    class M(BaseModel):
        d: int
        @validator("d")
        def valid(cls, v):
            if v not in (24, 48, 72): raise ValueError()
            return v
    with pytest.raises(ValidationError):
        M(d=99)
    assert M(d=48).d == 48
