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
        font-size: 20px;
        font-weight: bold;
        color: #e0e0e0;
    }
    .delta-pos { color: #00ff00; font-size: 12px; }
    .delta-neg { color: #ff0000; font-size: 12px; }
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
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<div class="section">
    <span style="font-size:24px; font-weight:900; color:#fff;">YN GLOBAL SURVEILLANCE TERMINAL</span><br>
    <span class="small" style="color:#00ffff;">FUTURES · COMMODITIES · FOREX · CRYPTO · INTEL</span>
</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("### // TARGET SELECTOR")
    ticker = st.text_input("SYMBOL", "NVDA").upper()
    st.caption("SYSTEM: ONLINE")

# ---------------- GLOBAL MARKET SCAN (The "Wake Up" Data) ----------------
@st.cache_data(ttl=60)
def fetch_global_scan():
    # 10 Key Metrics for Pre-Market Analysis
    symbols = {
        "ES_FUT": "ES=F",   # S&P 500 Futures
        "NQ_FUT": "NQ=F",   # Nasdaq Futures
        "10Y_YIELD": "^TNX", # Rates
        "VIX": "^VIX",      # Fear
        "DXY": "DX-Y.NYB",  # Dollar
        "OIL": "CL=F",      # Crude
        "GOLD": "GC=F",     # Safety
        "EURO": "EURUSD=X", # FX
        "BTC": "BTC-USD",   # Crypto Risk
        "ETH": "ETH-USD"    # Crypto Beta
    }
    
    data = {}
    try:
        # Batch download for speed
        tickers_list = list(symbols.values())
        df = yf.download(tickers_list, period="5d", interval="1d", progress=False)
        
        # Handle MultiIndex headers if they exist
        if isinstance(df.columns, pd.MultiIndex):
            try:
                # Try to get Close prices
                closes = df['Close']
            except KeyError:
                # If structure is different, fallback to flattening
                closes = df
                closes.columns = closes.columns.get_level_values(1)
        else:
            closes = df['Close'] # Fallback for simple structure

        # Process each symbol
        for k, v in symbols.items():
            if v in closes.columns:
                series = closes[v].dropna()
                if not series.empty:
                    curr = series.iloc[-1]
                    prev = series.iloc[-2] if len(series) > 1 else curr
                    
                    # Calculate % Change
                    chg = ((curr - prev) / prev) * 100
                    
                    # Formatting based on asset class
                    if "YIELD" in k or "VIX" in k: fmt = f"{curr:.2f}"
                    elif "BTC" in k: fmt = f"{curr:,.0f}"
                    elif "ETH" in k: fmt = f"{curr:,.0f}"
                    else: fmt = f"{curr:,.2f}"
                    
                    data[k] = {"price": fmt, "chg": chg}
                else:
                    data[k] = {"price": "N/A", "chg": 0.0}
            else:
                data[k] = {"price": "ERR", "chg": 0.0}
    except Exception as e:
        # Fallback empty structure
        data = {k: {"price": "OFFLINE", "chg": 0.0} for k in symbols}
        
    return data

scan_data = fetch_global_scan()

# Display in 2 Rows of 5 Columns
keys = list(scan_data.keys())
row1 = keys[:5] # Futures/Rates/VIX/DXY
row2 = keys[5:] # Commodities/FX/Crypto

# Render Row 1
cols1 = st.columns(5)
for col, k in zip(cols1, row1):
    item = scan_data[k]
    c_color = "#00ff00" if item['chg'] >= 0 else "#ff0000"
    col.markdown(f"""
    <div class="section" style="text-align:center; padding:10px;">
        <div style="color:#555; font-size:10px;">{k}</div>
        <div style="font-size:18px; color:#e0e0e0; font-weight:bold;">{item['price']}</div>
        <div style="font-size:11px; color:{c_color};">{item['chg']:+.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

# Render Row 2
cols2 = st.columns(5)
for col, k in zip(cols2, row2):
    item = scan_data[k]
    c_color = "#00ff00" if item['chg'] >= 0 else "#ff0000"
    col.markdown(f"""
    <div class="section" style="text-align:center; padding:10px;">
        <div style="color:#555; font-size:10px;">{k}</div>
        <div style="font-size:18px; color:#e0e0e0; font-weight:bold;">{item['price']}</div>
        <div style="font-size:11px; color:{c_color};">{item['chg']:+.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------- TRADINGVIEW CHART ----------------
st.markdown(f"""
<div class="section">
    <div class="title">PRICE ACTION · {ticker}</div>
    <div style="height:600px;">
        <div class="tradingview-widget-container" style="height:100%;width:100%">
            <div id="tradingview_b239c" style="height:100%;width:100%"></div>
            <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
            <script type="text/javascript">
            new TradingView.widget(
            {{
                "autosize": true,
                "symbol": "{ticker}",
                "interval": "15",
                "timezone": "Etc/UTC",
                "theme": "dark",
                "style": "1",
                "locale": "en",
                "enable_publishing": false,
                "backgroundColor": "rgba(0, 0, 0, 1)",
                "gridColor": "rgba(30, 30, 30, 1)",
                "hide_top_toolbar": false,
                "save_image": false,
                "studies": [
                    "RSI@tv-basicstudies",
                    "MASimple@tv-basicstudies",
                    "Volume@tv-basicstudies"
                ],
                "container_id": "tradingview_b239c"
            }}
            );
            </script>
        </div>
        </div>
</div>
""", unsafe_allow_html=True)

# ---------------- X / TWITTER INTEL (10 POSTS) ----------------
async def get_shadow_tweets(query_ticker):
    client = Client("en-US")
    
    if not os.path.exists("cookies.json"):
        return [{"user": {"name": "SYSTEM", "screen_name": "Admin"}, "text": "COOKIES.JSON MISSING - UPLOAD AUTH FILE"}]
        
    try:
        with open("cookies.json", "r") as f:
            raw = json.load(f)
        
        if isinstance(raw, list):
            cookies = {c["name"]: c["value"] for c in raw}
        else:
            cookies = raw
            
        client.set_cookies(cookies)
        
        # INCREASED COUNT TO 10
        tweets = await client.search_tweet(f"${query_ticker} filter:verified", "Latest", count=10)
        return tweets
    except Exception as e:
        return [{"user": {"name": "ERROR", "screen_name": "System"}, "text": f"AUTH FAILURE: {str(e)}"}]

st.markdown('<div class="section"><div class="title">𝕏 INTEL FEED (SHADOW MODE)</div>', unsafe_allow_html=True)

try:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tweets = loop.run_until_complete(get_shadow_tweets(ticker))
    
    # Display 10 Tweets
    for t in tweets:
        if isinstance(t, dict): # Handle Error Dict
            name = t['user']['name']
            handle = t['user']['screen_name']
            text = t['text']
        else: # Handle Twikit Object
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
st.markdown("""
<div class="section">
    <div class="title">SPONSORED UPLINK</div>
    <div style="text-align:center;">
        <script async="async" data-cfasync="false" 
            src="https://pl28519010.effectivegatecpm.com/7f2ad764010d514cdee2fdac0b042524/invoke.js">
        </script>
        <div id="container-7f2ad764010d514cdee2fdac0b042524"></div>
    </div>
</div>
""", unsafe_allow_html=True)
