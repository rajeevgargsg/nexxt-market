"""
NexxtMarket FastAPI Backend
"""
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, update
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr, validator
import json
import uuid

from config import get_settings
from database import get_db, get_redis, async_engine
from models import Base, User, Listing, ListingStatus, ListingEngagement, \
    Message, SavedListing, Notification, ListingActivityLog

settings = get_settings()

app = FastAPI(
    title="NexxtMarket API",
    description="AI-Driven Classified Marketplace",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


# ─── Startup ──────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ─── Auth ──────────────────────────────────────────────────────────────────────

def create_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# ─── Pydantic Schemas ─────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None


class UserOut(BaseModel):
    id: str
    email: str
    username: str
    full_name: Optional[str]
    trust_score: float
    total_sales: int
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ListingCreate(BaseModel):
    title: str
    description: str
    price: float
    category_id: Optional[str] = None
    location: Optional[str] = None
    condition: Optional[str] = "good"
    images: Optional[List[str]] = []
    tags: Optional[List[str]] = []
    duration_hours: Optional[int] = 48

    @validator("price")
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("price must be positive")
        return v

    @validator("duration_hours")
    def duration_must_be_valid(cls, v):
        if v not in (24, 48, 72):
            raise ValueError("duration_hours must be 24, 48, or 72")
        return v


class ListingOut(BaseModel):
    id: str
    title: str
    description: str
    price: float
    location: Optional[str]
    condition: Optional[str]
    images: Optional[List] = []
    tags: Optional[List] = []
    status: str
    total_views: int
    saves_count: int
    messages_count: int
    active_buyers: int
    is_boosted: bool
    ai_deal_score: Optional[float]
    market_avg_price: Optional[float]
    price_percentile: Optional[int]
    expires_at: Optional[datetime]
    created_at: datetime
    seller_id: str

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    listing_id: str
    receiver_id: str
    content: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


# ─── Auth Routes ──────────────────────────────────────────────────────────────

@app.post("/auth/register", response_model=TokenResponse, tags=["Auth"])
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check existing
    r = await db.execute(select(User).where(User.email == data.email))
    if r.scalar_one_or_none():
        raise HTTPException(400, "Email already registered")

    user = User(
        id=str(uuid.uuid4()),
        email=data.email,
        username=data.username,
        full_name=data.full_name,
        hashed_password=pwd_context.hash(data.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_token({"sub": user.id})
    return {"access_token": token, "token_type": "bearer", "user": user}


@app.post("/auth/token", response_model=TokenResponse, tags=["Auth"])
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(User).where(User.email == form.username))
    user = r.scalar_one_or_none()
    if not user or not pwd_context.verify(form.password, user.hashed_password):
        raise HTTPException(400, "Invalid credentials")

    token = create_token({"sub": user.id})
    return {"access_token": token, "token_type": "bearer", "user": user}


# ─── Listing Routes ───────────────────────────────────────────────────────────

@app.post("/listing/create", response_model=ListingOut, tags=["Listings"])
async def create_listing(
    data: ListingCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    now = datetime.now(timezone.utc)
    listing = Listing(
        id=str(uuid.uuid4()),
        seller_id=current_user.id,
        title=data.title,
        description=data.description,
        price=data.price,
        category_id=data.category_id,
        location=data.location,
        condition=data.condition,
        images=data.images or [],
        tags=data.tags or [],
        duration_hours=data.duration_hours,
        expires_at=now + timedelta(hours=data.duration_hours),
        rank_score=70.0,
    )
    db.add(listing)
    await db.commit()
    await db.refresh(listing)

    # Trigger AI optimization in background
    background_tasks.add_task(run_ai_optimization, listing.id)

    return listing


@app.get("/listing/feed", response_model=List[ListingOut], tags=["Listings"])
async def get_feed(
    category: Optional[str] = None,
    location: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort: Optional[str] = "rank",  # rank, newest, price_asc, price_desc
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    query = select(Listing).where(Listing.status == ListingStatus.ACTIVE)

    if category:
        query = query.where(Listing.category_id == category)
    if location:
        query = query.where(Listing.location.ilike(f"%{location}%"))
    if min_price:
        query = query.where(Listing.price >= min_price)
    if max_price:
        query = query.where(Listing.price <= max_price)

    # Sorting
    if sort == "newest":
        query = query.order_by(desc(Listing.created_at))
    elif sort == "price_asc":
        query = query.order_by(Listing.price.asc())
    elif sort == "price_desc":
        query = query.order_by(Listing.price.desc())
    else:  # rank (boosted first, then by score)
        query = query.order_by(desc(Listing.is_boosted), desc(Listing.rank_score))

    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@app.get("/listing/{listing_id}", tags=["Listings"])
async def get_listing(
    listing_id: str,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    result = await db.execute(select(Listing).where(Listing.id == listing_id))
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(404, "Listing not found")

    # Increment view count
    await db.execute(
        update(Listing).where(Listing.id == listing_id).values(
            total_views=Listing.total_views + 1,
            views_last_hour=Listing.views_last_hour + 1,
        )
    )

    # Get cached signals
    cached = await redis.get(f"signals:{listing_id}")
    signals = json.loads(cached) if cached else None

    return {
        "listing": {
            "id": listing.id,
            "title": listing.title,
            "description": listing.description,
            "price": listing.price,
            "location": listing.location,
            "condition": listing.condition,
            "images": listing.images,
            "tags": listing.tags,
            "status": listing.status,
            "total_views": listing.total_views + 1,
            "saves_count": listing.saves_count,
            "messages_count": listing.messages_count,
            "active_buyers": listing.active_buyers,
            "is_boosted": listing.is_boosted,
            "ai_deal_score": listing.ai_deal_score,
            "market_avg_price": listing.market_avg_price,
            "price_percentile": listing.price_percentile,
            "expires_at": listing.expires_at.isoformat() if listing.expires_at else None,
            "created_at": listing.created_at.isoformat() if listing.created_at else None,
            "seller_id": listing.seller_id,
        },
        "signals": signals,
    }


@app.get("/listing/{listing_id}/activity", tags=["Listings"])
async def get_listing_activity(listing_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ListingEngagement)
        .where(ListingEngagement.listing_id == listing_id)
        .order_by(desc(ListingEngagement.generated_at))
        .limit(10)
    )
    return result.scalars().all()


@app.post("/listing/{listing_id}/save", tags=["Listings"])
async def save_listing(
    listing_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check if already saved
    r = await db.execute(
        select(SavedListing).where(
            SavedListing.user_id == current_user.id,
            SavedListing.listing_id == listing_id,
        )
    )
    existing = r.scalar_one_or_none()
    if existing:
        await db.delete(existing)
        await db.execute(
            update(Listing).where(Listing.id == listing_id).values(
                saves_count=Listing.saves_count - 1
            )
        )
        return {"saved": False}

    saved = SavedListing(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        listing_id=listing_id,
    )
    db.add(saved)
    await db.execute(
        update(Listing).where(Listing.id == listing_id).values(
            saves_count=Listing.saves_count + 1
        )
    )
    return {"saved": True}


@app.post("/listing/boost", tags=["Listings"])
async def boost_listing(
    listing_id: str,
    boost_type: str = "standard",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Listing).where(Listing.id == listing_id))
    listing = result.scalar_one_or_none()
    if not listing or listing.seller_id != current_user.id:
        raise HTTPException(403, "Not authorized")

    # In production, validate payment here (Stripe, etc.)
    await db.execute(
        update(Listing).where(Listing.id == listing_id).values(
            is_boosted=True,
            boost_expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            rank_score=95.0,
        )
    )
    return {"boosted": True, "expires_in": "1 hour"}


@app.get("/listing/my", tags=["Listings"])
async def get_my_listings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all listings for the authenticated seller (dashboard)."""
    result = await db.execute(
        select(Listing)
        .where(Listing.seller_id == current_user.id)
        .order_by(desc(Listing.created_at))
    )
    listings = result.scalars().all()
    return {"listings": listings, "total": len(listings)}


# ─── AI Routes ────────────────────────────────────────────────────────────────

@app.post("/ai/optimize-listing", tags=["AI"])
async def ai_optimize(listing_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Listing).where(Listing.id == listing_id))
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(404, "Listing not found")

    from agents import optimize_listing
    optimized = await optimize_listing({
        "title": listing.title,
        "description": listing.description,
        "price": listing.price,
        "condition": listing.condition,
        "images": listing.images,
    })

    # Save AI suggestions
    await db.execute(
        update(Listing).where(Listing.id == listing_id).values(
            ai_title=optimized.get("optimized_title"),
            ai_description=optimized.get("optimized_description"),
            ai_tags=optimized.get("suggested_tags"),
            ai_suggested_price=optimized.get("suggested_price"),
            ai_deal_score=optimized.get("deal_score"),
        )
    )
    return optimized


@app.get("/ai/reply-suggestion", tags=["AI"])
async def reply_suggestion(
    listing_id: str,
    role: str = "buyer",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Listing).where(Listing.id == listing_id))
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(404, "Listing not found")

    msgs = await db.execute(
        select(Message).where(Message.listing_id == listing_id).limit(10)
    )
    messages = [{"role": "user", "content": m.content} for m in msgs.scalars().all()]

    from agents import suggest_reply
    suggestion = await suggest_reply(listing.title, messages, role)
    return {"suggestion": suggestion}


# ─── Recommendations ──────────────────────────────────────────────────────────

@app.get("/recommendations", response_model=List[ListingOut], tags=["Recommendations"])
async def get_recommendations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Simple: return high-scoring listings user hasn't seen
    result = await db.execute(
        select(Listing)
        .where(Listing.status == ListingStatus.ACTIVE)
        .where(Listing.seller_id != current_user.id)
        .order_by(desc(Listing.rank_score))
        .limit(20)
    )
    return result.scalars().all()


# ─── Messages ─────────────────────────────────────────────────────────────────

@app.post("/messages", tags=["Messages"])
async def send_message(
    data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    msg = Message(
        id=str(uuid.uuid4()),
        listing_id=data.listing_id,
        sender_id=current_user.id,
        receiver_id=data.receiver_id,
        content=data.content,
    )
    db.add(msg)

    # Update listing metrics
    await db.execute(
        update(Listing).where(Listing.id == data.listing_id).values(
            messages_count=Listing.messages_count + 1,
            active_buyers=Listing.active_buyers + 1,
        )
    )
    return {"sent": True, "message_id": msg.id}


@app.get("/messages/{listing_id}", tags=["Messages"])
async def get_messages(
    listing_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Message).where(
            Message.listing_id == listing_id,
            (Message.sender_id == current_user.id) | (Message.receiver_id == current_user.id)
        ).order_by(Message.created_at)
    )
    return result.scalars().all()


# ─── Notifications ────────────────────────────────────────────────────────────

@app.get("/notifications", tags=["Notifications"])
async def get_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(desc(Notification.created_at))
        .limit(50)
    )
    return result.scalars().all()


# ─── Health Check ─────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


# ─── Background Tasks ─────────────────────────────────────────────────────────

async def run_ai_optimization(listing_id: str):
    """Background: optimize listing with AI after creation."""
    from database import AsyncSessionLocal
    from agents import optimize_listing, analyze_listing_trust
    from sqlalchemy import update

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Listing).where(Listing.id == listing_id))
        listing = result.scalar_one_or_none()
        if not listing:
            return

        optimized = await optimize_listing({
            "title": listing.title,
            "description": listing.description,
            "price": listing.price,
            "condition": listing.condition,
            "images": listing.images or [],
        })

        await db.execute(
            update(Listing).where(Listing.id == listing_id).values(
                ai_title=optimized.get("optimized_title"),
                ai_description=optimized.get("optimized_description"),
                ai_tags=optimized.get("suggested_tags", []),
                ai_suggested_price=optimized.get("suggested_price"),
                ai_deal_score=optimized.get("deal_score"),
            )
        )
        await db.commit()
