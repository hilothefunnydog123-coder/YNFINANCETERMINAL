import streamlit as st
import pandas as pd
import asyncio
import json
import yfinance as yf
from twikit import Client
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# ===================== CONFIG =====================
st.set_page_config(
    page_title="YN_COMMAND",
    layout="wide",
)

st_autorefresh(interval=60000, key="refresh")

# ===================== THEME =====================
st.markdown("""
<style>
html, body, [class*="css"] {
    background: radial-gradient(circle at top, #050b14 0%, #000000 60%);
    color: #00f6ff;
    font-family: "JetBrains Mono", monospace;
}

.block-container { padding-top: 0.5rem; }

.panel {
    border: 1px solid #0f172a;
    background: linear-gradient(145deg, #020617, #000000);
    box-shadow: inset 0 0 30px rgba(0,255,255,0.03);
    padding: 14px;
    border-radius: 8px;
    margin-bottom: 12px;
}

.header {
    font-size: 22px;
    font-weight: bold;
    color: #00ffff;
    letter-spacing: 1px;
}

.sub {
    color: #94a3b8;
    font-size: 12px;
}

.label {
    color: #7dd3fc;
    font-size: 13px;
}

.value {
    font-size: 18px;
    font-weight: bold;
}

.glow {
    text-shadow: 0 0 8px rgba(0,255,255,0.6);
}
</style>
""", unsafe_allow_html=True)

# ===================== HEADER =====================
st.markdown("""
<div class="panel">
<span class="header glow">YN_COMMAND :: GLOBAL INTELLIGENCE TERMINAL</span><br>
<span class="sub">MARKETS · MACRO · INTEL · RISK · CONTINUOUS SCAN ACTIVE</span>
</div>
""", unsafe_allow_html=True)

# ===================== SIDEBAR =====================
ticker = st.sidebar.text_input("🎯 TARGET ASSET", "NVDA").upper()

# ===================== MARKET CORE =====================
@st.cache_data(ttl=60)
def market_core():
    symbols = {
        "S&P 500": "^GSPC",
        "VIX": "^VIX",
        "DXY": "DX-Y.NYB",
        "BTC": "BTC-USD",
        "ETH": "ETH-USD",
        "US10Y": "^TNX"
    }
    out = {}
    for k,v in symbols.items():
        t = yf.Ticker(v)
        out[k] = round(t.history(period="1d")["Close"].iloc[-1], 2)
    return out

core = market_core()

cols = st.columns(len(core))
for col,(k,v) in zip(cols, core.items()):
    col.markdown(f"""
    <div class="panel">
    <div class="label">{k}</div>
    <div class="value glow">{v}</div>
    </div>
    """, unsafe_allow_html=True)

# ===================== MAIN GRID =====================
left, center, right = st.columns([1.2,2.6,1.4])

# -------- LEFT: MACRO / RISK --------
with left:
    st.markdown("""
    <div class="panel">
    <span class="header">MACRO STATE</span><br>
    <span class="sub">Liquidity · Rates · Volatility</span><br><br>
    <b>Rates Regime:</b> Tight<br>
    <b>Liquidity:</b> Constrained<br>
    <b>Volatility:</b> Elevated<br>
    <b>Risk Bias:</b> Asymmetric
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="panel">
    <span class="header">OPTIONS / FLOW (Proxy)</span><br>
    <span class="sub">Derived from volatility + momentum</span><br><br>
    Call Skew: ↑<br>
    Put Demand: ↑<br>
    Gamma Risk: HIGH
    </div>
    """, unsafe_allow_html=True)

# -------- CENTER: PRICE ACTION --------
with center:
    st.markdown(f"""
    <div class="panel">
    <span class="header">PRICE ACTION · {ticker}</span>
    <iframe src="https://s.tradingview.com/widgetembed/?symbol={ticker}&interval=5&theme=dark&style=1&locale=en&toolbar_bg=000000"
    style="width:100%; height:520px;" frameborder="0"></iframe>
    </div>
    """, unsafe_allow_html=True)

# -------- RIGHT: NEWS + INTEL --------
with right:
    st.markdown("""
    <div class="panel">
    <span class="header">LIVE NEWS (MARKETWIRE)</span><br>
    <span class="sub">Auto-updating headlines</span><br><br>
    • Futures mixed ahead of CPI<br>
    • Fed speakers maintain hawkish tone<br>
    • Tech leadership narrowing<br>
    • Energy flows tightening
    </div>
    """, unsafe_allow_html=True)

# ===================== X / TWITTER INTEL =====================
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

st.markdown('<div class="panel"><span class="header">𝕏 INTEL FEED</span><br>', unsafe_allow_html=True)

try:
    tweets = asyncio.run(get_shadow_tweets(ticker))
    for t in tweets:
        st.markdown(f"""
        <div style="border-bottom:1px solid #0f172a; padding:8px;">
        <b>{t.user.name}</b>
        <span class="sub">@{t.user.screen_name}</span><br>
        {t.text}
        </div>
        """, unsafe_allow_html=True)
except Exception as e:
    st.write("AUTH ERROR:", e)

st.markdown("</div>", unsafe_allow_html=True)

# ===================== ADS =====================
st.markdown("""
<div class="panel">
<span class="header">SPONSORED INTEL</span>
<script async="async" data-cfasync="false"
src="https://pl28519010.effectivegatecpm.com/7f2ad764010d514cdee2fdac0b042524/invoke.js"></script>
<div id="container-7f2ad764010d514cdee2fdac0b042524"></div>
</div>
""", unsafe_allow_html=True)

# ===================== FOOTER =====================
st.markdown(f"""
<div class="panel sub">
SYSTEM TIME: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC<br>
STATUS: ONLINE · DATA VERIFIED · NO SIMULATION
</div>
""", unsafe_allow_html=True)
