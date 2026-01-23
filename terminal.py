import streamlit as st
import pandas as pd
import asyncio
import json
import yfinance as yf
from twikit import Client
from streamlit_autorefresh import st_autorefresh
import os
import streamlit.components.v1 as components
import requests # Needed for Stocktwits Fallback

# ---------------- CONFIG ----------------
st.set_page_config(
    layout="wide",
    page_title="YN_COMMAND TERMINAL",
    initial_sidebar_state="collapsed"
)

# Auto-refresh every 60 seconds
st_autorefresh(interval=60000, key="refresh")

# ---------------- STYLE ----------------
st.markdown("""
<style>
    /* CORE THEME */
    html, body, [class*="css"] {
        background-color: #000000;
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }
    
    [data-testid="stHeader"] { display: none; }
    .block-container { padding-top: 0rem; padding-bottom: 5rem; padding-left: 1rem; padding-right: 1rem; }
    
    /* SECTIONS */
    .section {
        background: #050505;
        border: 1px solid #222;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    }
    
    /* TITLES */
    .title-glitch {
        font-family: 'Courier New', monospace;
        font-weight: 900;
        font-size: 20px;
        color: #fff;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 15px;
        border-left: 4px solid #00ffff;
        padding-left: 10px;
    }
    
    /* METRICS */
    .metric-card {
        background: linear-gradient(145deg, #0a0a0a, #0f0f0f);
        border: 1px solid #333;
        border-radius: 6px;
        padding: 10px;
        text-align: center;
    }
    .metric-val { font-size: 18px; font-weight: bold; color: #fff; margin: 5px 0; }
    .pos { color: #00ff41; }
    .neg { color: #ff3b3b; }
    
    /* FEED CARDS */
    .tweet-card {
        background: #000;
        border: 1px solid #2f3336;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 12px;
    }
    .tweet-header { display: flex; align-items: center; margin-bottom: 8px; }
    .avatar { 
        width: 36px; height: 36px; border-radius: 50%; background: #333; 
        display: flex; align-items: center; justify-content: center; font-weight: bold; color: #fff; margin-right: 10px;
        overflow: hidden;
    }
    .avatar img { width: 100%; height: 100%; object-fit: cover; }
    .name { font-weight: bold; color: #e7e9ea; font-size: 14px; }
    .handle { color: #71767b; font-size: 13px; margin-left: 5px;}
    .tweet-text { color: #e7e9ea; font-size: 14px; line-height: 1.5; white-space: pre-wrap; }
    
    /* RANKER */
    .rank-card {
        display: flex; justify-content: space-between; align-items: center;
        background: #0a0a0a; border-bottom: 1px solid #222; padding: 10px;
    }
    .rank-bar { height: 4px; border-radius: 2px; flex-grow: 1; margin: 0 10px; background: #222; }
    .rank-fill { height: 100%; border-radius: 2px; }
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
<div style="text-align:center; margin-bottom:20px;">
    <h1 style="color:#fff; font-family:'Courier New'; font-weight:900; letter-spacing:4px; text-shadow:0 0 20px rgba(0,255,255,0.5);">GLOBAL SURVEILLANCE</h1>
    <div style="color:#00ffff; font-size:12px; letter-spacing:2px;">LIVE MARKET INTELLIGENCE SYSTEM</div>
</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("### // TARGET SELECTOR")
    ticker = st.text_input("SYMBOL", "NVDA").upper()
    st.caption("SYSTEM: ONLINE")

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
        <div style="font-size:10px; color:#666;">{k}</div>
        <div class="metric-val">{item['price']}</div>
        <div class="{color_cls}" style="font-size:12px;">{item['chg']:+.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------- MAIN DASHBOARD ----------------
col_main, col_side = st.columns([2, 1])

# --- LEFT: CHART & RANKER ---
with col_main:
    # CHART
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown(f'<div class="title-glitch">PRICE ACTION // {ticker}</div>', unsafe_allow_html=True)
    
    html_chart = f"""
    <div class="tradingview-widget-container" style="height:550px;width:100%">
      <div id="tradingview_widget" style="height:100%;width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
      "autosize": true, "symbol": "{ticker}", "interval": "15", "timezone": "Etc/UTC",
      "theme": "dark", "style": "1", "locale": "en", "enable_publishing": false,
      "backgroundColor": "rgba(0, 0, 0, 1)", "gridColor": "rgba(20, 20, 20, 1)",
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
    st.markdown('<div class="title-glitch">S&P 500 MOMENTUM RANKER</div>', unsafe_allow_html=True)
    
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
        <div class="rank-card">
            <div style="color:#555; width:30px;">#{i+1}</div>
            <div style="font-weight:bold; color:#fff; width:60px;">{r['sym']}</div>
            <div class="rank-bar"><div class="rank-fill" style="width:{bar_w}%; background:{fill_color}; box-shadow: 0 0 10px {fill_color};"></div></div>
            <div style="width:60px; text-align:right; font-family:'Roboto Mono'; color:{fill_color};">{r['chg']:+.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- RIGHT: REAL INTEL FEED (DUAL-CORE) ---
with col_side:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="title-glitch">LIVE INTEL FEED</div>', unsafe_allow_html=True)
    
    # 1. STOCKTWITS FALLBACK (REAL HUMANS)
    def fetch_stocktwits(symbol):
        url = f"https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json"
        try:
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            if r.status_code == 200:
                data = r.json()
                tweets = []
                for msg in data['messages'][:10]:
                    tweets.append({
                        "id": msg['id'],
                        "text": msg['body'],
                        "user": {
                            "name": msg['user']['username'],
                            "screen_name": msg['user']['username'], # Stocktwits uses username as handle
                            "profile_image_url_https": msg['user']['avatar_url']
                        },
                        "source": "Stocktwits"
                    })
                return tweets
            return []
        except: return []

    # 2. TWIKIT PRIMARY
    async def get_feed():
        # Try X first
        try:
            if os.path.exists("cookies.json"):
                client = Client("en-US")
                with open("cookies.json", "r") as f:
                    raw = json.load(f)
                cookies = {c["name"]: c["value"] for c in raw} if isinstance(raw, list) else raw
                client.set_cookies(cookies)
                return await client.search_tweet(f"${ticker} filter:verified", "Latest", count=10)
        except Exception as e:
            pass # Fail silently to fallback
            
        # Fallback to Stocktwits if X fails
        return fetch_stocktwits(ticker)

    try:
        # Run Async Loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        feed_data = loop.run_until_complete(get_feed())
        
        if not feed_data:
            st.markdown("<div style='color:#555;'>NO SIGNAL DETECTED</div>", unsafe_allow_html=True)
        else:
            for item in feed_data:
                # Normalize Data
                if isinstance(item, dict):
                    # Stocktwits format
                    name = item['user']['name']
                    handle = item['user']['screen_name']
                    text = item['text']
                    img_url = item['user'].get('profile_image_url_https', '')
                    source = item.get('source', 'X')
                else:
                    # Twikit Object
                    name = item.user.name
                    handle = item.user.screen_name
                    text = item.text
                    img_url = "" # Twikit avatar fetching can be complex, default blank
                    source = "X"

                # Avatar Logic
                if img_url:
                    avatar_html = f'<img src="{img_url}">'
                else:
                    initial = name[0] if name else "?"
                    avatar_html = initial

                st.markdown(f"""
                <div class="tweet-card">
                    <div class="tweet-header">
                        <div class="avatar">{avatar_html}</div>
                        <div style="margin-left:10px;">
                            <div class="name">{name} <span style="color:#1d9bf0; font-size:10px;">{source}</span></div>
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
