import streamlit as st
import pandas as pd
import asyncio
import json
import yfinance as yf
from twikit import Client
from streamlit_autorefresh import st_autorefresh
import os
import streamlit.components.v1 as components
import requests
import random
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(
    layout="wide",
    page_title="YN_COMMAND TERMINAL",
    initial_sidebar_state="collapsed"
)

# Auto-refresh every 60 seconds
st_autorefresh(interval=60000, key="refresh")

# ---------------- J.A.R.V.I.S. HOLOGRAPHIC CSS ----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;500;700&display=swap');

    /* CORE BACKGROUND (ARC REACTOR VIBE) */
    .stApp {
        background: radial-gradient(circle at 50% 10%, #1a2a3a 0%, #000000 90%);
        background-attachment: fixed;
        color: #e0f7fa;
        font-family: 'Rajdhani', sans-serif;
    }
    
    [data-testid="stHeader"] { display: none; }
    .block-container { padding-top: 0rem; padding-bottom: 5rem; }

    /* HOLOGRAPHIC PANELS (GLASSMORPHISM) */
    .section {
        background: rgba(10, 20, 30, 0.6);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 243, 255, 0.2);
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.05);
        border-radius: 4px;
        padding: 15px;
        margin-bottom: 20px;
        position: relative;
        overflow: hidden;
    }
    
    /* CORNER ACCENTS */
    .section::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 10px; height: 10px;
        border-top: 2px solid #00f3ff;
        border-left: 2px solid #00f3ff;
    }
    .section::after {
        content: '';
        position: absolute;
        bottom: 0; right: 0;
        width: 10px; height: 10px;
        border-bottom: 2px solid #00f3ff;
        border-right: 2px solid #00f3ff;
    }

    /* TYPOGRAPHY */
    .title-glitch {
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        font-size: 22px;
        color: #fff;
        text-shadow: 0 0 10px rgba(0, 243, 255, 0.8);
        text-transform: uppercase;
        letter-spacing: 3px;
        margin-bottom: 15px;
        border-bottom: 1px solid rgba(0, 243, 255, 0.3);
        padding-bottom: 5px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* SYSTEM PULSE ANIMATION */
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(0, 243, 255, 0.7); }
        70% { box-shadow: 0 0 0 5px rgba(0, 243, 255, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 243, 255, 0); }
    }
    
    .live-dot {
        height: 8px; width: 8px;
        background-color: #00f3ff;
        border-radius: 50%;
        display: inline-block;
        animation: pulse 2s infinite;
        margin-right: 8px;
    }

    /* HUD METRIC CARDS */
    .metric-card {
        background: rgba(0, 243, 255, 0.05);
        border: 1px solid rgba(0, 243, 255, 0.1);
        border-radius: 4px;
        padding: 12px;
        text-align: center;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        background: rgba(0, 243, 255, 0.1);
        border-color: #00f3ff;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.2);
    }
    .metric-label { font-family: 'Orbitron', sans-serif; font-size: 9px; color: #00f3ff; letter-spacing: 1px; opacity: 0.8; }
    .metric-val { font-family: 'Rajdhani', sans-serif; font-size: 20px; font-weight: 700; color: #fff; margin: 2px 0; text-shadow: 0 0 5px rgba(255,255,255,0.5); }
    
    .pos { color: #00ff41; text-shadow: 0 0 8px rgba(0, 255, 65, 0.4); }
    .neg { color: #ff3b3b; text-shadow: 0 0 8px rgba(255, 59, 59, 0.4); }

    /* DATA FEED UI */
    .tweet-card {
        background: rgba(255, 255, 255, 0.03);
        border-left: 2px solid #2f3336;
        padding: 12px;
        margin-bottom: 10px;
        transition: border-left 0.2s;
    }
    .tweet-card:hover { border-left: 2px solid #00f3ff; background: rgba(0, 243, 255, 0.02); }
    
    .avatar { 
        width: 38px; height: 38px; border-radius: 50%; 
        background: linear-gradient(45deg, #111, #333); 
        border: 1px solid #444;
        display: flex; align-items: center; justify-content: center; 
        font-family: 'Orbitron'; color: #00f3ff; margin-right: 12px;
        box-shadow: 0 0 10px rgba(0,0,0,0.5);
    }
    .avatar img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }
    
    .name { font-family: 'Rajdhani', sans-serif; font-weight: 700; color: #e0f7fa; font-size: 16px; }
    .handle { color: #00bcd4; font-size: 13px; opacity: 0.7; }
    .tweet-text { color: #cfd8dc; font-size: 14px; line-height: 1.5; font-weight: 400; }
    
    /* RANKER BARS */
    .rank-row { display: flex; align-items: center; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
    .rank-bar-bg { flex-grow: 1; height: 4px; background: rgba(255,255,255,0.1); margin: 0 12px; border-radius: 2px; }
    .rank-bar-fill { height: 100%; border-radius: 2px; box-shadow: 0 0 8px currentColor; }
</style>
""", unsafe_allow_html=True)

# ---------------- ADS (TOP) ----------------
components.html(
    """
    <div style="display:flex; justify-content:center; margin:10px 0;">
        <script>
          atOptions = {
            'key' : 'b70ce887becced7c033579163064d6b4',
            'format' : 'iframe',
            'height' : 60,
            'width' : 468,
            'params' : {}
          };
        </script>
        <script src="https://www.highperformanceformat.com/b70ce887becced7c033579163064d6b4/invoke.js"></script>
    </div>
    """,
    height=70,
)

# ---------------- HEADER ----------------
st.markdown("""
<div style="text-align:center; margin-bottom:30px;">
    <h1 style="font-family:'Orbitron'; font-weight:900; font-size:36px; color:#fff; text-shadow:0 0 20px #00f3ff; margin:0;">GLOBAL SURVEILLANCE</h1>
    <div style="font-family:'Rajdhani'; color:#00f3ff; font-size:14px; letter-spacing:4px; margin-top:5px;">
        <span class="live-dot"></span>SYSTEM ONLINE // REAL-TIME FEED ACTIVE
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("### // TARGET SELECTOR")
    ticker = st.text_input("SYMBOL", "NVDA").upper()
    st.caption("J.A.R.V.I.S. PROTOCOL ENGAGED")

# ---------------- DATA ENGINE ----------------
@st.cache_data(ttl=60)
def fetch_global_scan():
    symbols = {
        "ES_FUT": "ES=F", "NQ_FUT": "NQ=F", "10Y_YIELD": "^TNX", 
        "VIX": "^VIX", "DXY": "DX-Y.NYB", "OIL": "CL=F", 
        "GOLD": "GC=F", "EURO": "EURUSD=X", "BTC": "BTC-USD", "ETH": "ETH-USD"
    }
    data = {}
    try:
        tickers_list = list(symbols.values())
        df = yf.download(tickers_list, period="5d", interval="1d", progress=False)
        closes = df['Close'] if isinstance(df.columns, pd.MultiIndex) else df
        
        for k, v in symbols.items():
            if v in closes.columns:
                series = closes[v].dropna()
                curr = series.iloc[-1]
                prev = series.iloc[-2]
                chg = ((curr - prev) / prev) * 100
                fmt = f"{curr:,.0f}" if "BTC" in k or "ETH" in k else f"{curr:,.2f}"
                data[k] = {"price": fmt, "chg": chg}
            else: data[k] = {"price": "N/A", "chg": 0.0}
    except:
        data = {k: {"price": "OFFLINE", "chg": 0.0} for k in symbols}
    return data

scan_data = fetch_global_scan()

# ---------------- HUD GRID ----------------
keys = list(scan_data.keys())
c1, c2, c3, c4, c5 = st.columns(5)
c6, c7, c8, c9, c10 = st.columns(5)

for col, k in zip([c1,c2,c3,c4,c5,c6,c7,c8,c9,c10], keys):
    item = scan_data[k]
    color_cls = "pos" if item['chg'] >= 0 else "neg"
    col.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{k}</div>
        <div class="metric-val">{item['price']}</div>
        <div class="{color_cls}" style="font-family:'Rajdhani'; font-weight:bold; font-size:14px;">{item['chg']:+.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------- MAIN DASHBOARD ----------------
col_main, col_side = st.columns([2, 1])

# --- LEFT: CHART & RANKER ---
with col_main:
    # CHART
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown(f'''
    <div class="title-glitch">
        <span>TARGET SCAN // {ticker}</span>
        <span style="font-size:12px; color:#555;">LIVE FEED</span>
    </div>
    ''', unsafe_allow_html=True)
    
    html_chart = f"""
    <div class="tradingview-widget-container" style="height:550px;width:100%">
      <div id="tradingview_widget" style="height:100%;width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
      "autosize": true, "symbol": "{ticker}", "interval": "15", "timezone": "Etc/UTC",
      "theme": "dark", "style": "1", "locale": "en", "enable_publishing": false,
      "backgroundColor": "rgba(10, 20, 30, 1)", "gridColor": "rgba(0, 243, 255, 0.05)",
      "hide_top_toolbar": false, "save_image": false,
      "studies": ["RSI@tv-basicstudies", "MACD@tv-basicstudies", "Volume@tv-basicstudies"],
      "container_id": "tradingview_widget"
      }});
      </script>
    </div>
    """
    components.html(html_chart, height=560)
    st.markdown('</div>', unsafe_allow_html=True)

    # RANKER
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="title-glitch">S&P 500 MOMENTUM</div>', unsafe_allow_html=True)
    
    @st.cache_data(ttl=300)
    def get_alpha_ranks():
        targets = ["NVDA", "TSLA", "AMD", "META", "AMZN", "MSFT", "GOOGL", "AAPL", "NFLX", "PLTR", "COIN", "MSTR", "SMCI", "AVGO", "COST"]
        data = yf.download(targets, period="5d", interval="1d", progress=False)['Close']
        if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(1)
        
        ranks = []
        for t in targets:
            try:
                chg = ((data[t].iloc[-1] - data[t].iloc[-2])/data[t].iloc[-2])*100
                vol = data[t].pct_change().std() * 100
                ranks.append({"sym": t, "chg": chg, "vol": vol, "score": abs(chg)*vol})
            except: continue
        return sorted(ranks, key=lambda x: x['score'], reverse=True)

    ranks = get_alpha_ranks()
    
    for i, r in enumerate(ranks[:10]):
        bar_w = min(abs(r['chg']) * 20, 100)
        fill_color = "#00ff41" if r['chg'] > 0 else "#ff3b3b"
        st.markdown(f"""
        <div class="rank-row">
            <div style="font-family:'Orbitron'; color:#555; width:30px; font-size:10px;">0{i+1}</div>
            <div style="font-family:'Rajdhani'; font-weight:bold; color:#fff; width:60px; font-size:16px;">{r['sym']}</div>
            <div class="rank-bar-bg"><div class="rank-bar-fill" style="width:{bar_w}%; background:{fill_color}; color:{fill_color};"></div></div>
            <div style="width:70px; text-align:right; font-family:'Rajdhani'; font-weight:bold; color:{fill_color};">{r['chg']:+.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- RIGHT: INTEL FEED ---
with col_side:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="title-glitch">INTEL STREAM</div>', unsafe_allow_html=True)
    
    # FETCH LOGIC (TRIPLE REDUNDANCY)
    def fetch_yahoo_news(symbol):
        try:
            news = yf.Ticker(symbol).news
            tweets = []
            handles = ["@MarketWire", "@Bloomberg", "@Reuters", "@CNBC", "@WSJ"]
            for i, n in enumerate(news[:10]):
                tweets.append({
                    "user": {"name": handles[i%5], "screen_name": handles[i%5].replace("@","")},
                    "text": n['title'],
                    "source": "News Wire"
                })
            return tweets
        except: return []

    def fetch_stocktwits(symbol):
        url = f"https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json"
        try:
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            if r.status_code == 200:
                data = r.json()
                tweets = []
                for msg in data['messages'][:10]:
                    tweets.append({
                        "user": {"name": msg['user']['username'], "screen_name": msg['user']['username'], "profile_image_url_https": msg['user']['avatar_url']},
                        "text": msg['body'],
                        "source": "Stocktwits"
                    })
                return tweets
            return []
        except: return []

    async def get_feed():
        try:
            if os.path.exists("cookies.json"):
                client = Client("en-US")
                with open("cookies.json", "r") as f:
                    raw = json.load(f)
                cookies = {c["name"]: c["value"] for c in raw} if isinstance(raw, list) else raw
                client.set_cookies(cookies)
                return await client.search_tweet(f"${ticker} filter:verified", "Latest", count=10)
        except: pass
        
        st_data = fetch_stocktwits(ticker)
        if st_data: return st_data
        
        return fetch_yahoo_news(ticker)

    # EXECUTE
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        feed_data = loop.run_until_complete(get_feed())
        
        for item in feed_data:
            if isinstance(item, dict):
                name = item['user']['name']
                handle = item['user']['screen_name']
                text = item['text']
                img = item['user'].get('profile_image_url_https', '')
            else:
                name = item.user.name
                handle = item.user.screen_name
                text = item.text
                img = ""

            avatar_html = f'<img src="{img}">' if img else f'{name[0]}'

            st.markdown(f"""
            <div class="tweet-card">
                <div class="tweet-header">
                    <div class="avatar">{avatar_html}</div>
                    <div style="margin-left:5px;">
                        <div class="name-row">
                            <div class="name">{name}</div>
                            <div class="verified">☑</div>
                        </div>
                        <div class="handle">@{handle}</div>
                    </div>
                </div>
                <div class="tweet-text">{text}</div>
            </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"FEED SYSTEM ERROR: {e}")

    # VERTICAL AD
    components.html(
        """
        <div style="display:flex; justify-content:center; margin-top:20px;">
            <script>
              atOptions = {
                'key' : '914d023d74077cbb3c33063328e01c7f',
                'format' : 'iframe',
                'height' : 300,
                'width' : 160,
                'params' : {}
              };
            </script>
            <script src="https://www.highperformanceformat.com/914d023d74077cbb3c33063328e01c7f/invoke.js"></script>
        </div>
        """,
        height=320,
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- BOTTOM AD ----------------
components.html(
    """
    <div style="text-align:center;">
        <script async="async" data-cfasync="false" src="https://pl28519010.effectivegatecpm.com/7f2ad764010d514cdee2fdac0b042524/invoke.js"></script>
        <div id="container-7f2ad764010d514cdee2fdac0b042524"></div>
    </div>
    """,
    height=100,
)
