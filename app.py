"""
NexxtMarket — Streamlit v3 (Mobile-first, fully dark, readable)
"""
import streamlit as st
import sqlite3, json, os, re, uuid, httpx
from datetime import datetime, timezone, timedelta

st.set_page_config(page_title="NexxtMarket", page_icon="⚡", layout="wide",
                   initial_sidebar_state="collapsed")

# ═══════════════════════════════════════════════════════════════
# CSS — full dark theme + mobile nav + fix all white inputs
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

/* ── Reset & base ── */
*, html, body, [class*="css"] {
  font-family: 'Space Grotesk', sans-serif !important;
  box-sizing: border-box;
}
[data-testid="stAppViewContainer"] { background: #060609 !important; }
[data-testid="stSidebar"] { display: none !important; }
#MainMenu, footer, header, [data-testid="stToolbar"],
[data-testid="collapsedControl"] { display: none !important; visibility: hidden !important; }
[data-testid="stMainBlockContainer"] { padding: 0 !important; max-width: 100% !important; }
[data-testid="stMain"] { padding: 0 !important; }
.block-container { padding: 0 1.2rem 2rem !important; max-width: 860px !important; margin: 0 auto !important; }

/* ── Typography ── */
h1 { color: #fff !important; font-weight: 800 !important; letter-spacing: -1.5px !important; margin: 0 0 4px !important; }
h2, h3 { color: #fff !important; font-weight: 700 !important; }
p, label, span { color: #a0a0b8 !important; }

/* ── ALL text inputs dark ── */
input, textarea, select,
.stTextInput input,
.stTextArea textarea,
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
  background: #111118 !important;
  border: 1.5px solid #252535 !important;
  color: #ffffff !important;
  border-radius: 10px !important;
  font-family: 'Space Grotesk', sans-serif !important;
  font-size: 14px !important;
}
.stTextInput input:focus,
.stTextArea textarea:focus {
  border-color: #f97316 !important;
  box-shadow: 0 0 0 3px #f9731620 !important;
  outline: none !important;
}
.stTextInput label, .stTextArea label, .stNumberInput label,
.stSelectbox label, .stSlider label {
  color: #808099 !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  text-transform: uppercase !important;
  letter-spacing: .5px !important;
  margin-bottom: 4px !important;
}

/* ── Number input — kill white bg completely ── */
[data-testid="stNumberInput"] > div,
[data-testid="stNumberInput"] > div > div {
  background: #111118 !important;
  border: 1.5px solid #252535 !important;
  border-radius: 10px !important;
  overflow: hidden !important;
}
[data-testid="stNumberInput"] input {
  background: #111118 !important;
  color: #ffffff !important;
  border: none !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-weight: 600 !important;
  font-size: 16px !important;
}
[data-testid="stNumberInput"] button {
  background: #1e1e30 !important;
  color: #f97316 !important;
  border: none !important;
  border-left: 1px solid #252535 !important;
  font-size: 18px !important;
  font-weight: 700 !important;
  min-width: 44px !important;
  cursor: pointer !important;
}
[data-testid="stNumberInput"] button:hover { background: #f97316 !important; color: #000 !important; }
[data-testid="stNumberInput"] button:first-child { border-left: none !important; border-right: 1px solid #252535 !important; }

/* ── Select box ── */
[data-testid="stSelectbox"] > div > div {
  background: #111118 !important;
  border: 1.5px solid #252535 !important;
  color: #ffffff !important;
  border-radius: 10px !important;
}
[data-testid="stSelectbox"] > div > div > div { color: #ffffff !important; }
[data-baseweb="select"] { background: #111118 !important; }
[data-baseweb="popover"] > div {
  background: #111118 !important;
  border: 1px solid #252535 !important;
  border-radius: 10px !important;
}
[data-baseweb="menu"] { background: #111118 !important; }
[data-baseweb="option"] { background: #111118 !important; color: #c0c0d8 !important; }
[data-baseweb="option"]:hover { background: #1e1e30 !important; }
[aria-selected="true"][data-baseweb="option"] { background: #f9731620 !important; color: #f97316 !important; }

/* ── Slider ── */
[data-testid="stSlider"] > div { padding: 0 !important; }
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
  background: #f97316 !important;
}
[data-testid="stSlider"] div[data-testid="stTickBarMin"],
[data-testid="stSlider"] div[data-testid="stTickBarMax"] { color: #404055 !important; }

/* ── Primary button ── */
.stButton > button {
  background: linear-gradient(135deg, #f97316, #dc5a0a) !important;
  color: #000000 !important;
  font-family: 'Space Grotesk', sans-serif !important;
  font-weight: 700 !important;
  font-size: 14px !important;
  border: none !important;
  border-radius: 12px !important;
  padding: 0.65rem 1.6rem !important;
  width: 100% !important;
  transition: all .2s !important;
  box-shadow: 0 4px 20px #f9731630 !important;
  letter-spacing: .3px !important;
}
.stButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 28px #f9731650 !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Form container ── */
[data-testid="stForm"] {
  background: #0d0d15 !important;
  border: 1px solid #1e1e30 !important;
  border-radius: 16px !important;
  padding: 24px !important;
}

/* ── Toggle ── */
[data-testid="stToggle"] { accent-color: #f97316; }
[data-testid="stToggle"] label { color: #c0c0d8 !important; }

/* ── Progress ── */
.stProgress > div > div { background: #1a1a28 !important; border-radius: 99px !important; height: 6px !important; }
.stProgress > div > div > div { background: linear-gradient(90deg, #f97316, #fbbf24) !important; border-radius: 99px !important; }

/* ── Tabs ── */
[data-baseweb="tab-list"] {
  background: #0d0d15 !important;
  border-radius: 12px !important;
  padding: 5px !important;
  border: 1px solid #1e1e30 !important;
  gap: 4px !important;
}
[data-baseweb="tab"] { background: transparent !important; color: #505068 !important; border-radius: 8px !important; font-weight: 600 !important; }
[aria-selected="true"][data-baseweb="tab"] { background: #f97316 !important; color: #000 !important; }
[data-baseweb="tab-highlight"] { display: none !important; }
[data-baseweb="tab-border"] { display: none !important; }

/* ── Divider ── */
hr { border-color: #1a1a28 !important; margin: 16px 0 !important; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #f97316 !important; }

/* ── Alert / info boxes ── */
[data-testid="stAlert"] {
  background: #0d0d15 !important;
  border-radius: 12px !important;
  color: #c0c0d8 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #060609; }
::-webkit-scrollbar-thumb { background: #252535; border-radius: 99px; }

/* ══════════════════════════════════
   TOP NAV BAR (always visible)
══════════════════════════════════ */
.topnav {
  position: sticky;
  top: 0;
  z-index: 9999;
  background: rgba(6,6,9,0.95);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid #1a1a28;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  margin-bottom: 24px;
  width: 100%;
}
.topnav-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
}
.topnav-brand-text {
  font-size: 18px;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: -0.5px;
  white-space: nowrap;
}
.topnav-links {
  display: flex;
  align-items: center;
  gap: 4px;
}
.navbtn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  color: #606078;
  cursor: pointer;
  transition: all .15s;
  border: none;
  background: transparent;
  white-space: nowrap;
  text-decoration: none;
}
.navbtn:hover { background: #1a1a28; color: #ffffff; }
.navbtn.active { background: #f9731618; color: #f97316; border: 1px solid #f9731630; }

/* Mobile nav */
@media (max-width: 600px) {
  .topnav { padding: 0 12px; height: 52px; }
  .topnav-brand-text { font-size: 16px; }
  .navbtn { padding: 8px 10px; font-size: 12px; gap: 3px; }
  .navbtn-label { display: none; }
  .navbtn { padding: 8px 10px; }
  .block-container { padding: 0 0.8rem 2rem !important; }
}

/* ── Card styles ── */
.nm-card {
  background: linear-gradient(145deg, #0d0d18, #10101e);
  border: 1px solid #1e1e32;
  border-radius: 16px;
  padding: 18px 20px;
  margin-bottom: 10px;
  position: relative;
  overflow: hidden;
  transition: border-color .2s, box-shadow .2s;
}
.nm-card:hover { border-color: #2a2a45; box-shadow: 0 8px 32px #00000040; }
.nm-card-top { position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, #f97316, #fbbf24 40%, transparent); }
.nm-stats {
  background: #0d0d18;
  border: 1px solid #1a1a28;
  border-radius: 12px;
  padding: 12px 18px;
  display: flex;
  gap: 16px;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.nm-stat-val { font-size: 20px; font-weight: 800; color: #f97316; font-family: 'JetBrains Mono', monospace; }
.nm-stat-lbl { font-size: 11px; color: #40404e; margin-top: 1px; }
.nm-sep { width: 1px; height: 30px; background: #1a1a28; flex-shrink: 0; }
.nm-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 20px;
  display: inline-block;
}
.nm-tag {
  font-size: 11px;
  color: #50507a;
  background: #14141e;
  padding: 3px 10px;
  border-radius: 20px;
  border: 1px solid #1e1e2e;
  display: inline-block;
  margin: 2px;
}
.nm-price {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 800;
  color: #ffffff;
  line-height: 1;
}
.nm-section-title {
  font-size: 11px;
  color: #404055;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 600;
  margin: 24px 0 12px;
}
.nm-empty {
  text-align: center;
  padding: 60px 20px;
  color: #303045;
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# DB
# ═══════════════════════════════════════════════════════════════
DB = "nexxtmarket.db"
def get_db():
    c = sqlite3.connect(DB, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = get_db()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS listings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,description TEXT,
        price REAL NOT NULL,category TEXT DEFAULT 'Other',condition TEXT DEFAULT 'good',
        location TEXT DEFAULT 'Singapore',status TEXT DEFAULT 'active',
        views INTEGER DEFAULT 0,saves INTEGER DEFAULT 0,messages_count INTEGER DEFAULT 0,
        active_buyers INTEGER DEFAULT 0,market_avg_price REAL,ai_deal_score INTEGER DEFAULT 0,
        ai_title TEXT,ai_description TEXT,rank_score REAL DEFAULT 80.0,
        expires_at TEXT,created_at TEXT DEFAULT(datetime('now')));
    CREATE TABLE IF NOT EXISTS saved_listings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,listing_id INTEGER,session_id TEXT,
        created_at TEXT DEFAULT(datetime('now')));
    """)
    if c.execute("SELECT COUNT(*) FROM listings").fetchone()[0] == 0:
        seeds = [
            ("Sony WH-1000XM4 Headphones","Excellent noise cancelling, barely used. Original box included.",180,"Electronics","excellent",210,91,8),
            ("Trek FX3 City Bike 2022","Perfect urban commuter. Fully serviced 3 months ago.",420,"Sports","good",480,78,5),
            ("IKEA KALLAX Shelf 4×2","White, minor scuff on side. Self-collect only.",65,"Furniture","good",90,62,3),
            ("MacBook Pro M1 16GB 512GB","Space grey, light scratches on bottom. Charger included.",1050,"Electronics","good",1200,85,6),
            ("Nintendo Switch OLED + 3 Games","Mint condition, 1 month old. AC, Mario Kart, Zelda.",320,"Gaming","excellent",370,88,7),
            ("Dyson V11 Cordless Vacuum","2 years old, filter cleaned. All attachments included.",280,"Appliances","good",340,76,4),
            ("Herman Miller Aeron Chair B","Grey, some armrest wear. Bought 2020. Very comfortable.",650,"Furniture","good",800,82,5),
            ("iPhone 14 Pro 256GB Deep Purple","No scratches. Original charger and box included.",780,"Electronics","excellent",850,90,9),
        ]
        for t,d,p,cat,cond,mkt,score,buyers in seeds:
            exp=(datetime.now(timezone.utc)+timedelta(hours=24+len(t)%48)).isoformat()
            c.execute("INSERT INTO listings(title,description,price,category,condition,market_avg_price,ai_deal_score,rank_score,expires_at,views,saves,messages_count,active_buyers)VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (t,d,p,cat,cond,mkt,score,75+score%20,exp,score*2,score//10,score//15,buyers))
    c.commit(); c.close()

init_db()


# ═══════════════════════════════════════════════════════════════
# AI
# ═══════════════════════════════════════════════════════════════
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


# ═══════════════════════════════════════════════════════════════
# Signals
# ═══════════════════════════════════════════════════════════════
def price_sig(l):
    p=l["price"]; avg=l["market_avg_price"] or p
    diff=((p-avg)/avg*100) if avg else 0
    if diff<=-15: tag,col="#4ade80","#4ade80"
    elif diff<=-5: tag,col="Good Deal","#86efac"
    elif diff<=5:  tag,col="Fair Price","#94a3b8"
    elif diff<=15: tag,col="Slightly High","#fb923c"
    else:          tag,col="Overpriced","#f87171"
    if diff<=-15: tag="Excellent Deal"
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
    if any(x in t for x in ["head","sony","iphone","mac","laptop","pixel","samsung"]): return "📱"
    if any(x in t for x in ["bike","trek","cycle","scooter"]): return "🚲"
    if any(x in t for x in ["chair","shelf","ikea","sofa","desk","table","kallax"]): return "🪑"
    if any(x in t for x in ["switch","game","play","xbox","nintendo"]): return "🎮"
    if any(x in t for x in ["dyson","vacuum","wash","applian","fridge"]): return "🏠"
    if any(x in t for x in ["watch","rolex","omega","apple watch"]): return "⌚"
    return "📦"


# ═══════════════════════════════════════════════════════════════
# TOP NAV — rendered first, always visible
# ═══════════════════════════════════════════════════════════════
if "page" not in st.session_state:
    st.session_state.page = "browse"

page = st.session_state.page

def nav_class(p): return "navbtn active" if page == p else "navbtn"

st.markdown(f"""
<div class="topnav">
  <div class="topnav-brand">
    <span style="font-size:22px">⚡</span>
    <span class="topnav-brand-text">NexxtMarket</span>
  </div>
  <div class="topnav-links">
    <a class="{nav_class('browse')}" href="?page=browse">
      <span>🏠</span><span class="navbtn-label">Browse</span>
    </a>
    <a class="{nav_class('sell')}" href="?page=sell">
      <span>➕</span><span class="navbtn-label">Sell</span>
    </a>
    <a class="{nav_class('signals')}" href="?page=signals">
      <span>📊</span><span class="navbtn-label">AI Signals</span>
    </a>
    <a class="{nav_class('saved')}" href="?page=saved">
      <span>📋</span><span class="navbtn-label">Saved</span>
    </a>
  </div>
</div>
""", unsafe_allow_html=True)

# Read page from URL query param
qp = st.query_params
if "page" in qp and qp["page"] in ["browse","sell","signals","saved"]:
    page = qp["page"]
    st.session_state.page = page


# ═══════════════════════════════════════════════════════════════
# CARD HTML
# ═══════════════════════════════════════════════════════════════
def card_html(l):
    ps=price_sig(l); ts=time_sig(l); cs=comp_sig(l)
    diff_str=(f"+{ps['diff']}%" if ps['diff']>0 else f"{ps['diff']}%")
    bar=min(100,cs["fomo"])
    desc=(l["description"] or "")[:80]+("…" if len(l["description"] or "")>80 else "")
    icon=cat_icon(l["title"])
    return f"""
<div class="nm-card">
  <div class="nm-card-top"></div>
  <div style="display:flex;gap:14px;align-items:flex-start">
    <div style="width:50px;height:50px;border-radius:12px;flex-shrink:0;
      background:#15151f;border:1px solid #252535;
      display:flex;align-items:center;justify-content:center;font-size:24px">{icon}</div>
    <div style="flex:1;min-width:0">
      <!-- Title + Price row -->
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:10px">
        <div style="flex:1;min-width:0">
          <div style="font-size:15px;font-weight:700;color:#ffffff;
            white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-bottom:3px">{l["title"]}</div>
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
            <span class="nm-badge" style="color:{ps['col']};background:{ps['col']}18;border:1px solid {ps['col']}30">
              {ps['tag']} ({diff_str})
            </span>
          </div>
        </div>
      </div>
      <!-- Signal bar -->
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
        <div style="display:flex;gap:8px">
          <span style="font-size:11px;color:#30303e">👁 {l["views"]}</span>
          <span style="font-size:11px;color:#30303e">💾 {l["saves"]}</span>
          <span style="font-size:11px;color:#30303e">💬 {l["messages_count"]}</span>
          <span style="font-size:11px;color:#f9731660">📈 {l["rank_score"]:.0f}</span>
        </div>
      </div>
    </div>
  </div>
</div>"""


# ═══════════════════════════════════════════════════════════════
# PAGE: BROWSE
# ═══════════════════════════════════════════════════════════════
if page == "browse":
    st.markdown('<h1 style="font-size:32px">⚡ Live Marketplace</h1>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:13px;color:#40405e;margin:0 0 20px">Real-time price signals · AI deal scoring · Live competition data</p>', unsafe_allow_html=True)

    c1,c2,c3 = st.columns([2,2,2])
    with c1: cat = st.selectbox("Category", ["All","Electronics","Furniture","Sports","Gaming","Appliances"])
    with c2: sort = st.selectbox("Sort by", ["Rank Score","Price: Low→High","Price: High→Low","Newest"])
    with c3: maxp = st.number_input("Max Price ($)", min_value=0, value=5000, step=100)

    conn = get_db()
    q = "SELECT * FROM listings WHERE status='active' AND price<=?"; params=[maxp]
    if cat != "All": q += " AND category=?"; params.append(cat)
    sm = {"Rank Score":"rank_score DESC","Price: Low→High":"price ASC",
          "Price: High→Low":"price DESC","Newest":"created_at DESC"}
    rows = [dict(r) for r in conn.execute(q+f" ORDER BY {sm[sort]}",params).fetchall()]
    conn.close()

    # Stats bar
    deals = sum(1 for l in rows if price_sig(l)['diff'] <= -5)
    hot   = sum(1 for l in rows if l['active_buyers'] >= 3)
    st.markdown(f"""<div class="nm-stats">
      <div><div class="nm-stat-val">{len(rows)}</div><div class="nm-stat-lbl">Active</div></div>
      <div class="nm-sep"></div>
      <div><div class="nm-stat-val" style="color:#4ade80">{deals}</div><div class="nm-stat-lbl">Good Deals</div></div>
      <div class="nm-sep"></div>
      <div><div class="nm-stat-val" style="color:#f87171">{hot}</div><div class="nm-stat-lbl">Hot Items</div></div>
    </div>""", unsafe_allow_html=True)

    if not rows:
        st.markdown('<div class="nm-empty"><div style="font-size:40px">🔍</div><div style="font-size:16px;margin-top:10px">No listings found</div></div>', unsafe_allow_html=True)
    else:
        for l in rows:
            st.markdown(card_html(l), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# PAGE: SELL
# ═══════════════════════════════════════════════════════════════
elif page == "sell":
    st.markdown('<h1 style="font-size:32px">➕ Create Listing</h1>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:13px;color:#40405e;margin:0 0 20px">AI optimizes your title, description & suggested price automatically</p>', unsafe_allow_html=True)

    if "sell_step" not in st.session_state:
        st.session_state.sell_step=1; st.session_state.ld={}; st.session_state.ai_res=None

    step = st.session_state.sell_step
    steps_info = [("Details","✓" if step>1 else "1"),("AI Optimize","✓" if step>2 else "2"),("Publish","3")]
    cols = st.columns(3)
    for i,(col,(label,dot)) in enumerate(zip(cols,steps_info)):
        n=i+1
        if n<step:   bg,tc="#16a34a18","#4ade80"
        elif n==step: bg,tc="#f9731618","#f97316"
        else:        bg,tc="#15151f","#303045"
        with col:
            st.markdown(f"""<div style="background:{bg};border:1px solid {tc}40;border-radius:12px;
              padding:12px 8px;text-align:center;margin-bottom:20px">
              <div style="font-size:18px;font-weight:800;color:{tc}">{dot}</div>
              <div style="font-size:11px;color:{tc};margin-top:2px;text-transform:uppercase;letter-spacing:.5px">{label}</div>
            </div>""", unsafe_allow_html=True)

    # Step 1 — Details
    if step == 1:
        with st.form("sell_f1"):
            title    = st.text_input("Item Title", placeholder="e.g. Sony WH-1000XM4 Headphones")
            desc     = st.text_area("Description", placeholder="Condition, what's included, why selling…", height=100)
            c1,c2    = st.columns(2)
            with c1:
                price    = st.number_input("Price (SGD)", min_value=1.0, value=100.0, step=10.0)
                category = st.selectbox("Category", ["Electronics","Furniture","Sports","Gaming","Appliances","Fashion","Books","Other"])
            with c2:
                condition = st.selectbox("Condition", ["excellent","good","fair","poor"])
                duration  = st.selectbox("Duration", [24,48,72], format_func=lambda x:f"{x} hours")
            location = st.text_input("Location", value="Singapore")
            go = st.form_submit_button("Next → AI Optimize")
        if go:
            if not title.strip() or not desc.strip():
                st.error("Title and description are required.")
            else:
                st.session_state.ld = dict(title=title,description=desc,price=price,
                    category=category,condition=condition,location=location,duration=duration)
                st.session_state.sell_step=2; st.rerun()

    # Step 2 — AI
    elif step == 2:
        d = st.session_state.ld
        if st.session_state.ai_res is None:
            with st.spinner("✨ Optimizing with AI…"):
                raw = groq_chat("Return ONLY valid JSON. No extra text.",
                    f'Title:{d["title"]}\nDesc:{d["description"]}\nPrice:${d["price"]}\nCat:{d["category"]}\nCond:{d["condition"]}\nReturn:{{"optimized_title":"...","optimized_description":"...","suggested_price":0,"deal_score":0,"key_improvements":["...","..."]}}',400)
                res = None
                if raw:
                    try:
                        m=re.search(r'\{.*\}',raw,re.DOTALL); res=json.loads(m.group()) if m else None
                    except: pass
                if not res:
                    res={"optimized_title":d['title'].title(),"optimized_description":d['description'],
                         "suggested_price":d['price'],"deal_score":70,
                         "key_improvements":["Add more photos for +40% engagement","Mention original purchase price","Include reason for selling"]}
            st.session_state.ai_res=res

        res=st.session_state.ai_res; score=res.get("deal_score",70)
        sc="#4ade80" if score>=70 else "#fbbf24" if score>=50 else "#f87171"

        # Score ring
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
            <div style="font-size:16px;font-weight:700;color:#ffffff">AI Deal Score</div>
            <div style="font-size:12px;color:#505068;margin-top:3px">
              {"Strong listing — high conversion expected" if score>=70
               else "Decent — a few tweaks could help" if score>=50
               else "Needs improvement before publishing"}
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

        # Before / After
        c1,c2 = st.columns(2)
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
            st.markdown(f"""<div style="background:#0d0d18;border-left:2px solid #f97316;
              border-radius:0 10px 10px 0;padding:8px 14px;margin:4px 0;
              font-size:13px;color:#a0a0c0;line-height:1.4">{tip}</div>""", unsafe_allow_html=True)

        use_ai = st.toggle("Use AI-optimized version", value=True)
        st.session_state.ld["use_ai"]=use_ai; st.session_state.ld["ai_res"]=res

        c1,c2=st.columns(2)
        with c1:
            if st.button("← Back"): st.session_state.sell_step=1; st.rerun()
        with c2:
            if st.button("Preview & Publish →"): st.session_state.sell_step=3; st.rerun()

    # Step 3 — Preview & Publish
    elif step == 3:
        d=st.session_state.ld; res=d.get("ai_res",{}); use_ai=d.get("use_ai",False)
        ft = res.get("optimized_title",d['title']) if use_ai else d['title']
        fd = res.get("optimized_description",d['description']) if use_ai else d['description']

        st.markdown(f"""<div class="nm-card" style="margin-bottom:20px">
          <div class="nm-card-top"></div>
          <div style="font-size:20px;font-weight:800;color:#fff;margin-bottom:8px">{ft}</div>
          <div style="display:flex;align-items:baseline;gap:12px;margin-bottom:12px">
            <span class="nm-price" style="font-size:28px">${d['price']:,.0f}</span>
            <span style="font-size:12px;color:#505068">SGD · {d['category']} · {d['condition']} · ⏰ {d['duration']}h · 📍 {d['location']}</span>
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
                conn.execute("INSERT INTO listings(title,description,price,category,condition,location,market_avg_price,ai_deal_score,rank_score,expires_at)VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (ft,fd,d['price'],d['category'],d['condition'],d['location'],mkt,res.get("deal_score",70),85.0,exp))
                conn.commit(); conn.close()
                st.success("✅ Listing published! It's now live on the marketplace.")
                st.balloons()
                st.session_state.sell_step=1; st.session_state.ai_res=None; st.session_state.ld={}


# ═══════════════════════════════════════════════════════════════
# PAGE: AI SIGNALS
# ═══════════════════════════════════════════════════════════════
elif page == "signals":
    st.markdown('<h1 style="font-size:32px">📊 AI Signal Engine</h1>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:13px;color:#40405e;margin:0 0 20px">See all 7 engagement signals fire in real time for any listing</p>', unsafe_allow_html=True)

    has_key = bool(os.environ.get("GROQ_API_KEY"))
    if not has_key:
        st.markdown("""<div style="background:#1c120090;border:1px solid #ca8a0450;border-radius:12px;
          padding:12px 16px;font-size:13px;color:#fbbf24;margin-bottom:16px">
          ⚠️ <b>GROQ_API_KEY not set</b> — Add it in Streamlit Cloud → App Settings → Secrets.
          Signals will work, AI insights will be skipped.
        </div>""", unsafe_allow_html=True)

    with st.form("sig_form"):
        c1,c2 = st.columns(2)
        with c1:
            t     = st.text_input("Item title", "Sony WH-1000XM4 Headphones")
            price = st.number_input("Your price ($)", value=180.0, step=5.0)
            avg   = st.number_input("Market average ($)", value=210.0, step=5.0)
        with c2:
            views  = st.number_input("Views last hour", value=15, step=1)
            buyers = st.number_input("Active buyers", value=3, step=1)
            hrs    = st.slider("Hours until expiry", 1, 72, 20)
        go = st.form_submit_button("⚡  Generate All Signals")

    if go:
        mock = {"price":price,"market_avg_price":avg,"views_last_hour":views,
                "messages_count":int(buyers),"active_buyers":int(buyers),
                "expires_at":(datetime.now(timezone.utc)+timedelta(hours=hrs)).isoformat()}
        ps=price_sig(mock); ts=time_sig(mock); cs=comp_sig(mock)
        diff_str=f"+{ps['diff']}%" if ps['diff']>0 else f"{ps['diff']}%"

        c1,c2 = st.columns(2)
        sigs = [
            ("💰","Price Signal",ps['tag'],f"{diff_str} vs market avg ${avg:,.0f}",ps['col']),
            ("⏱","Time Pressure",f"{ts['ic']} {'Critical' if hrs<=3 else 'High' if hrs<=12 else 'Medium' if hrs<=24 else 'Low'}",f"{hrs}h remaining",ts['col']),
            ("👥","Competition",cs['lbl'],f"FOMO score: {cs['fomo']}/100","#a78bfa"),
            ("👁","Social Proof",f"{views} views/hr","Buyer interest active","#60a5fa"),
        ]
        for i,(icon,lbl,val,sub,col) in enumerate(sigs):
            with (c1 if i%2==0 else c2):
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
            <span style="font-size:14px;font-weight:700;color:#ffffff">🔥 Overall FOMO Score</span>
            <span style="font-size:24px;font-weight:800;color:#f97316;font-family:'JetBrains Mono',monospace">{cs['fomo']}/100</span>
          </div>
          <div style="height:8px;background:#1a1a28;border-radius:99px;overflow:hidden">
            <div style="height:8px;width:{cs['fomo']}%;background:linear-gradient(90deg,#f97316,#fbbf24);border-radius:99px"></div>
          </div>
          <div style="font-size:11px;color:#30303e;margin-top:6px">Higher = more urgency for buyers to act fast</div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="nm-section-title">🤖 AI Insight</div>', unsafe_allow_html=True)
        with st.spinner("Generating AI insight…"):
            insight = groq_chat(
                "Marketplace pricing analyst. Write ONE punchy insight (2 sentences max). Use actual numbers.",
                f"Item:{t}, Price:${price}, Market avg:${avg}, {buyers} active buyers, {hrs}h left, {views} views/hr")
        if insight:
            st.markdown(f"""<div style="background:#0a1525;border-left:3px solid #3b82f6;border-radius:0 12px 12px 0;
              padding:14px 18px;font-size:14px;color:#93c5fd;line-height:1.6">{insight}</div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div style="background:#0d0d18;border:1px solid #252535;border-radius:12px;
              padding:12px 16px;font-size:13px;color:#505068">
              Add GROQ_API_KEY in Streamlit Secrets to enable AI-generated insights.</div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# PAGE: SAVED
# ═══════════════════════════════════════════════════════════════
elif page == "saved":
    st.markdown('<h1 style="font-size:32px">📋 Saved Listings</h1>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:13px;color:#40405e;margin:0 0 20px">Listings you\'ve bookmarked this session</p>', unsafe_allow_html=True)

    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    conn=get_db()
    saved=[dict(r) for r in conn.execute(
        "SELECT l.* FROM listings l JOIN saved_listings sl ON l.id=sl.listing_id WHERE sl.session_id=? ORDER BY sl.created_at DESC",
        (st.session_state.session_id,)).fetchall()]
    conn.close()

    if not saved:
        st.markdown("""<div class="nm-empty">
          <div style="font-size:40px">💾</div>
          <div style="font-size:16px;margin-top:10px;color:#505068">No saved listings yet</div>
          <div style="font-size:13px;margin-top:6px;color:#303045">Browse the marketplace to find items you like</div>
        </div>""", unsafe_allow_html=True)
    else:
        for l in saved:
            st.markdown(card_html(l), unsafe_allow_html=True)
