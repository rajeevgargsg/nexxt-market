"""
Seed demo data — run once to populate DB with realistic listings.
python scripts/seed_data.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database import SyncSessionLocal, sync_engine
from models import Base, User, Listing, ListingStatus
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import uuid, random

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DEMO_USERS = [
    {"email": "alice@demo.com", "username": "alice_sg", "full_name": "Alice Tan"},
    {"email": "bob@demo.com",   "username": "bob_deals", "full_name": "Bob Lim"},
    {"email": "carol@demo.com", "username": "carol_market", "full_name": "Carol Wong"},
]

DEMO_LISTINGS = [
    {"title": "iPhone 14 Pro 256GB Deep Purple", "price": 950, "category_id": "electronics",
     "description": "Excellent condition, 6 months warranty remaining. No scratches, original accessories included.",
     "location": "Tampines, Singapore", "condition": "Like New"},
    {"title": "Honda Civic 2020 1.5 Turbo CVT", "price": 72000, "category_id": "vehicles",
     "description": "Low mileage 38,000km, full service history at Honda. One careful owner.",
     "location": "Jurong, Singapore", "condition": "Good"},
    {"title": "MacBook Pro M2 16-inch 512GB", "price": 1800, "category_id": "electronics",
     "description": "Bought 8 months ago, still has 4 months warranty. Used for light office work.",
     "location": "Orchard, Singapore", "condition": "Excellent"},
    {"title": "IKEA KALLAX Shelf 4x2 White", "price": 80, "category_id": "furniture",
     "description": "Self-assembled, good condition. Moving out so selling fast. Can help disassemble.",
     "location": "Bishan, Singapore", "condition": "Good"},
    {"title": "Sony WH-1000XM5 Wireless Headphones", "price": 280, "category_id": "electronics",
     "description": "Noise cancelling, barely used. Comes with all original accessories.",
     "location": "Clementi, Singapore", "condition": "Like New"},
    {"title": "PS5 Digital Edition + 4 Games", "price": 550, "category_id": "electronics",
     "description": "6 months old, all original packaging. Games: Spider-Man 2, FIFA 24, GTA V, Minecraft.",
     "location": "Woodlands, Singapore", "condition": "Good"},
    {"title": "Nike Air Jordan 1 Retro High OG UK9", "price": 220, "category_id": "fashion",
     "description": "Chicago colorway, worn twice. 100% authentic, receipt available.",
     "location": "Bugis, Singapore", "condition": "Like New"},
    {"title": "Canon EOS R50 Mirrorless Camera Kit", "price": 750, "category_id": "electronics",
     "description": "Includes 18-45mm kit lens, 2 batteries, 64GB card. Perfect for YouTube/vlogging.",
     "location": "Buona Vista, Singapore", "condition": "Excellent"},
    {"title": "Samsung 65 inch QLED 4K Smart TV", "price": 650, "category_id": "electronics",
     "description": "2022 model, excellent picture quality. Selling as upgrading to bigger screen.",
     "location": "Serangoon, Singapore", "condition": "Good"},
    {"title": "Dyson V15 Detect Cordless Vacuum", "price": 450, "category_id": "other",
     "description": "Purchased 10 months ago, all attachments included. Battery holds full charge.",
     "location": "Pasir Ris, Singapore", "condition": "Like New"},
    {"title": "Loewe Camera Bag 25L Dark Navy", "price": 120, "category_id": "fashion",
     "description": "Barely used, fits 15 inch laptop. Perfect for photographers or travelers.",
     "location": "Dhoby Ghaut, Singapore", "condition": "Like New"},
    {"title": "Specialized Allez Sport Road Bike", "price": 680, "category_id": "sports",
     "description": "2021 model, size 54cm, Shimano Claris groupset. Stored indoors, no rust.",
     "location": "Bedok, Singapore", "condition": "Good"},
]


def seed():
    Base.metadata.create_all(bind=sync_engine)
    db = SyncSessionLocal()

    try:
        # Create users
        users = []
        for u in DEMO_USERS:
            existing = db.query(User).filter(User.email == u["email"]).first()
            if existing:
                users.append(existing)
                continue
            user = User(
                id=str(uuid.uuid4()),
                email=u["email"],
                username=u["username"],
                full_name=u["full_name"],
                hashed_password=pwd_context.hash("demo1234"),
                trust_score=random.uniform(60, 90),
                total_sales=random.randint(0, 30),
                is_verified=random.choice([True, False]),
            )
            db.add(user)
            users.append(user)
        db.commit()
        print(f"✅ {len(users)} users ready")

        # Create listings
        count = 0
        now = datetime.now(timezone.utc)
        for i, l in enumerate(DEMO_LISTINGS):
            seller = users[i % len(users)]
            hours_left = random.uniform(2, 70)
            market_avg = l["price"] * random.uniform(0.85, 1.2)

            listing = Listing(
                id=str(uuid.uuid4()),
                seller_id=seller.id,
                title=l["title"],
                description=l["description"],
                price=l["price"],
                category_id=l.get("category_id"),
                location=l.get("location"),
                condition=l.get("condition"),
                images=[f"https://picsum.photos/seed/{i+1}/600/450"],
                tags=[l["category_id"], l["condition"].replace(" ", "")],
                status=ListingStatus.ACTIVE,
                duration_hours=48,
                expires_at=now + timedelta(hours=hours_left),
                total_views=random.randint(10, 250),
                views_last_hour=random.randint(0, 15),
                saves_count=random.randint(0, 25),
                messages_count=random.randint(0, 12),
                active_buyers=random.randint(0, 4),
                is_boosted=random.choice([False, False, False, True]),
                market_avg_price=market_avg,
                price_percentile=random.randint(10, 90),
                rank_score=random.uniform(40, 90),
            )
            db.add(listing)
            count += 1

        db.commit()
        print(f"✅ {count} listings seeded")
        print("\n🔑 Demo login credentials:")
        print("   Email: alice@demo.com | Password: demo1234")
        print("   Email: bob@demo.com   | Password: demo1234")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
