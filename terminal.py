import streamlit as st
import pandas as pd
import asyncio
import json
import yfinance as yf
from twikit import Client
from streamlit_autorefresh import st_autorefresh
import os
import streamlit.components.v1 as components

# ---------------- CONFIG ----------------
st.set_page_config(
    layout="wide",
    page_title="YN_COMMAND TERMINAL",
    initial_sidebar_state="collapsed"
)

# Auto-refresh every 60 seconds
st_autorefresh(interval=60000, key="refresh")

# ---------------- HYPER-VISUAL CSS ----------------
st.markdown("""
<style>
    /* CORE THEME */
    html, body, [class*="css"] {
        background-color: #000000;
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }
    
    /* HIDE STREAMLIT UI */
    [data-testid="stHeader"] { display: none; }
    .block-container { padding-top: 0rem; padding-bottom: 5rem; padding-left: 1rem; padding-right: 1rem; }
    
    /* NEON BORDERS & GLOWS */
    .section {
        background: #050505;
        border: 1px solid #222;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        transition: all 0.3s ease;
    }
    .section:hover {
        border-color: #00ffff;
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.1);
    }
    
    /* TYPOGRAPHY */
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
    
    /* METRIC CARDS */
    .metric-card {
        background: linear-gradient(145deg, #0a0a0a, #0f0f0f);
        border: 1px solid #333;
        border-radius: 6px;
        padding: 10px;
        text-align: center;
    }
    .metric-label { font-size: 10px; color: #666; letter-spacing: 1px; }
    .metric-val { font-size: 18px; font-weight: bold; color: #fff; margin: 5px 0; }
    .pos { color: #00ff41; text-shadow: 0 0 5px rgba(0, 255, 65, 0.3); }
    .neg { color: #ff3b3b; text-shadow: 0 0 5px rgba(255, 59, 59, 0.3); }
    
    /* TWITTER FEED CARDS */
    .tweet-card {
        background: #000;
        border: 1px solid #2f3336;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 12px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .tweet-header { display: flex; align-items: center; margin-bottom: 8px; }
    .avatar { 
        width: 36px; height: 36px; border-radius: 50%; background: #333; 
        display: flex; align-items: center; justify-content: center; font-weight: bold; color: #fff; margin-right: 10px;
    }
    .user-info { display: flex; flex-direction: column; line-height: 1.2; }
    .name { font-weight: bold; color: #e7e9ea; font-size: 14px; }
    .handle { color: #71767b; font-size: 13px; }
    .verified { color: #1d9bf0; margin-left: 4px; }
    .tweet-text { color: #e7e9ea; font-size: 14px; line-height: 1.5; white-space: pre-wrap; }
    .tweet-footer { margin-top: 10px; border-top: 1px solid #2f3336; padding-top: 8px; display: flex; justify-content: space-between; color: #71767b; font-size: 12px; }
    
    /* RANKER HEATMAP */
    .rank-card {
        display: flex; justify-content: space-between; align-items: center;
        background: #0a0a0a; border-bottom: 1px solid #222; padding: 10px;
        transition: background 0.2s;
    }
    .rank-card:hover { background: #111; }
    .rank-num { font-size: 12px; color: #555; width: 30px; }
    .rank-sym { font-weight: bold; color: #fff; width: 60px; }
    .rank-bar { height: 4px; border-radius: 2px; flex-grow: 1; margin: 0 10px; background: #222; }
    .rank-fill { height: 100%; border-radius: 2px; }
    
    /* LOAD MORE BUTTON */
    .load-btn {
        width: 100%; background: #1d9bf0; color: white; border: none; padding: 10px;
        border-radius: 20px; font-weight: bold; cursor: pointer; text-align: center; margin-top: 10px;
    }
    .load-btn:hover { background: #1a8cd8; }
</style>
""", unsafe_allow_html=True)

