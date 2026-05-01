"""
NexxtMarket — Streamlit Edition (Polished UI v2)
"""
import streamlit as st
import sqlite3, json, os, re, uuid, httpx
from datetime import datetime, timezone, timedelta

st.set_page_config(page_title="NexxtMarket", page_icon="⚡", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
html,[class*="css"]{font-family:'Space Grotesk',sans-serif}
[data-testid="stAppViewContainer"]{background:#050508}
[data-testid="stSidebar"]{background:#0c0c12!important;border-right:1px solid #1e1e2e}
[data-testid="stSidebar"] *{color:#a0a0b8!important}
[data-testid="stSidebar"] .stRadio label{color:#fff!important;font-size:14px!important}
#MainMenu,footer,header{visibility:hidden}
h1{color:#fff!important;font-weight:700!important;letter-spacing:-1px}
h2,h3{color:#fff!important;font-weight:600!important}
.stButton>button{background:linear-gradient(135deg,#f97316,#ea580c)!important;color:#000!important;font-family:'Space Grotesk',sans-serif!important;font-weight:700!important;font-size:14px!important;border:none!important;border-radius:10px!important;padding:.6rem 1.5rem!important;transition:all .2s!important;box-shadow:0 0 20px #f9731630!important}
.stButton>button:hover{transform:translateY(-1px)!important;box-shadow:0 0 30px #f9731650!important}
.stSelectbox>div>div,[data-baseweb="select"]{background:#0f0f1a!important;border:1px solid #2a2a3e!important;color:#fff!important;border-radius:10px!important}
.stNumberInput>div>div>input,.stTextInput>div>div>input,.stTextArea>div>div>textarea{background:#0f0f1a!important;border:1px solid #2a2a3e!important;color:#fff!important;border-radius:10px!important;font-family:'Space Grotesk',sans-serif!important}
[data-baseweb="popover"]{background:#0f0f1a!important;border:1px solid #2a2a3e!important}
.stProgress>div>div{background:#1e1e2e!important;border-radius:99px!important}
.stProgress>div>div>div{background:linear-gradient(90deg,#f97316,#fbbf24)!important;border-radius:99px!important}
.stTabs [data-baseweb="tab-list"]{background:#0f0f1a;border-radius:12px;padding:4px;border:1px solid #1e1e2e;gap:4px}
.stTabs [data-baseweb="tab"]{background:transparent;color:#606080;border-radius:8px;font-weight:500}
.stTabs [aria-selected="true"]{background:#f97316!important;color:#000!important;font-weight:700!important}
[data-testid="stForm"]{background:#0a0a14!important;border:1px solid #1e1e2e!important;border-radius:16px!important;padding:1.5rem!important}
hr{border-color:#1e1e2e!important}
::-webkit-scrollbar{width:4px}::-webkit-scrollbar-track{background:#050508}::-webkit-scrollbar-thumb{background:#2a2a3e;border-radius:99px}
[data-testid="metric-container"]{background:#0f0f1a;border:1px solid #1e1e2e;border-radius:12px;padding:16px}
[data-testid="metric-container"] label{color:#606080!important;font-size:12px!important}
[data-testid="metric-container"] [data-testid="stMetricValue"]{color:#fff!important;font-weight:700!important}
.stRadio>div{gap:0!important}
.stRadio>div>label{background:#0f0f1a;border:1px solid #1e1e2e;border-radius:8px;padding:10px 16px;margin-bottom:4px;cursor:pointer;transition:all .15s;font-size:14px}
.stRadio>div>label:hover{border-color:#f97316;color:#fff!important}
</style>
""", unsafe_allow_html=True)

# ── DB ──────────────────────────────────────────────────────────────────────────
DB = "nexxtmarket.db"
def get_db():
    c = sqlite3.connect(DB, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = get_db()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS listings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,description TEXT,price REAL NOT NULL,
        category TEXT DEFAULT 'Other',condition TEXT DEFAULT 'good',location TEXT DEFAULT 'Singapore',
        status TEXT DEFAULT 'active',views INTEGER DEFAULT 0,saves INTEGER DEFAULT 0,
        messages_count INTEGER DEFAULT 0,active_buyers INTEGER DEFAULT 0,
        market_avg_price REAL,ai_deal_score INTEGER DEFAULT 0,ai_title TEXT,ai_description TEXT,
        rank_score REAL DEFAULT 80.0,expires_at TEXT,created_at TEXT DEFAULT(datetime('now')));
    CREATE TABLE IF NOT EXISTS saved_listings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,listing_id INTEGER,session_id TEXT,
        created_at TEXT DEFAULT(datetime('now')));
    """)
    if c.execute("SELECT COUNT(*) FROM listings").fetchone()[0]==0:
        for row in [
            ("Sony WH-1000XM4 Headphones","Excellent noise cancelling, barely used. Box included.",180,"Electronics","excellent",210,91,8),
            ("Trek FX3 City Bike 2022","Perfect urban commuter. Serviced 3 months ago.",420,"Sports","good",480,78,5),
            ("IKEA KALLAX Shelf 4x2","White, minor scuff on side. Self-collect.",65,"Furniture","good",90,62,3),
            ("MacBook Pro M1 16GB 512GB","Space grey, light scratches on base. Charger included.",1050,"Electronics","good",1200,85,6),
            ("Nintendo Switch OLED + 3 Games","Mint, 1 month old. AC, Mario Kart, Zelda.",320,"Gaming","excellent",370,88,7),
            ("Dyson V11 Cordless Vacuum","2 yrs old, filter cleaned. All attachments.",280,"Appliances","good",340,76,4),
            ("Herman Miller Aeron Chair B","Grey, armrest wear. 2020 model. Very comfy.",650,"Furniture","good",800,82,5),
            ("iPhone 14 Pro 256GB Purple","No scratches. Original charger included.",780,"Electronics","excellent",850,90,9),
        ]:
            title,desc,price,cat,cond,mkt,score,buyers = row
            exp=(datetime.now(timezone.utc)+timedelta(hours=24+len(title)%48)).isoformat()
            c.execute("INSERT INTO listings(title,description,price,category,condition,market_avg_price,ai_deal_score,rank_score,expires_at,views,saves,messages_count,active_buyers)VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (title,desc,price,cat,cond,mkt,score,75+score%20,exp,score*2,score//10,score//15,buyers))
    c.commit();c.close()

init_db()

# ── AI ──────────────────────────────────────────────────────────────────────────
def groq_chat(system,user,max_tokens=200):
    key=os.environ.get("GROQ_API_KEY","")
    if not key: return None
    try:
        r=httpx.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
            json={"model":"llama-3.1-8b-instant","messages":[{"role":"system","content":system},{"role":"user","content":user}],"max_tokens":max_tokens,"temperature":0.7},timeout=10)
        return r.json()["choices"][0]["message"]["content"].strip()
    except: return None

# ── Signals ─────────────────────────────────────────────────────────────────────
def price_signal(l):
    p=l["price"];avg=l["market_avg_price"] or p
    diff=((p-avg)/avg*100) if avg else 0
    if diff<=-15: tag,col="Excellent Deal","#4ade80"
    elif diff<=-5: tag,col="Good Deal","#86efac"
    elif diff<=5: tag,col="Fair Price","#94a3b8"
    elif diff<=15: tag,col="Slightly High","#fb923c"
    else: tag,col="Overpriced","#f87171"
    return {"tag":tag,"color":col,"diff":round(diff,1),"avg":avg}

def time_signal(l):
    try:
        exp=datetime.fromisoformat(l["expires_at"].replace("Z","+00:00"))
        h=max(0,(exp-datetime.now(timezone.utc)).total_seconds()/3600)
    except: h=24
    if h<=3: ic,col="🚨","#f87171"
    elif h<=12: ic,col="🔥","#fb923c"
    elif h<=24: ic,col="⏳","#fbbf24"
    else: ic,col="✅","#4ade80"
    return {"hours":round(h,1),"icon":ic,"color":col}

def comp_signal(l):
    b=l["active_buyers"] or 0;m=l["messages_count"] or 0
    if b>=5: lbl,fomo="🔥 Very Hot",95
    elif b>=3: lbl,fomo="⚡ High Demand",80
    elif b==2: lbl,fomo="👀 2 Interested",60
    elif b==1: lbl,fomo="💭 1 Watching",40
    elif m>=1: lbl,fomo="💬 Some Interest",25
    else: lbl,fomo="✨ First Mover",10
    return {"label":lbl,"fomo":fomo}

def cat_icon(title):
    t=title.lower()
    if any(x in t for x in ["head","phone","mac","iphone","laptop","sony"]): return "📱"
    if any(x in t for x in ["bike","sport","gym"]): return "🚲"
    if any(x in t for x in ["chair","shelf","ikea","sofa","table"]): return "🪑"
    if any(x in t for x in ["switch","game","playstation","xbox"]): return "🎮"
    if any(x in t for x in ["dyson","vacuum","applian"]): return "🏠"
    return "📦"

def card(l,ps,ts,cs):
    diff_str=(f"+{ps['diff']}%" if ps['diff']>0 else f"{ps['diff']}%")
    bar=min(100,cs["fomo"])
    desc=(l["description"] or "")[:85]+("…" if len(l["description"] or "")>85 else "")
    icon=cat_icon(l["title"])
    return f"""
<div style="background:linear-gradient(135deg,#0e0e1a,#111120);border:1px solid #1e1e32;border-radius:16px;padding:20px 24px;margin-bottom:12px;position:relative;overflow:hidden">
  <div style="position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,#f97316,#fbbf24,transparent)"></div>
  <div style="display:flex;gap:18px;align-items:flex-start">
    <div style="width:54px;height:54px;border-radius:12px;flex-shrink:0;background:linear-gradient(135deg,#1e1e32,#2a2a42);display:flex;align-items:center;justify-content:center;font-size:26px;border:1px solid #2a2a42">{icon}</div>
    <div style="flex:1;min-width:0">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px">
        <div style="flex:1">
          <div style="font-size:16px;font-weight:700;color:#fff;margin-bottom:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{l["title"]}</div>
          <div style="font-size:13px;color:#60608a;margin-bottom:10px;line-height:1.4">{desc}</div>
          <div style="display:flex;gap:6px;flex-wrap:wrap">
            <span style="font-size:11px;color:#60608a;background:#15152a;padding:3px 10px;border-radius:20px;border:1px solid #2a2a42">📍 {l["location"]}</span>
            <span style="font-size:11px;color:#60608a;background:#15152a;padding:3px 10px;border-radius:20px;border:1px solid #2a2a42">🏷 {l["category"]}</span>
            <span style="font-size:11px;color:#60608a;background:#15152a;padding:3px 10px;border-radius:20px;border:1px solid #2a2a42">⭐ {l["condition"]}</span>
          </div>
        </div>
        <div style="text-align:right;flex-shrink:0">
          <div style="font-size:26px;font-weight:800;color:#fff;font-family:'JetBrains Mono',monospace;line-height:1">${l["price"]:,.0f}</div>
          <div style="font-size:11px;color:#50507a;margin-top:2px">avg ${ps['avg']:,.0f}</div>
          <div style="margin-top:6px"><span style="font-size:12px;font-weight:700;color:{ps['color']};background:{ps['color']}18;padding:3px 10px;border-radius:20px;border:1px solid {ps['color']}40">{ps['tag']} ({diff_str})</span></div>
        </div>
      </div>
      <div style="display:flex;gap:14px;margin-top:14px;padding-top:14px;border-top:1px solid #1a1a2e;flex-wrap:wrap;align-items:center">
        <span style="font-size:13px;color:{ts['color']};font-weight:600">{ts['icon']} {ts['hours']}h left</span>
        <span style="font-size:13px;color:#a0a0c0;font-weight:600">{cs['label']}</span>
        <div style="flex:1;min-width:80px">
          <div style="height:4px;background:#1a1a2e;border-radius:99px;overflow:hidden">
            <div style="height:4px;width:{bar}%;background:linear-gradient(90deg,#f97316,#fbbf24);border-radius:99px"></div>
          </div>
          <div style="font-size:10px;color:#404060;margin-top:2px">FOMO {cs['fomo']}/100</div>
        </div>
        <div style="display:flex;gap:10px;margin-left:auto">
          <span style="font-size:11px;color:#40405e">👁 {l["views"]}</span>
          <span style="font-size:11px;color:#40405e">💾 {l["saves"]}</span>
          <span style="font-size:11px;color:#40405e">💬 {l["messages_count"]}</span>
          <span style="font-size:11px;color:#f9731680">📈 {l["rank_score"]:.0f}</span>
        </div>
      </div>
    </div>
  </div>
</div>"""

# ── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""<div style="padding:0 0 20px">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
        <span style="font-size:28px">⚡</span>
        <span style="font-size:20px;font-weight:800;color:#fff;font-family:'Space Grotesk',sans-serif;letter-spacing:-.5px">NexxtMarket</span>
      </div>
      <div style="font-size:12px;color:#404060;padding-left:38px">AI-Powered Classified Marketplace</div>
    </div>""",unsafe_allow_html=True)
    st.divider()
    page=st.radio("Navigate",["🏠  Browse","➕  Sell","📊  AI Signals","📋  Saved"])
    st.divider()
    has_key=bool(os.environ.get("GROQ_API_KEY"))
    if has_key:
        st.markdown("""<div style="background:#052e1680;border:1px solid #16a34a40;border-radius:10px;padding:10px 14px;font-size:12px;color:#4ade80">✅ Groq AI active</div>""",unsafe_allow_html=True)
    else:
        st.markdown("""<div style="background:#1c120080;border:1px solid #ca8a0440;border-radius:10px;padding:10px 14px;font-size:12px;color:#fbbf24">⚠️ Add <b>GROQ_API_KEY</b> in Secrets for live AI</div>""",unsafe_allow_html=True)
    st.markdown("""<div style="margin-top:20px"><div style="font-size:11px;color:#30304a;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">Free Stack</div>
      <div style="font-size:12px;color:#404060;line-height:2">🤖 Groq Llama-3.1<br>☁️ Streamlit Cloud<br>🗄️ SQLite<br>🐍 Python</div></div>""",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# BROWSE
# ══════════════════════════════════════════════════════════
if "🏠" in page:
    st.markdown("""<div style="padding:10px 0 20px">
      <h1 style="font-size:36px;margin:0;line-height:1">⚡ Live Marketplace</h1>
      <p style="color:#40405e;margin:6px 0 0;font-size:14px">Real-time signals · AI deal scoring · Live competition</p>
    </div>""",unsafe_allow_html=True)

    c1,c2,c3=st.columns([2,2,2])
    with c1: cat=st.selectbox("Category",["All","Electronics","Furniture","Sports","Gaming","Appliances"],label_visibility="collapsed")
    with c2: sort=st.selectbox("Sort",["Rank Score","Price: Low→High","Price: High→Low","Newest"],label_visibility="collapsed")
    with c3: maxp=st.number_input("Max $",min_value=0,value=5000,step=100,label_visibility="collapsed")

    conn=get_db()
    q="SELECT * FROM listings WHERE status='active' AND price<=?";params=[maxp]
    if cat!="All": q+=" AND category=?";params.append(cat)
    sm={"Rank Score":"rank_score DESC","Price: Low→High":"price ASC","Price: High→Low":"price DESC","Newest":"created_at DESC"}
    rows=[dict(r) for r in conn.execute(q+f" ORDER BY {sm[sort]}",params).fetchall()]
    conn.close()

    deals=sum(1 for l in rows if price_signal(l)['diff']<=-5)
    hot=sum(1 for l in rows if l['active_buyers']>=3)
    st.markdown(f"""<div style="display:flex;gap:20px;margin:0 0 20px;padding:14px 20px;background:#0a0a14;border:1px solid #1a1a2e;border-radius:12px">
      <div><span style="font-size:22px;font-weight:800;color:#f97316">{len(rows)}</span><span style="font-size:12px;color:#404060;margin-left:6px">Active</span></div>
      <div style="width:1px;background:#1a1a2e"></div>
      <div><span style="font-size:22px;font-weight:800;color:#4ade80">{deals}</span><span style="font-size:12px;color:#404060;margin-left:6px">Good Deals</span></div>
      <div style="width:1px;background:#1a1a2e"></div>
      <div><span style="font-size:22px;font-weight:800;color:#f87171">{hot}</span><span style="font-size:12px;color:#404060;margin-left:6px">Hot Items</span></div>
    </div>""",unsafe_allow_html=True)

    if not rows:
        st.markdown("""<div style="text-align:center;padding:60px;color:#30304a"><div style="font-size:48px">🔍</div>
          <div style="font-size:18px;margin-top:12px">No listings found</div></div>""",unsafe_allow_html=True)
    else:
        for l in rows:
            ps=price_signal(l);ts=time_signal(l);cs=comp_signal(l)
            st.markdown(card(l,ps,ts,cs),unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# SELL
# ══════════════════════════════════════════════════════════
elif "➕" in page:
    st.markdown("""<h1 style="font-size:36px;margin:0 0 6px">➕ Create Listing</h1>
      <p style="color:#40405e;margin:0 0 24px;font-size:14px">AI optimizes your title, description & price automatically</p>""",unsafe_allow_html=True)

    if "sell_step" not in st.session_state:
        st.session_state.sell_step=1;st.session_state.listing_data={};st.session_state.ai_result=None

    step=st.session_state.sell_step
    steps=["Details","AI Optimize","Publish"]
    cols=st.columns(3)
    for i,(col,label) in enumerate(zip(cols,steps)):
        n=i+1
        if n<step: bg,txt,dot="#16a34a20","#4ade80","✓"
        elif n==step: bg,txt,dot="#f9731620","#f97316",str(n)
        else: bg,txt,dot="#1a1a2e","#30304a",str(n)
        with col:
            st.markdown(f"""<div style="background:{bg};border:1px solid {txt}40;border-radius:12px;padding:12px;text-align:center">
              <span style="font-size:20px;font-weight:800;color:{txt}">{dot}</span>
              <div style="font-size:12px;color:{txt};margin-top:4px">{label}</div></div>""",unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>",unsafe_allow_html=True)

    if step==1:
        with st.form("f1"):
            title=st.text_input("Item Title *",placeholder="e.g. Sony WH-1000XM4 Headphones")
            desc=st.text_area("Description *",placeholder="Condition, what's included, reason for selling…",height=110)
            c1,c2=st.columns(2)
            with c1:
                price=st.number_input("Price (SGD) *",min_value=1.0,value=100.0,step=5.0)
                category=st.selectbox("Category",["Electronics","Furniture","Sports","Gaming","Appliances","Fashion","Books","Other"])
            with c2:
                condition=st.selectbox("Condition",["excellent","good","fair","poor"])
                duration=st.selectbox("Duration",[24,48,72],format_func=lambda x:f"{x} hours")
            location=st.text_input("Location",value="Singapore")
            if st.form_submit_button("Next → AI Optimize →"):
                if not title.strip() or not desc.strip(): st.error("Title and description required.")
                else:
                    st.session_state.listing_data=dict(title=title,description=desc,price=price,category=category,condition=condition,location=location,duration=duration)
                    st.session_state.sell_step=2;st.rerun()

    elif step==2:
        data=st.session_state.listing_data
        if st.session_state.ai_result is None:
            with st.spinner("✨ AI is optimizing your listing…"):
                raw=groq_chat("Return ONLY valid JSON, no extra text.",
                    f'Title:{data["title"]}\nDesc:{data["description"]}\nPrice:${data["price"]}\nCategory:{data["category"]}\nCondition:{data["condition"]}\nReturn:{{"optimized_title":"...","optimized_description":"...","suggested_price":0,"deal_score":0,"key_improvements":["..."]}}',400)
                result=None
                if raw:
                    try:
                        m=re.search(r'\{.*\}',raw,re.DOTALL)
                        result=json.loads(m.group()) if m else None
                    except: pass
                if not result:
                    result={"optimized_title":data['title'].title(),"optimized_description":data['description'],"suggested_price":data['price'],"deal_score":70,"key_improvements":["Add more photos","Mention original price","State reason for selling"]}
            st.session_state.ai_result=result

        result=st.session_state.ai_result;score=result.get("deal_score",70)
        sc="#4ade80" if score>=70 else "#fbbf24" if score>=50 else "#f87171"
        st.markdown(f"""<div style="background:#0a0a14;border:1px solid #1e1e2e;border-radius:14px;padding:20px;margin-bottom:20px;display:flex;align-items:center;gap:20px">
          <div style="width:72px;height:72px;border-radius:50%;background:conic-gradient({sc} {score*3.6}deg,#1e1e2e 0deg);display:flex;align-items:center;justify-content:center;flex-shrink:0">
            <div style="width:58px;height:58px;border-radius:50%;background:#0a0a14;display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:800;color:{sc}">{score}</div>
          </div>
          <div><div style="font-size:18px;font-weight:700;color:#fff">AI Deal Score</div>
          <div style="font-size:13px;color:#40405e;margin-top:2px">{"Strong listing" if score>=70 else "Good listing — a few improvements could help" if score>=50 else "Consider revising"}</div></div>
        </div>""",unsafe_allow_html=True)

        c1,c2=st.columns(2)
        with c1:
            st.markdown("**Original**")
            st.markdown(f"""<div style="background:#0f0f1a;border:1px solid #1e1e2e;border-radius:12px;padding:14px;font-size:13px;color:#60608a">
              <b style="color:#a0a0c0">{data['title']}</b><br><br>{data['description'][:200]}</div>""",unsafe_allow_html=True)
        with c2:
            st.markdown("**✨ AI Optimized**")
            st.markdown(f"""<div style="background:#0f1a0f;border:1px solid #16a34a40;border-radius:12px;padding:14px;font-size:13px;color:#a0c0a0">
              <b style="color:#4ade80">{result.get('optimized_title',data['title'])}</b><br><br>{result.get('optimized_description',data['description'])[:200]}</div>""",unsafe_allow_html=True)

        for tip in result.get("key_improvements",[]):
            st.markdown(f"""<div style="background:#0f0f1a;border-left:3px solid #f97316;border-radius:0 8px 8px 0;padding:8px 14px;margin:4px 0;font-size:13px;color:#a0a0c0">💡 {tip}</div>""",unsafe_allow_html=True)

        use_ai=st.toggle("Use AI-optimized version",value=True)
        st.session_state.listing_data["use_ai"]=use_ai;st.session_state.listing_data["ai_result"]=result
        c1,c2=st.columns(2)
        with c1:
            if st.button("← Back"): st.session_state.sell_step=1;st.rerun()
        with c2:
            if st.button("Preview & Publish →"): st.session_state.sell_step=3;st.rerun()

    elif step==3:
        data=st.session_state.listing_data;result=data.get("ai_result",{});use_ai=data.get("use_ai",False)
        ft=result.get("optimized_title",data['title']) if use_ai else data['title']
        fd=result.get("optimized_description",data['description']) if use_ai else data['description']
        st.markdown(f"""<div style="background:#0e0e1a;border:1px solid #2a2a42;border-radius:16px;padding:24px;position:relative;overflow:hidden;margin-bottom:20px">
          <div style="position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,#f97316,#fbbf24,transparent)"></div>
          <h2 style="margin:0 0 8px;font-size:22px;color:#fff">{ft}</h2>
          <span style="font-size:28px;font-weight:800;color:#fff;font-family:'JetBrains Mono',monospace">${data['price']:,.0f}</span>
          <span style="font-size:12px;color:#60608a;margin-left:12px">📍 {data['location']} · 🏷 {data['category']} · ⭐ {data['condition']} · ⏰ {data['duration']}h</span>
          <p style="font-size:14px;color:#80809a;line-height:1.6;margin:14px 0 0">{fd}</p>
        </div>""",unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1:
            if st.button("← Back"): st.session_state.sell_step=2;st.rerun()
        with c2:
            if st.button("🚀 Publish Listing"):
                conn=get_db();exp=(datetime.now(timezone.utc)+timedelta(hours=data['duration'])).isoformat()
                row=conn.execute("SELECT AVG(price) FROM listings WHERE category=? AND status='active'",(data['category'],)).fetchone()
                mkt=row[0] if row[0] else data['price']
                conn.execute("INSERT INTO listings(title,description,price,category,condition,location,market_avg_price,ai_deal_score,rank_score,expires_at)VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (ft,fd,data['price'],data['category'],data['condition'],data['location'],mkt,result.get("deal_score",70),85.0,exp))
                conn.commit();conn.close()
                st.success("✅ Published!");st.balloons()
                st.session_state.sell_step=1;st.session_state.ai_result=None;st.session_state.listing_data={}

# ══════════════════════════════════════════════════════════
# AI SIGNALS
# ══════════════════════════════════════════════════════════
elif "📊" in page:
    st.markdown("""<h1 style="font-size:36px;margin:0 0 6px">📊 AI Signal Engine</h1>
      <p style="color:#40405e;margin:0 0 24px;font-size:14px">See all engagement signals fire in real time</p>""",unsafe_allow_html=True)

    with st.form("sig"):
        c1,c2=st.columns(2)
        with c1:
            t=st.text_input("Title","Sony WH-1000XM4 Headphones")
            p=st.number_input("Your price ($)",value=180.0)
            avg=st.number_input("Market average ($)",value=210.0)
        with c2:
            views=st.number_input("Views last hour",value=15,step=1)
            buyers=st.number_input("Active buyers",value=3,step=1)
            hrs=st.slider("Hours until expiry",1,72,20)
        go=st.form_submit_button("⚡ Generate All Signals")

    if go:
        mock={"title":t,"price":p,"market_avg_price":avg,"views_last_hour":views,"saves_count":8,
              "messages_count":buyers,"active_buyers":buyers,"description":"Demo","images":[],
              "expires_at":(datetime.now(timezone.utc)+timedelta(hours=hrs)).isoformat(),"is_boosted":False}
        ps=price_signal(mock);ts=time_signal(mock);cs=comp_signal(mock)
        diff_str=f"+{ps['diff']}%" if ps['diff']>0 else f"{ps['diff']}%"

        sigs=[
            ("💰","Price Intelligence",ps['tag'],f"{diff_str} vs mkt avg ${avg:,.0f}",ps['color']),
            ("⏱","Time Pressure",f"{ts['icon']} {'Critical' if hrs<=3 else 'High' if hrs<=12 else 'Low'}",f"{hrs}h remaining",ts['color']),
            ("👥","Competition",cs['label'],f"FOMO: {cs['fomo']}/100","#a78bfa"),
            ("👁","Social Proof",f"{views} views/hr","Active interest","#60a5fa"),
        ]
        c1,c2=st.columns(2)
        for i,(icon,label,val,sub,col) in enumerate(sigs):
            with (c1 if i%2==0 else c2):
                st.markdown(f"""<div style="background:#0e0e1a;border:1px solid {col}30;border-radius:14px;padding:18px;margin-bottom:12px">
                  <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
                    <span style="font-size:22px">{icon}</span>
                    <span style="font-size:11px;color:#40405e;text-transform:uppercase;letter-spacing:1px">{label}</span>
                  </div>
                  <div style="font-size:20px;font-weight:700;color:{col}">{val}</div>
                  <div style="font-size:12px;color:#40405e;margin-top:4px">{sub}</div>
                </div>""",unsafe_allow_html=True)

        st.markdown(f"""<div style="background:#0e0e1a;border:1px solid #2a2a42;border-radius:14px;padding:18px;margin-bottom:12px">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
            <span style="font-size:14px;font-weight:600;color:#fff">🔥 Overall FOMO Score</span>
            <span style="font-size:24px;font-weight:800;color:#f97316">{cs['fomo']}/100</span>
          </div>
          <div style="height:8px;background:#1a1a2e;border-radius:99px;overflow:hidden">
            <div style="height:8px;width:{cs['fomo']}%;background:linear-gradient(90deg,#f97316,#fbbf24);border-radius:99px"></div>
          </div>
        </div>""",unsafe_allow_html=True)

        st.markdown("**🤖 AI Insight (Groq)**")
        with st.spinner("Generating…"):
            insight=groq_chat("Marketplace analyst. ONE sharp insight, max 2 sentences, specific numbers.",
                f"Item:{t}, Price:${p}, Mkt avg:${avg}, {buyers} buyers, {hrs}h left, {views} views/hr")
        if insight:
            st.markdown(f"""<div style="background:#0c1a2e;border:1px solid #2563eb40;border-left:3px solid #3b82f6;border-radius:0 12px 12px 0;padding:14px 18px;font-size:14px;color:#93c5fd;line-height:1.6">{insight}</div>""",unsafe_allow_html=True)
        else:
            st.markdown("""<div style="background:#1c120080;border:1px solid #ca8a0440;border-radius:12px;padding:12px 16px;font-size:13px;color:#fbbf24">Add GROQ_API_KEY in Streamlit Secrets → App settings → Secrets to enable AI</div>""",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# SAVED
# ══════════════════════════════════════════════════════════
elif "📋" in page:
    st.markdown("""<h1 style="font-size:36px;margin:0 0 6px">📋 Saved Listings</h1>
      <p style="color:#40405e;margin:0 0 24px;font-size:14px">Listings you've bookmarked this session</p>""",unsafe_allow_html=True)
    if "session_id" not in st.session_state: st.session_state.session_id=str(uuid.uuid4())
    conn=get_db()
    saved=[dict(r) for r in conn.execute("SELECT l.* FROM listings l JOIN saved_listings sl ON l.id=sl.listing_id WHERE sl.session_id=? ORDER BY sl.created_at DESC",(st.session_state.session_id,)).fetchall()]
    conn.close()
    if not saved:
        st.markdown("""<div style="text-align:center;padding:60px;color:#30304a"><div style="font-size:48px">💾</div>
          <div style="font-size:18px;margin-top:12px">No saved listings yet</div>
          <div style="font-size:14px;margin-top:6px">Browse the marketplace to find listings you like</div></div>""",unsafe_allow_html=True)
    else:
        for l in saved:
            ps=price_signal(l);ts=time_signal(l);cs=comp_signal(l)
            st.markdown(card(l,ps,ts,cs),unsafe_allow_html=True)
