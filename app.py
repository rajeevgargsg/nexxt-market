"""
NexxtMarket — Streamlit Edition
Runs on Streamlit Cloud (free). No Docker, no Postgres, no Redis needed.
Uses SQLite for storage + Groq free API for AI features.
"""
import streamlit as st
import sqlite3
import json
import asyncio
import os
import httpx
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NexxtMarket",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inline CSS (dark theme) ────────────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background: #0a0a0a; }
  [data-testid="stSidebar"] { background: #111; border-right: 1px solid #222; }
  h1, h2, h3 { color: #f97316; font-family: 'Georgia', serif; }
  .metric-card {
    background: #161616; border: 1px solid #2a2a2a; border-radius: 12px;
    padding: 16px; margin: 6px 0;
  }
  .signal-box {
    background: #0d1117; border-left: 3px solid #f97316;
    border-radius: 8px; padding: 12px 16px; margin: 8px 0;
  }
  .listing-card {
    background: #141414; border: 1px solid #252525; border-radius: 12px;
    padding: 16px; margin: 8px 0;
  }
  .badge-deal   { background:#16a34a22; color:#4ade80; padding:2px 10px; border-radius:20px; font-size:12px; }
  .badge-fair   { background:#1d4ed822; color:#60a5fa; padding:2px 10px; border-radius:20px; font-size:12px; }
  .badge-high   { background:#dc262622; color:#f87171; padding:2px 10px; border-radius:20px; font-size:12px; }
  .stButton > button { background:#f97316; color:#000; font-weight:700; border-radius:10px; border:none; }
  .stButton > button:hover { background:#fb923c; }
</style>
""", unsafe_allow_html=True)

# ── SQLite Setup ───────────────────────────────────────────────────────────────
DB_PATH = "nexxtmarket.db"

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS listings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        category TEXT DEFAULT 'Other',
        condition TEXT DEFAULT 'good',
        location TEXT DEFAULT 'Singapore',
        status TEXT DEFAULT 'active',
        views INTEGER DEFAULT 0,
        saves INTEGER DEFAULT 0,
        messages_count INTEGER DEFAULT 0,
        active_buyers INTEGER DEFAULT 0,
        market_avg_price REAL,
        ai_deal_score INTEGER DEFAULT 0,
        ai_title TEXT,
        ai_description TEXT,
        rank_score REAL DEFAULT 80.0,
        expires_at TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS saved_listings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        listing_id INTEGER,
        session_id TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    );
    """)
    # Seed demo data if empty
    count = conn.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
    if count == 0:
        _seed_demo(conn)
    conn.commit()
    conn.close()

def _seed_demo(conn):
    demos = [
        ("Sony WH-1000XM4 Headphones", "Excellent noise cancelling, barely used. Original box included.", 180, "Electronics", "excellent", 210, 91),
        ("Trek FX3 City Bike 2022", "Perfect urban commuter bike. Serviced 3 months ago.", 420, "Sports", "good", 480, 78),
        ("IKEA KALLAX Shelf Unit 4x2", "White, good condition. Minor scuff on side. Self-collect only.", 65, "Furniture", "good", 90, 62),
        ("MacBook Pro M1 2021 16GB", "Space grey, 512GB SSD. Light scratches on bottom panel.", 1050, "Electronics", "good", 1200, 85),
        ("Nintendo Switch OLED + 3 Games", "Mint condition, 1 month old. Animal Crossing, Mario Kart, Zelda.", 320, "Gaming", "excellent", 370, 88),
        ("Dyson V11 Cordless Vacuum", "2 years old, filter cleaned. All attachments included.", 280, "Appliances", "good", 340, 76),
        ("Herman Miller Aeron Chair Size B", "Grey, some wear on armrests. Bought 2020. Still very comfortable.", 650, "Furniture", "good", 800, 82),
        ("iPhone 14 Pro 256GB Deep Purple", "Excellent condition, no scratches. Comes with original charger.", 780, "Electronics", "excellent", 850, 90),
    ]
    for title, desc, price, cat, cond, mkt, score in demos:
        exp = (datetime.now(timezone.utc) + timedelta(hours=24 + len(title) % 48)).isoformat()
        conn.execute(
            "INSERT INTO listings (title, description, price, category, condition, market_avg_price, ai_deal_score, rank_score, expires_at, views, saves, messages_count, active_buyers) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (title, desc, price, cat, cond, mkt, score, 75 + score % 20, exp,
             10 + score * 2, score // 10, score // 15, score // 25)
        )

init_db()


# ── Groq AI Helper ─────────────────────────────────────────────────────────────

def groq_chat(system: str, user: str, max_tokens: int = 200) -> str:
    api_key = os.environ.get("GROQ_API_KEY", "") or (st.secrets.get("GROQ_API_KEY", "") if hasattr(st, "secrets") else "")
    if not api_key:
        return None
    try:
        resp = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                "max_tokens": max_tokens,
                "temperature": 0.7,
            },
            timeout=10,
        )
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return None


# ── Signal Generators (sync, no Redis) ────────────────────────────────────────

def price_signal(listing):
    price = listing["price"]
    avg = listing["market_avg_price"] or price
    diff = ((price - avg) / avg * 100) if avg else 0
    if diff <= -15:   label, emoji = "Excellent Deal 🟢", "🟢"
    elif diff <= -5:  label, emoji = "Good Deal 🟡", "🟡"
    elif diff <= 5:   label, emoji = "Fair Price ⚪", "⚪"
    elif diff <= 15:  label, emoji = "Slightly High 🟠", "🟠"
    else:             label, emoji = "Overpriced 🔴", "🔴"
    return {"label": label, "diff": round(diff, 1), "avg": avg}

def time_signal(listing):
    try:
        exp = datetime.fromisoformat(listing["expires_at"].replace("Z", "+00:00"))
        hours = max(0, (exp - datetime.now(timezone.utc)).total_seconds() / 3600)
    except Exception:
        hours = 24
    if hours <= 3:   urgency = "🚨 CRITICAL"
    elif hours <= 12: urgency = "🔥 HIGH"
    elif hours <= 24: urgency = "⏳ MEDIUM"
    else:            urgency = "✅ LOW"
    return {"hours": round(hours, 1), "urgency": urgency}

def competition_signal(listing):
    buyers = listing["active_buyers"] or 0
    msgs = listing["messages_count"] or 0
    if buyers >= 3:  level, score = "🔥 High Competition", 90
    elif buyers == 2: level, score = "⚡ Active Bidding", 75
    elif buyers == 1: level, score = "👀 1 Interested", 50
    elif msgs >= 1:  level, score = "💬 Some Interest", 35
    else:            level, score = "✅ First Mover", 10
    return {"level": level, "fomo": score, "buyers": buyers}


# ── Navigation ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚡ NexxtMarket")
    st.markdown("*AI-Powered Classified Marketplace*")
    st.divider()
    page = st.radio("Navigate", ["🏠 Browse Listings", "➕ Sell Something", "📊 AI Signal Demo", "📋 My Saved"])
    st.divider()
    st.markdown("**Free stack used:**")
    st.markdown("- Groq Llama-3.1 (LLM)\n- Streamlit Cloud\n- SQLite\n- Python")
    has_key = bool(os.environ.get("GROQ_API_KEY"))
    if has_key:
        st.success("✅ Groq AI active")
    else:
        st.warning("⚠️ Add GROQ_API_KEY in Streamlit secrets for AI features")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Browse Listings
# ═══════════════════════════════════════════════════════════════════════════════

if page == "🏠 Browse Listings":
    st.title("⚡ Live Marketplace")

    # Filters
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        category = st.selectbox("Category", ["All", "Electronics", "Furniture", "Sports", "Gaming", "Appliances"])
    with col2:
        sort_by = st.selectbox("Sort", ["Rank Score", "Price: Low→High", "Price: High→Low", "Newest"])
    with col3:
        max_price = st.number_input("Max Price ($)", min_value=0, value=5000, step=50)

    conn = get_db()
    query = "SELECT * FROM listings WHERE status='active' AND price <= ?"
    params = [max_price]
    if category != "All":
        query += " AND category = ?"
        params.append(category)

    sort_map = {
        "Rank Score": "rank_score DESC",
        "Price: Low→High": "price ASC",
        "Price: High→Low": "price DESC",
        "Newest": "created_at DESC",
    }
    query += f" ORDER BY {sort_map[sort_by]}"
    listings = conn.execute(query, params).fetchall()
    conn.close()

    st.markdown(f"**{len(listings)} active listings**")
    st.divider()

    if not listings:
        st.info("No listings found. Adjust your filters or add one!")
    else:
        for listing in listings:
            l = dict(listing)
            ps = price_signal(l)
            ts = time_signal(l)
            cs = competition_signal(l)

            with st.container():
                st.markdown(f'<div class="listing-card">', unsafe_allow_html=True)
                c1, c2, c3 = st.columns([4, 2, 2])

                with c1:
                    st.markdown(f"### {l['title']}")
                    st.markdown(f"*{l['description'][:100]}...*" if len(l.get('description','')) > 100 else f"*{l.get('description','')}*")
                    st.markdown(f"📍 {l['location']} &nbsp;|&nbsp; 🏷️ {l['category']} &nbsp;|&nbsp; ⭐ {l['condition']}")

                with c2:
                    st.markdown(f"### ${l['price']:,.0f}")
                    st.markdown(f"*mkt avg: ${ps['avg']:,.0f}*")
                    diff_str = f"+{ps['diff']}%" if ps['diff'] > 0 else f"{ps['diff']}%"
                    st.markdown(f"**{ps['label']}** ({diff_str})")

                with c3:
                    st.markdown(f"⏱️ **{ts['urgency']}**")
                    st.markdown(f"⏰ {ts['hours']}h left")
                    st.markdown(f"👥 {cs['level']}")
                    st.progress(cs['fomo'] / 100, text=f"FOMO: {cs['fomo']}/100")

                st.markdown(
                    f"👁️ {l['views']} views &nbsp; 💾 {l['saves']} saves &nbsp; 💬 {l['messages_count']} msgs &nbsp; "
                    f"📈 Rank: {l['rank_score']:.0f}/100",
                    unsafe_allow_html=False,
                )
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — Sell Something
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "➕ Sell Something":
    st.title("➕ Create a Listing")

    if "sell_step" not in st.session_state:
        st.session_state.sell_step = 1
        st.session_state.listing_data = {}
        st.session_state.ai_result = None

    step = st.session_state.sell_step

    # Step indicator
    cols = st.columns(3)
    for i, label in enumerate(["1. Details", "2. AI Optimize", "3. Publish"]):
        with cols[i]:
            if i + 1 == step:
                st.markdown(f"**🟠 {label}**")
            elif i + 1 < step:
                st.markdown(f"~~✅ {label}~~")
            else:
                st.markdown(f"⬜ {label}")
    st.divider()

    # ── Step 1: Basic Details
    if step == 1:
        with st.form("listing_form"):
            title = st.text_input("Title *", placeholder="e.g. Sony WH-1000XM4 Headphones")
            description = st.text_area("Description *", placeholder="Describe condition, what's included, reason for selling...", height=120)
            col1, col2 = st.columns(2)
            with col1:
                price = st.number_input("Price (SGD) *", min_value=1.0, value=100.0, step=5.0)
                category = st.selectbox("Category", ["Electronics", "Furniture", "Sports", "Gaming", "Appliances", "Fashion", "Books", "Other"])
            with col2:
                condition = st.selectbox("Condition", ["excellent", "good", "fair", "poor"])
                duration = st.selectbox("Listing Duration", [24, 48, 72], format_func=lambda x: f"{x} hours")
            location = st.text_input("Location", value="Singapore")
            submitted = st.form_submit_button("Next → AI Optimize")

        if submitted:
            if not title or not description:
                st.error("Title and description are required.")
            else:
                st.session_state.listing_data = {
                    "title": title, "description": description, "price": price,
                    "category": category, "condition": condition,
                    "location": location, "duration": duration,
                }
                st.session_state.sell_step = 2
                st.rerun()

    # ── Step 2: AI Optimization
    elif step == 2:
        data = st.session_state.listing_data
        st.subheader("🤖 AI Optimization")

        if st.session_state.ai_result is None:
            with st.spinner("Asking AI to optimize your listing..."):
                prompt = f"""
Listing title: {data['title']}
Description: {data['description']}
Price: ${data['price']}
Category: {data['category']}
Condition: {data['condition']}

Return JSON only (no extra text):
{{
  "optimized_title": "...",
  "optimized_description": "...",
  "suggested_price": 0,
  "deal_score": 0,
  "key_improvements": ["...", "..."],
  "suggested_tags": ["...", "..."]
}}
"""
                raw = groq_chat("You are a marketplace listing optimizer. Return ONLY valid JSON.", prompt, 400)
                if raw:
                    try:
                        import re
                        json_str = re.search(r'\{.*\}', raw, re.DOTALL)
                        result = json.loads(json_str.group()) if json_str else None
                    except Exception:
                        result = None
                else:
                    result = None

                # Fallback if no API key or parse error
                if not result:
                    result = {
                        "optimized_title": data['title'].title(),
                        "optimized_description": data['description'],
                        "suggested_price": data['price'],
                        "deal_score": 70,
                        "key_improvements": ["Add more photos", "Mention original price", "State reason for selling"],
                        "suggested_tags": [data['category'].lower(), data['condition']],
                    }
                st.session_state.ai_result = result

        result = st.session_state.ai_result
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Original**")
            st.text(data['title'])
            st.text(f"${data['price']}")
            st.text_area("", data['description'], height=120, disabled=True, key="orig_desc")

        with col2:
            st.markdown("**✨ AI Optimized**")
            st.success(result.get("optimized_title", data['title']))
            suggested_price = result.get("suggested_price", data['price'])
            if suggested_price != data['price']:
                st.info(f"💡 Suggested price: ${suggested_price}")
            st.text_area("", result.get("optimized_description", data['description']), height=120, disabled=True, key="ai_desc")

        score = result.get("deal_score", 70)
        st.markdown(f"**Deal Score: {score}/100**")
        st.progress(score / 100)

        improvements = result.get("key_improvements", [])
        if improvements:
            st.markdown("**Improvements:**")
            for tip in improvements:
                st.markdown(f"- {tip}")

        use_ai = st.toggle("Use AI-optimized version", value=True)
        st.session_state.listing_data["use_ai"] = use_ai
        st.session_state.listing_data["ai_result"] = result

        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back"):
                st.session_state.sell_step = 1
                st.rerun()
        with col2:
            if st.button("Next → Preview & Publish"):
                st.session_state.sell_step = 3
                st.rerun()

    # ── Step 3: Publish
    elif step == 3:
        data = st.session_state.listing_data
        result = data.get("ai_result", {})
        use_ai = data.get("use_ai", False)

        st.subheader("📋 Preview & Publish")

        final_title = result.get("optimized_title", data['title']) if use_ai else data['title']
        final_desc = result.get("optimized_description", data['description']) if use_ai else data['description']
        final_price = data['price']

        st.markdown(f"### {final_title}")
        st.markdown(f"**${final_price:,.0f}** &nbsp;|&nbsp; {data['category']} &nbsp;|&nbsp; {data['condition']} &nbsp;|&nbsp; 📍 {data['location']}")
        st.markdown(final_desc)
        st.markdown(f"⏰ Expires in: **{data['duration']} hours**")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back"):
                st.session_state.sell_step = 2
                st.rerun()
        with col2:
            if st.button("🚀 Publish Listing", type="primary"):
                conn = get_db()
                exp = (datetime.now(timezone.utc) + timedelta(hours=data['duration'])).isoformat()
                # Get market avg for category
                avg_row = conn.execute(
                    "SELECT AVG(price) FROM listings WHERE category=? AND status='active'",
                    (data['category'],)
                ).fetchone()
                market_avg = avg_row[0] if avg_row[0] else final_price

                conn.execute(
                    """INSERT INTO listings
                       (title, description, price, category, condition, location,
                        market_avg_price, ai_deal_score, ai_title, ai_description,
                        rank_score, expires_at)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (final_title, final_desc, final_price, data['category'],
                     data['condition'], data['location'], market_avg,
                     result.get("deal_score", 70), result.get("optimized_title"),
                     result.get("optimized_description"), 85.0, exp)
                )
                conn.commit()
                conn.close()

                st.success("✅ Listing published!")
                st.balloons()
                st.session_state.sell_step = 1
                st.session_state.ai_result = None
                st.session_state.listing_data = {}


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — AI Signal Demo
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "📊 AI Signal Demo":
    st.title("📊 Live AI Signals — Demo")
    st.markdown("Paste any listing details below and see all 7 engagement signals fire in real time.")

    with st.form("signal_form"):
        col1, col2 = st.columns(2)
        with col1:
            demo_title = st.text_input("Item title", value="Sony WH-1000XM4 Headphones")
            demo_price = st.number_input("Your price ($)", value=180.0)
            demo_market = st.number_input("Market average ($)", value=210.0)
        with col2:
            demo_views = st.number_input("Views last hour", value=15, step=1)
            demo_buyers = st.number_input("Active buyers", value=3, step=1)
            demo_hours = st.slider("Hours until expiry", 1, 72, 20)
        run = st.form_submit_button("⚡ Generate All Signals")

    if run:
        listing = {
            "title": demo_title, "price": demo_price,
            "market_avg_price": demo_market,
            "views_last_hour": demo_views, "saves": 8, "saves_count": 8,
            "messages_count": demo_buyers, "active_buyers": demo_buyers,
            "description": "Demo listing for signal generation", "images": [],
            "expires_at": (datetime.now(timezone.utc) + timedelta(hours=demo_hours)).isoformat(),
            "is_boosted": False,
        }

        ps = price_signal(listing)
        ts = time_signal(listing)
        cs = competition_signal(listing)

        tab1, tab2, tab3, tab4 = st.tabs(["💰 Price", "⏱ Time", "👥 Social", "🤖 AI Insight"])

        with tab1:
            st.markdown("### 💰 Price Intelligence")
            diff = ps['diff']
            if diff <= -5:
                st.success(f"**{ps['label']}** — {abs(diff):.1f}% below market avg (${ps['avg']:,.0f})")
            elif diff >= 10:
                st.error(f"**{ps['label']}** — {diff:.1f}% above market avg")
            else:
                st.info(f"**{ps['label']}** — within 5% of market avg")

        with tab2:
            st.markdown("### ⏱️ Time Pressure")
            hours = ts['hours']
            if hours <= 3:
                st.error(f"**{ts['urgency']}** — Only {hours:.0f}h left!")
            elif hours <= 12:
                st.warning(f"**{ts['urgency']}** — {hours:.0f}h remaining")
            else:
                st.success(f"**{ts['urgency']}** — {hours:.0f}h remaining")
            st.progress(min(1.0, (72 - hours) / 72))

        with tab3:
            st.markdown("### 👥 Competition & Social Proof")
            st.markdown(f"**{cs['level']}**")
            st.markdown(f"FOMO Score: **{cs['fomo']}/100**")
            st.progress(cs['fomo'] / 100)
            col1, col2, col3 = st.columns(3)
            col1.metric("Views/hr", demo_views)
            col2.metric("Active Buyers", demo_buyers)
            col3.metric("Messages", demo_buyers)

        with tab4:
            st.markdown("### 🤖 AI Content Insight (Groq)")
            with st.spinner("Generating AI insight..."):
                insight = groq_chat(
                    "You are a marketplace analyst. Write ONE sharp insight about this listing (max 2 sentences). Be specific.",
                    f"Item: {demo_title}, Price: ${demo_price}, Market avg: ${demo_market}, {demo_buyers} active buyers, {demo_hours}h left"
                )
            if insight:
                st.info(insight)
            else:
                st.warning("Add your GROQ_API_KEY in Streamlit secrets to enable AI insights. (Settings → Secrets → add GROQ_API_KEY)")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — Saved Listings
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "📋 My Saved":
    st.title("📋 Saved Listings")

    if "session_id" not in st.session_state:
        import uuid
        st.session_state.session_id = str(uuid.uuid4())

    conn = get_db()
    saved = conn.execute("""
        SELECT l.* FROM listings l
        JOIN saved_listings sl ON l.id = sl.listing_id
        WHERE sl.session_id = ?
        ORDER BY sl.created_at DESC
    """, (st.session_state.session_id,)).fetchall()
    conn.close()

    if not saved:
        st.info("You haven't saved any listings yet. Browse the marketplace and click Save on listings you like.")
    else:
        for l in saved:
            l = dict(l)
            ps = price_signal(l)
            with st.container():
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(f"**{l['title']}** — ${l['price']:,.0f}")
                    st.markdown(f"{l['category']} · {ps['label']}")
                with c2:
                    ts = time_signal(l)
                    st.markdown(f"⏰ {ts['hours']}h left")
            st.divider()