# ---------------- TOP AD BANNER ----------------
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
        <div class="metric-label">{k}</div>
        <div class="metric-val">{item['price']}</div>
        <div class="{color_cls}" style="font-size:12px;">{item['chg']:+.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------- MAIN DASHBOARD ----------------
col_main, col_side = st.columns([2, 1])

# --- LEFT COLUMN: CHART & RANKER ---
with col_main:
    # 1. TRADINGVIEW CHART (PRO)
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

    # 2. S&P 500 ALPHA RANKER (VISUAL)
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
    
    # Render Heatmap Rows
    for i, r in enumerate(ranks[:10]):
        bar_w = min(abs(r['chg']) * 20, 100) # Visual scaling
        fill_color = "#00ff41" if r['chg'] > 0 else "#ff3b3b"
        st.markdown(f"""
        <div class="rank-card">
            <div class="rank-num">#{i+1}</div>
            <div class="rank-sym">{r['sym']}</div>
            <div class="rank-bar"><div class="rank-fill" style="width:{bar_w}%; background:{fill_color}; box-shadow: 0 0 10px {fill_color};"></div></div>
            <div style="width:60px; text-align:right; font-family:'Roboto Mono'; color:{fill_color};">{r['chg']:+.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- RIGHT COLUMN: TWITTER FEED (SCROLLABLE) ---
with col_side:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="title-glitch">LIVE INTEL FEED</div>', unsafe_allow_html=True)
    
    # Session State for "Load More"
    if 'tweet_count' not in st.session_state:
        st.session_state.tweet_count = 5

    async def get_feed():
        if not os.path.exists("cookies.json"):
            return [{"user": {"name": "SYSTEM", "screen_name": "Admin"}, "text": "COOKIES.JSON MISSING"}]
        try:
            client = Client("en-US")
            with open("cookies.json", "r") as f:
                raw = json.load(f)
            cookies = {c["name"]: c["value"] for c in raw} if isinstance(raw, list) else raw
            client.set_cookies(cookies)
            # Fetch more if requested
            return await client.search_tweet(f"${ticker} filter:verified", "Latest", count=st.session_state.tweet_count + 5)
        except Exception as e:
            return [{"user": {"name": "ERROR", "screen_name": "System"}, "text": str(e)}]

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tweets = loop.run_until_complete(get_feed())
        
        # Render Twitter Cards
        for t in tweets:
            # Handle Data Structure
            if isinstance(t, dict):
                name = t['user']['name']
                handle = t['user']['screen_name']
                text = t['text']
            else:
                name = t.user.name
                handle = t.user.screen_name
                text = t.text
            
            # Generate Avatar Initials
            initial = name[0] if name else "?"
            
            st.markdown(f"""
            <div class="tweet-card">
                <div class="tweet-header">
                    <div class="avatar">{initial}</div>
                    <div class="user-info">
                        <div style="display:flex; align-items:center;">
                            <span class="name">{name}</span>
                            <span class="verified">☑</span>
                        </div>
                        <span class="handle">@{handle}</span>
                    </div>
                </div>
                <div class="tweet-text">{text}</div>
                <div class="tweet-footer">
                    <span>Just now</span>
                    <span>INTEL SCAN</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        # LOAD MORE BUTTON
        if st.button("LOAD MORE INTEL", key="load_more", help="Fetch older tweets"):
            st.session_state.tweet_count += 5
            st.rerun()
            
    except Exception as e:
        st.error(f"FEED ERROR: {e}")

    # VERTICAL AD IN FEED
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

# ---------------- BOTTOM AD (HORIZONTAL) ----------------
components.html(
    """
    <div style="text-align:center;">
        <script async="async" data-cfasync="false" src="https://pl28519010.effectivegatecpm.com/7f2ad764010d514cdee2fdac0b042524/invoke.js"></script>
        <div id="container-7f2ad764010d514cdee2fdac0b042524"></div>
    </div>
    """,
    height=100,
)
