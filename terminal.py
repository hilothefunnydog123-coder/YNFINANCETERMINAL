import streamlit as st
import pandas as pd
import asyncio
import json
import yfinance as yf
from twikit import Client
from streamlit_autorefresh import st_autorefresh
import os

# ---------------- CONFIG ----------------
st.set_page_config(
    layout="wide",
    page_title="YN_COMMAND TERMINAL",
    initial_sidebar_state="collapsed"
)

# Auto-refresh every 60 seconds to keep data live
st_autorefresh(interval=60000, key="refresh")

# ---------------- STYLE ----------------
st.markdown("""
<style>
    /* GLOBAL RESET */
    html, body, [class*="css"] {
        background-color: #000000;
        color: #00ffff;
        font-family: 'Courier New', monospace;
    }
    
    /* HIDE STREAMLIT UI CRUFT */
    [data-testid="stHeader"] { display: none; }
    .block-container { padding-top: 1rem; padding-bottom: 2rem; }
    
    /* CUSTOM BORDERS */
    .section {
        border: 1px solid #1f2933;
        background-color: #050505;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 0 10px rgba(0, 255, 255, 0.05);
    }
    
    /* TYPOGRAPHY */
    .title {
        color: #00ffff;
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 1px;
        border-bottom: 1px dashed #333;
        padding-bottom: 5px;
    }
    .value {
        font-size: 24px;
        font-weight: bold;
        color: #e0e0e0;
    }
    .small { color: #555; font-size: 10px; }
    
    /* TWEET BOX */
    .tweet {
        border-left: 2px solid #333;
        padding-left: 10px;
        margin-bottom: 12px;
        font-size: 12px;
        color: #ccc;
    }
    .tweet b { color: #00ffff; }
    
    /* AD CONTAINER */
    #ad-container { margin-top: 20px; border: 1px solid #333; padding: 10px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<div class="section">
    <span style="font-size:24px; font-weight:900; color:#fff;">YN GLOBAL SURVEILLANCE TERMINAL</span><br>
    <span class="small" style="color:#00ffff;">LIVE DATA · REAL FEEDS · CONTINUOUS SCAN ACTIVE</span>
</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("### // TARGET SELECTOR")
    ticker = st.text_input("SYMBOL", "NVDA").upper()
    st.caption("SYSTEM: ONLINE")

# ---------------- MARKET SNAPSHOT ----------------
@st.cache_data(ttl=60)
def market_snapshot():
    symbols = {
        "SPX": "^GSPC",
        "VIX": "^VIX",
        "DXY": "DX-Y.NYB",
        "BTC": "BTC-USD",
        "ETH": "ETH-USD"
    }
    data = {}
    try:
        tickers = list(symbols.values())
        df = yf.download(tickers, period="2d", progress=False)['Close']
        
        # Handle MultiIndex
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        # Fill NaNs
        df = df.ffill().bfill()
        
        for k, v in symbols.items():
            if v in df.columns:
                price = df[v].iloc[-1]
                data[k] = f"{price:,.2f}"
            else:
                data[k] = "ERR"
    except:
        data = {k: "N/A" for k in symbols}
    return data

snap = market_snapshot()

c1, c2, c3, c4, c5 = st.columns(5)
metrics = list(snap.items())

for col, (k, v) in zip([c1, c2, c3, c4, c5], metrics):
    col.markdown(f"""
    <div class="section" style="text-align:center; padding:10px;">
        <div style="color:#555; font-size:10px;">{k}</div>
        <div style="font-size:18px; color:#00ffff; font-weight:bold;">{v}</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------- TRADINGVIEW CHART ----------------
st.markdown(f"""
<div class="section">
    <div class="title">PRICE ACTION · {ticker}</div>
    <div style="height:500px;">
        <div class="tradingview-widget-container" style="height:100%;width:100%">
            <div id="tradingview_b239c" style="height:100%;width:100%"></div>
            <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
            <script type="text/javascript">
            new TradingView.widget(
            {{
                "autosize": true,
                "symbol": "{ticker}",
                "interval": "5",
                "timezone": "Etc/UTC",
                "theme": "dark",
                "style": "1",
                "locale": "en",
                "enable_publishing": false,
                "backgroundColor": "rgba(0, 0, 0, 1)",
                "gridColor": "rgba(30, 30, 30, 1)",
                "hide_top_toolbar": false,
                "save_image": false,
                "container_id": "tradingview_b239c"
            }}
            );
            </script>
        </div>
        </div>
</div>
""", unsafe_allow_html=True)

# ---------------- X / TWITTER INTEL ----------------
async def get_shadow_tweets(query_ticker):
    # Initialize Client
    client = Client("en-US")
    
    # Check for cookies file
    if not os.path.exists("cookies.json"):
        return [{"user": {"name": "SYSTEM", "screen_name": "Admin"}, "text": "COOKIES.JSON MISSING - UPLOAD AUTH FILE"}]
        
    try:
        with open("cookies.json", "r") as f:
            raw = json.load(f)
        
        # Convert list format to dictionary if necessary
        if isinstance(raw, list):
            cookies = {c["name"]: c["value"] for c in raw}
        else:
            cookies = raw
            
        client.set_cookies(cookies)
        
        # Search Query: Cashtag + Verified filter for quality
        tweets = await client.search_tweet(f"${query_ticker}", "Latest", count=5)
        return tweets
    except Exception as e:
        return [{"user": {"name": "ERROR", "screen_name": "System"}, "text": f"AUTH FAILURE: {str(e)}"}]

st.markdown('<div class="section"><div class="title">𝕏 INTEL FEED (SHADOW)</div>', unsafe_allow_html=True)

# Run Async Loop safely in Streamlit
try:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tweets = loop.run_until_complete(get_shadow_tweets(ticker))
    
    for t in tweets:
        # Handle both Twikit objects and error dicts
        if isinstance(t, dict):
            name = t['user']['name']
            handle = t['user']['screen_name']
            text = t['text']
        else:
            name = t.user.name
            handle = t.user.screen_name
            text = t.text
            
        st.markdown(f"""
        <div class="tweet">
            <div><b>{name}</b> <span style="color:#555;">@{handle}</span></div>
            <div style="margin-top:4px;">{text}</div>
        </div>
        """, unsafe_allow_html=True)
        
except Exception as e:
    st.error(f"RUNTIME ERROR: {e}")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- ADS (ADSTERRA NATIVE) ----------------
# Injected at the bottom as requested in the snippet
import streamlit.components.v1 as components

components.html(
    """
    <html>
      <head>
        <meta charset="utf-8">
      </head>
      <body style="margin:0;padding:0;background:#000000;text-align:center;">
        <div style="color:#333;font-family:monospace;font-size:10px;margin-bottom:5px;">SPONSORED UPLINK</div>
        <script async="async" data-cfasync="false"
          src="https://pl28519010.effectivegatecpm.com/7f2ad764010d514cdee2fdac0b042524/invoke.js">
        </script>
        <div id="container-7f2ad764010d514cdee2fdac0b042524"></div>
      </body>
    </html>
    """,
    height=100,
)
