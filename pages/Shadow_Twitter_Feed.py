import streamlit as st
import pandas as pd
import asyncio
import json
import yfinance as yf
from twikit import Client
from streamlit_autorefresh import st_autorefresh

# ---------------- CONFIG ----------------
st.set_page_config(
    layout="wide",
    page_title="YN_COMMAND TERMINAL",
)

st_autorefresh(interval=60000, key="refresh")

# ---------------- STYLE ----------------
st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #000000;
    color: #00ffff;
    font-family: monospace;
}
.block-container { padding-top: 1rem; }
.section {
    border: 1px solid #1f2933;
    padding: 12px;
    margin-bottom: 12px;
}
.title {
    color:#00ffff;
    font-size:18px;
    font-weight:bold;
    margin-bottom:6px;
}
.small { color:#9ca3af; font-size:12px; }
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<div class="section">
<span class="title">YN GLOBAL SURVEILLANCE TERMINAL</span><br>
<span class="small">LIVE DATA · REAL FEEDS · CONTINUOUS SCAN ACTIVE</span>
</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
ticker = st.sidebar.text_input("TARGET TICKER", "NVDA").upper()

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
    for k,v in symbols.items():
        t = yf.Ticker(v)
        data[k] = round(t.history(period="1d")["Close"].iloc[-1], 2)
    return data

snap = market_snapshot()

c1,c2,c3,c4,c5 = st.columns(5)
for col,(k,v) in zip([c1,c2,c3,c4,c5], snap.items()):
    col.markdown(f"""
    <div class="section">
    <div class="title">{k}</div>
    <div>{v}</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------- TRADINGVIEW CHART ----------------
st.markdown(f"""
<div class="section">
<div class="title">PRICE ACTION · {ticker}</div>
<iframe src="https://s.tradingview.com/widgetembed/?symbol={ticker}&interval=5&theme=dark&style=1&locale=en&toolbar_bg=000000"
style="width:100%; height:500px;" frameborder="0"></iframe>
</div>
""", unsafe_allow_html=True)

# ---------------- X / TWITTER INTEL ----------------
async def get_shadow_tweets(ticker):
    client = Client("en-US")
    with open("cookies.json","r") as f:
        raw = json.load(f)
    cookies = {c["name"]: c["value"] for c in raw}
    client.set_cookies(cookies)
    tweets = await client.search_tweet(
        f"${ticker} filter:verified",
        "Latest",
        count=8
    )
    return tweets

st.markdown('<div class="section"><div class="title">𝕏 INTEL FEED</div>', unsafe_allow_html=True)

try:
    tweets = asyncio.run(get_shadow_tweets(ticker))
    for t in tweets:
        st.markdown(f"""
        <div style="border-bottom:1px solid #1f2933; padding:8px 0;">
        <b>{t.user.name}</b> @{t.user.screen_name}<br>
        {t.text}
        </div>
        """, unsafe_allow_html=True)
except Exception as e:
    st.write("AUTH ERROR:", e)

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- ADS (ADSTERRA NATIVE) ----------------
st.markdown("""
<div class="section">
<div class="title">SPONSORED</div>
<script async="async" data-cfasync="false"
src="https://pl28519010.effectivegatecpm.com/7f2ad764010d514cdee2fdac0b042524/invoke.js"></script>
<div id="container-7f2ad764010d514cdee2fdac0b042524"></div>
</div>
""", unsafe_allow_html=True)
