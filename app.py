"""
NexxtMarket v4 — News ticker · Phone/PIN login · QR code · Save listings
"""
import streamlit as st
import sqlite3, json, os, re, uuid, httpx, qrcode, io, hashlib, random, time
from datetime import datetime, timezone, timedelta
from PIL import Image

st.set_page_config(page_title="NexxtMarket", page_icon="⚡", layout="wide",
                   initial_sidebar_state="collapsed")

# ══════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');
*,html,body,[class*="css"]{font-family:'Space Grotesk',sans-serif!important;box-sizing:border-box}
[data-testid="stAppViewContainer"]{background:#060609!important}
[data-testid="stSidebar"]{display:none!important}
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="collapsedControl"]{display:none!important;visibility:hidden!important}
.block-container{padding:0 1.2rem 3rem!important;max-width:880px!important;margin:0 auto!important}
h1{color:#fff!important;font-weight:800!important;letter-spacing:-1.5px!important;margin:0 0 4px!important}
h2,h3{color:#fff!important;font-weight:700!important}
p,label,span{color:#a0a0b8!important}
/* inputs */
input,textarea,[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea{background:#111118!important;border:1.5px solid #252535!important;color:#fff!important;border-radius:10px!important;font-family:'Space Grotesk',sans-serif!important;font-size:14px!important}
input:focus,textarea:focus{border-color:#f97316!important;box-shadow:0 0 0 3px #f9731620!important;outline:none!important}
.stTextInput label,.stTextArea label,.stNumberInput label,.stSelectbox label,.stSlider label{color:#707088!important;font-size:11px!important;font-weight:600!important;text-transform:uppercase!important;letter-spacing:.5px!important}
/* number input */
[data-testid="stNumberInput"]>div,[data-testid="stNumberInput"]>div>div{background:#111118!important;border:1.5px solid #252535!important;border-radius:10px!important;overflow:hidden!important}
[data-testid="stNumberInput"] input{background:#111118!important;color:#fff!important;border:none!important;font-family:'JetBrains Mono',monospace!important;font-weight:600!important;font-size:16px!important}
[data-testid="stNumberInput"] button{background:#1e1e30!important;color:#f97316!important;border:none!important;font-size:18px!important;font-weight:700!important;min-width:44px!important}
[data-testid="stNumberInput"] button:hover{background:#f97316!important;color:#000!important}
[data-testid="stNumberInput"] button:first-child{border-right:1px solid #252535!important}
/* select */
[data-testid="stSelectbox"]>div>div{background:#111118!important;border:1.5px solid #252535!important;color:#fff!important;border-radius:10px!important}
[data-baseweb="popover"]>div{background:#111118!important;border:1px solid #252535!important;border-radius:10px!important}
[data-baseweb="option"]{background:#111118!important;color:#c0c0d8!important}
[data-baseweb="option"]:hover{background:#1e1e30!important}
[aria-selected="true"][data-baseweb="option"]{background:#f9731620!important;color:#f97316!important}
/* button */
.stButton>button{background:linear-gradient(135deg,#f97316,#dc5a0a)!important;color:#000!important;font-family:'Space Grotesk',sans-serif!important;font-weight:700!important;font-size:14px!important;border:none!important;border-radius:12px!important;padding:.65rem 1.6rem!important;width:100%!important;transition:all .2s!important;box-shadow:0 4px 20px #f9731630!important}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 28px #f9731650!important}
/* form */
[data-testid="stForm"]{background:#0d0d15!important;border:1px solid #1e1e30!important;border-radius:16px!important;padding:24px!important}
/* tabs */
[data-baseweb="tab-list"]{background:#0d0d15!important;border-radius:12px!important;padding:5px!important;border:1px solid #1e1e30!important;gap:4px!important}
[data-baseweb="tab"]{background:transparent!important;color:#505068!important;border-radius:8px!important;font-weight:600!important}
[aria-selected="true"][data-baseweb="tab"]{background:#f97316!important;color:#000!important}
[data-baseweb="tab-highlight"],[data-baseweb="tab-border"]{display:none!important}
hr{border-color:#1a1a28!important;margin:16px 0!important}
.stSpinner>div{border-top-color:#f97316!important}
::-webkit-scrollbar{width:4px;height:4px}::-webkit-scrollbar-track{background:#060609}::-webkit-scrollbar-thumb{background:#252535;border-radius:99px}
[data-testid="stToggle"] label{color:#c0c0d8!important}
/* progress */
.stProgress>div>div{background:#1a1a28!important;border-radius:99px!important;height:6px!important}
.stProgress>div>div>div{background:linear-gradient(90deg,#f97316,#fbbf24)!important;border-radius:99px!important}

/* ── Ticker ── */
.ticker-wrap{background:#0d0d18;border-bottom:1px solid #1e1e2e;overflow:hidden;padding:0;height:36px;display:flex;align-items:center}
.ticker-label{background:#f97316;color:#000;font-size:11px;font-weight:800;padding:0 14px;height:36px;display:flex;align-items:center;white-space:nowrap;flex-shrink:0;letter-spacing:.5px;text-transform:uppercase}
.ticker-track{display:flex;animation:ticker-scroll 60s linear infinite;white-space:nowrap}
.ticker-track:hover{animation-play-state:paused}
.ticker-item{font-size:12px;color:#8080a0;padding:0 32px;display:flex;align-items:center;gap:8px;white-space:nowrap}
.ticker-item b{color:#f97316}
.ticker-dot{color:#252535}
@keyframes ticker-scroll{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}

/* ── Top Nav ── */
.topnav{position:sticky;top:0;z-index:9999;background:rgba(6,6,9,0.97);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border-bottom:1px solid #1a1a28;padding:0 20px;display:flex;align-items:center;justify-content:space-between;height:54px;margin-bottom:0;width:100%}
.topnav-brand{display:flex;align-items:center;gap:8px}
.topnav-brand-text{font-size:18px;font-weight:800;color:#fff;letter-spacing:-.5px;white-space:nowrap}
.topnav-links{display:flex;align-items:center;gap:3px}
.navbtn{display:flex;align-items:center;gap:6px;padding:7px 13px;border-radius:10px;font-size:13px;font-weight:600;color:#505068;cursor:pointer;transition:all .15s;border:1px solid transparent;background:transparent;white-space:nowrap;text-decoration:none!important}
.navbtn:hover{background:#1a1a28;color:#fff}
.navbtn.active{background:#f9731618;color:#f97316;border-color:#f9731630}
.navbtn-login{background:#1e1e30;color:#c0c0d8;border:1px solid #2a2a42}
.navbtn-login:hover{background:#f97316;color:#000;border-color:#f97316}
.navbtn-login.logged{background:#16a34a20;color:#4ade80;border-color:#16a34a30}
@media(max-width:640px){.topnav{padding:0 10px;height:50px}.navbtn{padding:7px 9px;font-size:12px}.navbtn-label{display:none}.topnav-brand-text{font-size:15px}}

/* ── Cards ── */
.nm-card{background:linear-gradient(145deg,#0d0d18,#10101e);border:1px solid #1e1e32;border-radius:16px;padding:18px 20px;margin-bottom:10px;position:relative;overflow:hidden;transition:border-color .2s,box-shadow .2s}
.nm-card:hover{border-color:#2a2a45;box-shadow:0 8px 32px #00000040}
.nm-card-top{position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,#f97316,#fbbf24 40%,transparent)}
.nm-stats{background:#0d0d18;border:1px solid #1a1a28;border-radius:12px;padding:12px 18px;display:flex;gap:16px;align-items:center;margin-bottom:16px;flex-wrap:wrap}
.nm-stat-val{font-size:20px;font-weight:800;color:#f97316;font-family:'JetBrains Mono',monospace}
.nm-stat-lbl{font-size:11px;color:#404050;margin-top:1px}
.nm-sep{width:1px;height:30px;background:#1a1a28;flex-shrink:0}
.nm-badge{font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;display:inline-block}
.nm-tag{font-size:11px;color:#505070;background:#14141e;padding:3px 10px;border-radius:20px;border:1px solid #1e1e2e;display:inline-block;margin:2px}
.nm-price{font-family:'JetBrains Mono',monospace;font-weight:800;color:#fff;line-height:1}
.nm-section-title{font-size:11px;color:#404055;text-transform:uppercase;letter-spacing:1px;font-weight:600;margin:20px 0 10px}
.nm-empty{text-align:center;padding:60px 20px;color:#303045}
.save-btn{display:inline-flex;align-items:center;gap:5px;font-size:11px;font-weight:600;color:#505070;background:#14141e;border:1px solid #1e1e2e;border-radius:20px;padding:4px 12px;cursor:pointer;transition:all .15s}
.save-btn:hover{border-color:#f97316;color:#f97316}
.save-btn.saved{background:#f9731618;border-color:#f9731640;color:#f97316}
/* modal-style login box */
.login-box{background:#0d0d18;border:1px solid #1e1e30;border-radius:20px;padding:28px 28px 24px;max-width:400px;margin:40px auto}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# DATABASE
# ══════════════════════════════════════════════════════════════════
DB = "nexxtmarket.db"

def get_db():
    c = sqlite3.connect(DB, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = get_db()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT UNIQUE NOT NULL,
        name TEXT,
        pin_hash TEXT NOT NULL,
        created_at TEXT DEFAULT(datetime('now')));
    CREATE TABLE IF NOT EXISTS listings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT NOT NULL,description TEXT,price REAL NOT NULL,
        category TEXT DEFAULT 'Other',condition TEXT DEFAULT 'good',
        location TEXT DEFAULT 'Singapore',status TEXT DEFAULT 'active',
        views INTEGER DEFAULT 0,saves INTEGER DEFAULT 0,
        messages_count INTEGER DEFAULT 0,active_buyers INTEGER DEFAULT 0,
        market_avg_price REAL,ai_deal_score INTEGER DEFAULT 0,
        ai_title TEXT,ai_description TEXT,rank_score REAL DEFAULT 80.0,
        expires_at TEXT,created_at TEXT DEFAULT(datetime('now')));
    CREATE TABLE IF NOT EXISTS saved_listings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        listing_id INTEGER,user_id INTEGER,session_id TEXT,
        created_at TEXT DEFAULT(datetime('now')),
        UNIQUE(listing_id, session_id));
    """)
    if c.execute("SELECT COUNT(*) FROM listings").fetchone()[0] == 0:
        seeds = [
            ("Sony WH-1000XM4 Headphones","Excellent noise cancelling, barely used. Original box included.",180,"Electronics","excellent",210,91,8),
            ("Trek FX3 City Bike 2022","Perfect urban commuter. Fully serviced 3 months ago.",420,"Sports","good",480,78,5),
            ("IKEA KALLAX Shelf 4×2","White, minor scuff on side. Self-collect only.",65,"Furniture","good",90,62,3),
            ("MacBook Pro M1 16GB 512GB","Space grey, light scratches on bottom. Charger included.",1050,"Electronics","good",1200,85,6),
            ("Nintendo Switch OLED + 3 Games","Mint condition, 1 month old. AC, Mario Kart, Zelda.",320,"Gaming","excellent",370,88,7),
            ("Dyson V11 Cordless Vacuum","2 years old, filter cleaned. All attachments included.",280,"Appliances","good",340,76,4),
            ("Herman Miller Aeron Chair B","Grey, some armrest wear. Very comfortable. 2020.",650,"Furniture","good",800,82,5),
            ("iPhone 14 Pro 256GB Deep Purple","No scratches. Original charger and box included.",780,"Electronics","excellent",850,90,9),
        ]
        for t,d,p,cat,cond,mkt,score,buyers in seeds:
            exp=(datetime.now(timezone.utc)+timedelta(hours=24+len(t)%48)).isoformat()
            c.execute("INSERT INTO listings(title,description,price,category,condition,market_avg_price,ai_deal_score,rank_score,expires_at,views,saves,messages_count,active_buyers)VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (t,d,p,cat,cond,mkt,score,75+score%20,exp,score*2,score//10,score//15,buyers))
    c.commit(); c.close()

init_db()

def hash_pin(pin): return hashlib.sha256(pin.encode()).hexdigest()

def register_user(phone, name, pin):
    c = get_db()
    try:
        c.execute("INSERT INTO users(phone,name,pin_hash)VALUES(?,?,?)",(phone,name,hash_pin(pin)))
        c.commit()
        return c.execute("SELECT * FROM users WHERE phone=?",(phone,)).fetchone()
    except sqlite3.IntegrityError: return None
    finally: c.close()

def login_user(phone, pin):
    c = get_db()
    u = c.execute("SELECT * FROM users WHERE phone=? AND pin_hash=?",(phone,hash_pin(pin))).fetchone()
    c.close()
    return dict(u) if u else None

def get_saved_ids(session_id):
    c = get_db()
    rows = c.execute("SELECT listing_id FROM saved_listings WHERE session_id=?",(session_id,)).fetchall()
    c.close()
    return {r[0] for r in rows}

def toggle_save(listing_id, session_id):
    c = get_db()
    existing = c.execute("SELECT id FROM saved_listings WHERE listing_id=? AND session_id=?",(listing_id,session_id)).fetchone()
    if existing:
        c.execute("DELETE FROM saved_listings WHERE listing_id=? AND session_id=?",(listing_id,session_id))
        saved = False
    else:
        try:
            c.execute("INSERT INTO saved_listings(listing_id,session_id)VALUES(?,?)",(listing_id,session_id))
            saved = True
        except: saved = True
    c.commit(); c.close()
    return saved


# ══════════════════════════════════════════════════════════════════
# AI
# ══════════════════════════════════════════════════════════════════
def groq_chat(system, user, max_tokens=200):
    key = os.environ.get("GROQ_API_KEY","")
    if not key: return None
    try:
        r = httpx.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
            json={"model":"llama-3.1-8b-instant",
                  "messages":[{"role":"system","content":system},{"role":"user","content":user}],
                  "max_tokens":max_tokens,"temperature":0.7},timeout=10)
        return r.json()["choices"][0]["message"]["content"].strip()
    except: return None


# ══════════════════════════════════════════════════════════════════
# TICKER DATA — rotating facts + AI insights
# ══════════════════════════════════════════════════════════════════
TICKER_FACTS = [
    ("🇸🇬 Market", "Singapore's secondhand market grew <b>34%</b> in 2024 — resellers made avg $8,400/yr"),
    ("📱 Hot Right Now", "iPhone resale values dropped <b>12%</b> this quarter — great time to buy refurbished"),
    ("🚲 Trending", "E-bikes now outsell regular bikes on classifieds — prices up <b>22%</b> YoY"),
    ("💡 Seller Tip", "Listings posted between <b>6–9PM</b> get 3x more views than morning posts"),
    ("🔥 Deal Alert", "MacBook M1 models selling <b>40% below</b> retail — market flooded with upgrades"),
    ("⚡ Speed", "Best-priced electronics sell in <b>under 4 hours</b> on average — price is everything"),
    ("🪑 Furniture", "IKEA resale holds <b>60% value</b> — highest retention of any furniture brand"),
    ("📊 Insight", "Listings with 3+ photos sell <b>2.8× faster</b> than single-photo posts"),
    ("🎮 Gaming", "Nintendo Switch demand spiked <b>45%</b> after new title releases — sell now"),
    ("💰 Price IQ", "Items priced <b>15% below market avg</b> sell within 2 hours, 91% of the time"),
    ("🌍 Trend", "Gen Z drives <b>67%</b> of secondhand electronics purchases globally in 2025"),
    ("⌚ Watches", "Luxury watch resale now outperforms stocks — avg <b>8.2% annual gain</b>"),
    ("🛋️ WFH", "Standing desk resale up <b>180%</b> since 2020 — remote work drives demand"),
    ("🤖 AI Fact", "AI-optimized listings get <b>53% more</b> inquiries vs manually written titles"),
    ("📦 Shipping", "Same-day meetup listings close <b>3× faster</b> than delivery-only listings"),
    ("🔋 Tech", "AirPods resale value drops <b>8% per month</b> — sell within 6 months of buying"),
]

def render_ticker():
    # Double the items so the loop is seamless
    items_html = ""
    all_items = TICKER_FACTS * 2
    for icon_lbl, text in all_items:
        items_html += f'<span class="ticker-item"><span style="color:#f97316;font-weight:700;font-size:10px">{icon_lbl}</span> <span style="color:#1e1e2e">·</span> <span>{text}</span></span>'

    return f"""
<div class="ticker-wrap">
  <div class="ticker-label">⚡ LIVE INTEL</div>
  <div style="overflow:hidden;flex:1">
    <div class="ticker-track">{items_html}</div>
  </div>
</div>"""


# ══════════════════════════════════════════════════════════════════
# QR CODE
# ══════════════════════════════════════════════════════════════════
def make_qr(data: str) -> Image.Image:
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M,
                        box_size=8, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#f97316", back_color="#0d0d18")
    return img


# ══════════════════════════════════════════════════════════════════
# SIGNALS
# ══════════════════════════════════════════════════════════════════
def price_sig(l):
    p=l["price"]; avg=l["market_avg_price"] or p
    diff=((p-avg)/avg*100) if avg else 0
    if diff<=-15:  tag,col="Excellent Deal","#4ade80"
    elif diff<=-5: tag,col="Good Deal","#86efac"
    elif diff<=5:  tag,col="Fair Price","#94a3b8"
    elif diff<=15: tag,col="Slightly High","#fb923c"
    else:          tag,col="Overpriced","#f87171"
    return {"tag":tag,"col":col,"diff":round(diff,1),"avg":avg}

def time_sig(l):
    try:
        exp=datetime.fromisoformat(l["expires_at"].replace("Z","+00:00"))
        h=max(0,(exp-datetime.now(timezone.utc)).total_seconds()/3600)
    except: h=24
    if h<=3:    ic,col="🚨","#f87171"
    elif h<=12: ic,col="🔥","#fb923c"
    elif h<=24: ic,col="⏳","#fbbf24"
    else:       ic,col="✅","#4ade80"
    return {"h":round(h,1),"ic":ic,"col":col}

def comp_sig(l):
    b=l["active_buyers"] or 0; m=l["messages_count"] or 0
    if b>=5:   lbl,fomo="🔥 Very Hot",95
    elif b>=3: lbl,fomo="⚡ High Demand",80
    elif b==2: lbl,fomo="👀 2 Interested",60
    elif b==1: lbl,fomo="💭 1 Watching",40
    elif m>=1: lbl,fomo="💬 Some Interest",25
    else:      lbl,fomo="✨ Be First",10
    return {"lbl":lbl,"fomo":fomo}

def cat_icon(title):
    t=title.lower()
    if any(x in t for x in ["head","sony","iphone","mac","laptop","pixel","galaxy"]): return "📱"
    if any(x in t for x in ["bike","trek","cycle","scoot"]): return "🚲"
    if any(x in t for x in ["chair","shelf","ikea","sofa","desk","table","kallax"]): return "🪑"
    if any(x in t for x in ["switch","game","play","xbox","nintendo"]): return "🎮"
    if any(x in t for x in ["dyson","vacuum","wash","fridge","applian"]): return "🏠"
    if any(x in t for x in ["watch","rolex","omega","apple watch"]): return "⌚"
    return "📦"


# ══════════════════════════════════════════════════════════════════
# SESSION
# ══════════════════════════════════════════════════════════════════
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "browse"

qp = st.query_params
if "page" in qp and qp["page"] in ["browse","sell","signals","saved","login"]:
    st.session_state.page = qp["page"]

page = st.session_state.page
user = st.session_state.user
sid  = st.session_state.session_id


# ══════════════════════════════════════════════════════════════════
# RENDER TICKER
# ══════════════════════════════════════════════════════════════════
st.markdown(render_ticker(), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# TOP NAV
# ══════════════════════════════════════════════════════════════════
def nc(p): return "navbtn active" if page==p else "navbtn"
user_btn_label = f"👤 {user['name'].split()[0]}" if user else "🔐 Login"
user_btn_cls   = "navbtn navbtn-login logged" if user else "navbtn navbtn-login"
user_page      = "browse" if user else "login"   # clicking name goes to profile (browse for now)

st.markdown(f"""
<div class="topnav">
  <div class="topnav-brand">
    <span style="font-size:22px">⚡</span>
    <span class="topnav-brand-text">NexxtMarket</span>
  </div>
  <div class="topnav-links">
    <a class="{nc('browse')}" href="?page=browse">🏠<span class="navbtn-label"> Browse</span></a>
    <a class="{nc('sell')}" href="?page=sell">➕<span class="navbtn-label"> Sell</span></a>
    <a class="{nc('signals')}" href="?page=signals">📊<span class="navbtn-label"> AI Signals</span></a>
    <a class="{nc('saved')}" href="?page=saved">📋<span class="navbtn-label"> Saved</span></a>
    <a class="{user_btn_cls}" href="?page=login">{user_btn_label}</a>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# CARD HTML
# ══════════════════════════════════════════════════════════════════
def card_html(l, saved_ids):
    ps=price_sig(l); ts=time_sig(l); cs=comp_sig(l)
    diff_str=(f"+{ps['diff']}%" if ps['diff']>0 else f"{ps['diff']}%")
    bar=min(100,cs["fomo"])
    desc=(l["description"] or "")[:80]+("…" if len(l["description"] or "")>80 else "")
    icon=cat_icon(l["title"])
    lid=l["id"]
    is_saved=lid in saved_ids
    save_cls="save-btn saved" if is_saved else "save-btn"
    save_lbl="💾 Saved" if is_saved else "🤍 Save"
    return f"""
<div class="nm-card" id="card-{lid}">
  <div class="nm-card-top"></div>
  <div style="display:flex;gap:14px;align-items:flex-start">
    <div style="width:50px;height:50px;border-radius:12px;flex-shrink:0;
      background:#15151f;border:1px solid #252535;
      display:flex;align-items:center;justify-content:center;font-size:24px">{icon}</div>
    <div style="flex:1;min-width:0">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:10px">
        <div style="flex:1;min-width:0">
          <div style="font-size:15px;font-weight:700;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-bottom:3px">{l["title"]}</div>
          <div style="font-size:12px;color:#50506a;margin-bottom:8px;line-height:1.4">{desc}</div>
          <div style="display:flex;flex-wrap:wrap;gap:4px">
            <span class="nm-tag">📍 {l["location"]}</span>
            <span class="nm-tag">🏷 {l["category"]}</span>
            <span class="nm-tag">⭐ {l["condition"]}</span>
          </div>
        </div>
        <div style="text-align:right;flex-shrink:0">
          <div class="nm-price" style="font-size:22px">${l["price"]:,.0f}</div>
          <div style="font-size:11px;color:#40404e;margin-top:2px">avg ${ps['avg']:,.0f}</div>
          <div style="margin-top:5px">
            <span class="nm-badge" style="color:{ps['col']};background:{ps['col']}18;border:1px solid {ps['col']}30">{ps['tag']} ({diff_str})</span>
          </div>
        </div>
      </div>
      <div style="display:flex;gap:12px;margin-top:12px;padding-top:12px;
        border-top:1px solid #1a1a28;flex-wrap:wrap;align-items:center">
        <span style="font-size:13px;font-weight:600;color:{ts['col']}">{ts['ic']} {ts['h']}h left</span>
        <span style="font-size:13px;font-weight:600;color:#c0c0d8">{cs['lbl']}</span>
        <div style="flex:1;min-width:60px">
          <div style="height:4px;background:#1a1a28;border-radius:99px;overflow:hidden">
            <div style="height:4px;width:{bar}%;background:linear-gradient(90deg,#f97316,#fbbf24);border-radius:99px"></div>
          </div>
          <div style="font-size:10px;color:#30303e;margin-top:2px">FOMO {cs['fomo']}/100</div>
        </div>
        <div style="display:flex;gap:8px;align-items:center">
          <span style="font-size:11px;color:#30303e">👁 {l["views"]}</span>
          <span style="font-size:11px;color:#30303e">💾 {l["saves"]}</span>
          <span style="font-size:11px;color:#30303e">💬 {l["messages_count"]}</span>
          <span style="font-size:11px;color:#f9731660">📈 {l["rank_score"]:.0f}</span>
        </div>
      </div>
    </div>
  </div>
</div>"""


# ══════════════════════════════════════════════════════════════════
# PAGE: BROWSE
# ══════════════════════════════════════════════════════════════════
if page == "browse":
    st.markdown('<h1 style="font-size:30px">⚡ Live Marketplace</h1>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:13px;color:#40405e;margin:0 0 18px">Real-time price signals · AI deal scoring · Live competition</p>', unsafe_allow_html=True)

    c1,c2,c3 = st.columns([2,2,2])
    with c1: cat  = st.selectbox("Category",["All","Electronics","Furniture","Sports","Gaming","Appliances"])
    with c2: sort = st.selectbox("Sort by",["Rank Score","Price: Low→High","Price: High→Low","Newest"])
    with c3: maxp = st.number_input("Max Price ($)", min_value=0, value=5000, step=100)

    conn=get_db()
    q="SELECT * FROM listings WHERE status='active' AND price<=?"; params=[maxp]
    if cat!="All": q+=" AND category=?"; params.append(cat)
    sm={"Rank Score":"rank_score DESC","Price: Low→High":"price ASC",
        "Price: High→Low":"price DESC","Newest":"created_at DESC"}
    rows=[dict(r) for r in conn.execute(q+f" ORDER BY {sm[sort]}",params).fetchall()]
    conn.close()

    saved_ids = get_saved_ids(sid)
    deals=sum(1 for l in rows if price_sig(l)['diff']<=-5)
    hot=sum(1 for l in rows if l['active_buyers']>=3)
    st.markdown(f"""<div class="nm-stats">
      <div><div class="nm-stat-val">{len(rows)}</div><div class="nm-stat-lbl">Active</div></div>
      <div class="nm-sep"></div>
      <div><div class="nm-stat-val" style="color:#4ade80">{deals}</div><div class="nm-stat-lbl">Good Deals</div></div>
      <div class="nm-sep"></div>
      <div><div class="nm-stat-val" style="color:#f87171">{hot}</div><div class="nm-stat-lbl">Hot Items</div></div>
      <div class="nm-sep"></div>
      <div><div class="nm-stat-val" style="color:#a78bfa">{len(saved_ids)}</div><div class="nm-stat-lbl">Saved</div></div>
    </div>""", unsafe_allow_html=True)

    if not rows:
        st.markdown('<div class="nm-empty"><div style="font-size:40px">🔍</div><div style="font-size:16px;margin-top:10px">No listings found</div></div>', unsafe_allow_html=True)
    else:
        for l in rows:
            st.markdown(card_html(l, saved_ids), unsafe_allow_html=True)
            # Save button per listing
            btn_label = "💾 Saved" if l["id"] in saved_ids else "🤍 Save"
            col1, col2 = st.columns([5, 1])
            with col2:
                if st.button(btn_label, key=f"save_{l['id']}"):
                    toggle_save(l["id"], sid)
                    st.rerun()


# ══════════════════════════════════════════════════════════════════
# PAGE: SELL
# ══════════════════════════════════════════════════════════════════
elif page == "sell":
    st.markdown('<h1 style="font-size:30px">➕ Create Listing</h1>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:13px;color:#40405e;margin:0 0 18px">AI optimizes your title, description & suggested price automatically</p>', unsafe_allow_html=True)

    if "sell_step" not in st.session_state:
        st.session_state.sell_step=1; st.session_state.ld={}; st.session_state.ai_res=None

    step=st.session_state.sell_step
    cols=st.columns(3)
    for i,(label,) in enumerate([("Details",),("AI Optimize",),("Publish",)]):
        n=i+1
        if n<step:    bg,tc="#16a34a18","#4ade80"; dot="✓"
        elif n==step: bg,tc="#f9731618","#f97316"; dot=str(n)
        else:         bg,tc="#15151f","#303045";   dot=str(n)
        with cols[i]:
            st.markdown(f"""<div style="background:{bg};border:1px solid {tc}40;border-radius:12px;padding:12px 8px;text-align:center;margin-bottom:20px">
              <div style="font-size:18px;font-weight:800;color:{tc}">{dot}</div>
              <div style="font-size:11px;color:{tc};margin-top:2px;text-transform:uppercase;letter-spacing:.5px">{label}</div>
            </div>""", unsafe_allow_html=True)

    if step==1:
        with st.form("sell1"):
            title    = st.text_input("Item Title", placeholder="e.g. Sony WH-1000XM4 Headphones")
            desc     = st.text_area("Description", placeholder="Condition, what's included, why selling…", height=100)
            c1,c2    = st.columns(2)
            with c1:
                price    = st.number_input("Price (SGD)", min_value=1.0, value=100.0, step=10.0)
                category = st.selectbox("Category",["Electronics","Furniture","Sports","Gaming","Appliances","Fashion","Books","Other"])
            with c2:
                condition = st.selectbox("Condition",["excellent","good","fair","poor"])
                duration  = st.selectbox("Duration",[24,48,72],format_func=lambda x:f"{x} hours")
            location = st.text_input("Location", value="Singapore")
            if st.form_submit_button("Next → AI Optimize"):
                if not title.strip() or not desc.strip():
                    st.error("Title and description are required.")
                else:
                    st.session_state.ld=dict(title=title,description=desc,price=price,
                        category=category,condition=condition,location=location,duration=duration)
                    st.session_state.sell_step=2; st.rerun()

    elif step==2:
        d=st.session_state.ld
        if st.session_state.ai_res is None:
            with st.spinner("✨ Optimizing with AI…"):
                raw=groq_chat("Return ONLY valid JSON, no extra text.",
                    f'Title:{d["title"]}\nDesc:{d["description"]}\nPrice:${d["price"]}\nCat:{d["category"]}\nReturn:{{"optimized_title":"...","optimized_description":"...","suggested_price":0,"deal_score":0,"key_improvements":["...","..."]}}',400)
                res=None
                if raw:
                    try:
                        m=re.search(r'\{.*\}',raw,re.DOTALL); res=json.loads(m.group()) if m else None
                    except: pass
                if not res:
                    res={"optimized_title":d['title'].title(),"optimized_description":d['description'],
                         "suggested_price":d['price'],"deal_score":70,
                         "key_improvements":["Add more photos for +40% engagement",
                                             "Mention original purchase price","Include reason for selling"]}
            st.session_state.ai_res=res

        res=st.session_state.ai_res; score=res.get("deal_score",70)
        sc="#4ade80" if score>=70 else "#fbbf24" if score>=50 else "#f87171"
        st.markdown(f"""<div style="background:#0d0d18;border:1px solid #1e1e30;border-radius:14px;
          padding:18px 20px;display:flex;align-items:center;gap:18px;margin-bottom:16px">
          <div style="width:68px;height:68px;border-radius:50%;flex-shrink:0;
            background:conic-gradient({sc} {score*3.6}deg,#1e1e30 0deg);
            display:flex;align-items:center;justify-content:center">
            <div style="width:54px;height:54px;border-radius:50%;background:#0d0d18;
              display:flex;align-items:center;justify-content:center;
              font-size:18px;font-weight:800;color:{sc};font-family:'JetBrains Mono',monospace">{score}</div>
          </div>
          <div>
            <div style="font-size:16px;font-weight:700;color:#fff">AI Deal Score</div>
            <div style="font-size:12px;color:#505068;margin-top:3px">
              {"Strong listing — high conversion expected" if score>=70
               else "Decent — a few tweaks could help" if score>=50
               else "Needs improvement before publishing"}
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

        c1,c2=st.columns(2)
        with c1:
            st.markdown('<div class="nm-section-title">Original</div>', unsafe_allow_html=True)
            st.markdown(f"""<div style="background:#0d0d18;border:1px solid #1e1e30;border-radius:12px;padding:14px">
              <div style="font-size:14px;font-weight:700;color:#a0a0c0;margin-bottom:8px">{d['title']}</div>
              <div style="font-size:12px;color:#505068;line-height:1.5">{d['description'][:200]}</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="nm-section-title">✨ AI Optimized</div>', unsafe_allow_html=True)
            st.markdown(f"""<div style="background:#0d1a0d;border:1px solid #16a34a30;border-radius:12px;padding:14px">
              <div style="font-size:14px;font-weight:700;color:#4ade80;margin-bottom:8px">{res.get('optimized_title',d['title'])}</div>
              <div style="font-size:12px;color:#688068;line-height:1.5">{res.get('optimized_description',d['description'])[:200]}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<div class="nm-section-title">💡 Key Improvements</div>', unsafe_allow_html=True)
        for tip in res.get("key_improvements",[]):
            st.markdown(f"""<div style="background:#0d0d18;border-left:2px solid #f97316;border-radius:0 10px 10px 0;padding:8px 14px;margin:4px 0;font-size:13px;color:#a0a0c0;line-height:1.4">{tip}</div>""", unsafe_allow_html=True)

        use_ai=st.toggle("Use AI-optimized version",value=True)
        st.session_state.ld["use_ai"]=use_ai; st.session_state.ld["ai_res"]=res
        c1,c2=st.columns(2)
        with c1:
            if st.button("← Back"): st.session_state.sell_step=1; st.rerun()
        with c2:
            if st.button("Preview & Publish →"): st.session_state.sell_step=3; st.rerun()

    elif step==3:
        d=st.session_state.ld; res=d.get("ai_res",{}); use_ai=d.get("use_ai",False)
        ft=res.get("optimized_title",d['title']) if use_ai else d['title']
        fd=res.get("optimized_description",d['description']) if use_ai else d['description']
        st.markdown(f"""<div class="nm-card" style="margin-bottom:20px">
          <div class="nm-card-top"></div>
          <div style="font-size:20px;font-weight:800;color:#fff;margin-bottom:8px">{ft}</div>
          <div style="display:flex;align-items:baseline;gap:12px;margin-bottom:12px;flex-wrap:wrap">
            <span class="nm-price" style="font-size:26px">${d['price']:,.0f} SGD</span>
            <span style="font-size:12px;color:#505068">{d['category']} · {d['condition']} · ⏰ {d['duration']}h · 📍 {d['location']}</span>
          </div>
          <div style="font-size:13px;color:#70708a;line-height:1.6">{fd}</div>
        </div>""", unsafe_allow_html=True)

        c1,c2=st.columns(2)
        with c1:
            if st.button("← Back"): st.session_state.sell_step=2; st.rerun()
        with c2:
            if st.button("🚀 Publish Listing"):
                conn=get_db()
                exp=(datetime.now(timezone.utc)+timedelta(hours=d['duration'])).isoformat()
                row=conn.execute("SELECT AVG(price) FROM listings WHERE category=? AND status='active'",(d['category'],)).fetchone()
                mkt=row[0] if row[0] else d['price']
                uid=user['id'] if user else None
                conn.execute("INSERT INTO listings(user_id,title,description,price,category,condition,location,market_avg_price,ai_deal_score,rank_score,expires_at,views,saves,messages_count,active_buyers)VALUES(?,?,?,?,?,?,?,?,?,?,?,0,0,0,0)",
                    (uid,ft,fd,d['price'],d['category'],d['condition'],d['location'],mkt,res.get("deal_score",70),85.0,exp))
                conn.commit(); conn.close()
                st.success("✅ Your listing is now live on the marketplace!")
                st.balloons()
                st.session_state.sell_step=1; st.session_state.ai_res=None; st.session_state.ld={}
                st.markdown('<div style="text-align:center;margin-top:12px"><a href="?page=browse" style="color:#f97316;font-size:14px;font-weight:600;text-decoration:none">→ View on marketplace</a></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# PAGE: AI SIGNALS
# ══════════════════════════════════════════════════════════════════
elif page == "signals":
    st.markdown('<h1 style="font-size:30px">📊 AI Signal Engine</h1>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:13px;color:#40405e;margin:0 0 18px">See all engagement signals fire in real time for any listing</p>', unsafe_allow_html=True)

    with st.form("sig_form"):
        c1,c2=st.columns(2)
        with c1:
            t=st.text_input("Item title","Sony WH-1000XM4 Headphones")
            p=st.number_input("Your price ($)",value=180.0,step=5.0)
            avg=st.number_input("Market average ($)",value=210.0,step=5.0)
        with c2:
            views=st.number_input("Views last hour",value=15,step=1)
            buyers=st.number_input("Active buyers",value=3,step=1)
            hrs=st.slider("Hours until expiry",1,72,20)
        go=st.form_submit_button("⚡  Generate All Signals")

    if go:
        mock={"price":p,"market_avg_price":avg,"views_last_hour":views,
              "messages_count":int(buyers),"active_buyers":int(buyers),
              "expires_at":(datetime.now(timezone.utc)+timedelta(hours=hrs)).isoformat()}
        ps=price_sig(mock); ts=time_sig(mock); cs=comp_sig(mock)
        diff_str=f"+{ps['diff']}%" if ps['diff']>0 else f"{ps['diff']}%"

        c1,c2=st.columns(2)
        sigs=[
            ("💰","Price Signal",ps['tag'],f"{diff_str} vs market avg ${avg:,.0f}",ps['col']),
            ("⏱","Time Pressure",f"{ts['ic']} {'Critical' if hrs<=3 else 'High' if hrs<=12 else 'Low'}",f"{hrs}h remaining",ts['col']),
            ("👥","Competition",cs['lbl'],f"FOMO score: {cs['fomo']}/100","#a78bfa"),
            ("👁","Social Proof",f"{views} views/hr","Buyer interest active","#60a5fa"),
        ]
        for i,(icon,lbl,val,sub,col) in enumerate(sigs):
            with(c1 if i%2==0 else c2):
                st.markdown(f"""<div style="background:#0d0d18;border:1px solid {col}28;border-radius:14px;padding:16px;margin-bottom:10px">
                  <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
                    <span style="font-size:20px">{icon}</span>
                    <span style="font-size:10px;color:#404055;text-transform:uppercase;letter-spacing:1px;font-weight:600">{lbl}</span>
                  </div>
                  <div style="font-size:18px;font-weight:700;color:{col};margin-bottom:3px">{val}</div>
                  <div style="font-size:12px;color:#404055">{sub}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown(f"""<div style="background:#0d0d18;border:1px solid #2a2a3e;border-radius:14px;padding:16px;margin-bottom:14px">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
            <span style="font-size:14px;font-weight:700;color:#fff">🔥 Overall FOMO Score</span>
            <span style="font-size:24px;font-weight:800;color:#f97316;font-family:'JetBrains Mono',monospace">{cs['fomo']}/100</span>
          </div>
          <div style="height:8px;background:#1a1a28;border-radius:99px;overflow:hidden">
            <div style="height:8px;width:{cs['fomo']}%;background:linear-gradient(90deg,#f97316,#fbbf24);border-radius:99px"></div>
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="nm-section-title">🤖 AI Insight</div>', unsafe_allow_html=True)
        with st.spinner("Generating…"):
            insight=groq_chat("Marketplace analyst. Write ONE punchy 2-sentence insight. Use specific numbers.",
                f"Item:{t}, Price:${p}, Market avg:${avg}, {buyers} buyers, {hrs}h left, {views} views/hr")
        if insight:
            st.markdown(f"""<div style="background:#0a1525;border-left:3px solid #3b82f6;border-radius:0 12px 12px 0;padding:14px 18px;font-size:14px;color:#93c5fd;line-height:1.6">{insight}</div>""", unsafe_allow_html=True)
        else:
            st.info("Add GROQ_API_KEY in Streamlit Secrets to enable AI-generated insights.")


# ══════════════════════════════════════════════════════════════════
# PAGE: SAVED
# ══════════════════════════════════════════════════════════════════
elif page == "saved":
    st.markdown('<h1 style="font-size:30px">📋 Saved Listings</h1>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:13px;color:#40405e;margin:0 0 18px">Items you\'ve bookmarked this session</p>', unsafe_allow_html=True)

    conn=get_db()
    saved=[dict(r) for r in conn.execute(
        "SELECT l.* FROM listings l JOIN saved_listings sl ON l.id=sl.listing_id WHERE sl.session_id=? ORDER BY sl.created_at DESC",
        (sid,)).fetchall()]
    conn.close()
    saved_ids=get_saved_ids(sid)

    if not saved:
        st.markdown("""<div class="nm-empty">
          <div style="font-size:40px">💾</div>
          <div style="font-size:16px;margin-top:10px;color:#505068">No saved listings yet</div>
          <div style="font-size:13px;margin-top:6px;color:#303045">Browse and tap 🤍 Save on any listing</div>
        </div>""", unsafe_allow_html=True)
        if st.button("→ Browse Marketplace"):
            st.query_params["page"]="browse"; st.rerun()
    else:
        for l in saved:
            st.markdown(card_html(l,saved_ids), unsafe_allow_html=True)
            c1,c2=st.columns([5,1])
            with c2:
                if st.button("🗑 Remove", key=f"rm_{l['id']}"):
                    toggle_save(l["id"],sid); st.rerun()


# ══════════════════════════════════════════════════════════════════
# PAGE: LOGIN
# ══════════════════════════════════════════════════════════════════
elif page == "login":
    if user:
        # Already logged in — show profile + QR
        st.markdown(f'<h1 style="font-size:30px">👤 My Profile</h1>', unsafe_allow_html=True)
        st.markdown(f"""<div style="background:#0d0d18;border:1px solid #1e1e30;border-radius:16px;padding:22px;margin-bottom:20px">
          <div style="font-size:20px;font-weight:800;color:#fff;margin-bottom:4px">{user['name']}</div>
          <div style="font-size:13px;color:#505068">📱 {user['phone']}</div>
          <div style="font-size:12px;color:#303045;margin-top:6px">Member since {user.get('created_at','—')[:10]}</div>
        </div>""", unsafe_allow_html=True)

        col1, col2 = st.columns([1,1])
        with col1:
            st.markdown('<div class="nm-section-title">📱 Scan to open on mobile</div>', unsafe_allow_html=True)
            app_url = "https://nexxt-market-xjiavvz9ljtratr8kx77xi.streamlit.app"
            qr_img = make_qr(f"{app_url}?page=browse")
            buf = io.BytesIO()
            qr_img.save(buf, format="PNG")
            st.image(buf.getvalue(), width=200, caption="Scan with your phone camera")

        with col2:
            st.markdown('<div class="nm-section-title">📊 Your Activity</div>', unsafe_allow_html=True)
            conn=get_db()
            my_listings=conn.execute("SELECT COUNT(*) FROM listings WHERE user_id=?",(user['id'],)).fetchone()[0]
            my_saved=conn.execute("SELECT COUNT(*) FROM saved_listings WHERE session_id=?",(sid,)).fetchone()[0]
            conn.close()
            st.markdown(f"""
            <div style="display:flex;flex-direction:column;gap:10px">
              <div style="background:#0d0d18;border:1px solid #1e1e30;border-radius:12px;padding:14px">
                <div style="font-size:24px;font-weight:800;color:#f97316;font-family:'JetBrains Mono',monospace">{my_listings}</div>
                <div style="font-size:12px;color:#404055;margin-top:2px">Active Listings</div>
              </div>
              <div style="background:#0d0d18;border:1px solid #1e1e30;border-radius:12px;padding:14px">
                <div style="font-size:24px;font-weight:800;color:#a78bfa;font-family:'JetBrains Mono',monospace">{my_saved}</div>
                <div style="font-size:12px;color:#404055;margin-top:2px">Saved Items</div>
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        if st.button("🚪 Log Out"):
            st.session_state.user=None; st.query_params["page"]="browse"; st.rerun()

    else:
        # Login / Register
        st.markdown('<h1 style="font-size:30px">🔐 Login / Register</h1>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:13px;color:#40405e;margin:0 0 20px">Use your mobile number as your login ID. No email needed.</p>', unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["  Sign In  ", "  Register  "])

        with tab1:
            with st.form("login_form"):
                phone = st.text_input("Mobile Number", placeholder="+65 9123 4567")
                pin   = st.text_input("PIN (4–6 digits)", type="password", placeholder="••••••")
                login_btn = st.form_submit_button("Sign In →")
            if login_btn:
                if not phone.strip() or not pin.strip():
                    st.error("Enter your mobile number and PIN.")
                else:
                    u = login_user(phone.strip(), pin.strip())
                    if u:
                        st.session_state.user = u
                        st.success(f"Welcome back, {u['name']}! 👋")
                        time.sleep(1)
                        st.query_params["page"]="browse"; st.rerun()
                    else:
                        st.error("Phone number or PIN incorrect. Try again or register below.")

            # QR code for mobile access
            st.markdown('<div class="nm-section-title">📱 Open on your phone</div>', unsafe_allow_html=True)
            app_url = "https://nexxt-market-xjiavvz9ljtratr8kx77xi.streamlit.app"
            qr_img  = make_qr(f"{app_url}?page=login")
            buf     = io.BytesIO()
            qr_img.save(buf, format="PNG")
            col1,col2 = st.columns([1,2])
            with col1:
                st.image(buf.getvalue(), width=160)
            with col2:
                st.markdown("""<div style="padding:10px 0">
                  <div style="font-size:14px;font-weight:700;color:#fff;margin-bottom:6px">Scan to open NexxtMarket on mobile</div>
                  <div style="font-size:12px;color:#505068;line-height:1.6">
                    1. Open your phone camera<br>
                    2. Point at the QR code<br>
                    3. Tap the link that appears<br>
                    4. Log in with the same phone + PIN
                  </div>
                </div>""", unsafe_allow_html=True)

        with tab2:
            with st.form("reg_form"):
                r_name  = st.text_input("Your Name", placeholder="Jane Smith")
                r_phone = st.text_input("Mobile Number", placeholder="+65 9123 4567")
                r_pin   = st.text_input("Choose a PIN (4–6 digits)", type="password", placeholder="••••••")
                r_pin2  = st.text_input("Confirm PIN", type="password", placeholder="••••••")
                reg_btn = st.form_submit_button("Create Account →")
            if reg_btn:
                if not all([r_name.strip(), r_phone.strip(), r_pin.strip(), r_pin2.strip()]):
                    st.error("All fields are required.")
                elif len(r_pin) < 4:
                    st.error("PIN must be at least 4 digits.")
                elif r_pin != r_pin2:
                    st.error("PINs don't match.")
                else:
                    u = register_user(r_phone.strip(), r_name.strip(), r_pin.strip())
                    if u:
                        st.session_state.user = dict(u)
                        st.success(f"Account created! Welcome, {r_name}! 🎉")
                        time.sleep(1)
                        st.query_params["page"]="browse"; st.rerun()
                    else:
                        st.error("That phone number is already registered. Try signing in.")
