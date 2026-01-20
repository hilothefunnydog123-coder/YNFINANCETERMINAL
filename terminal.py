import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import pytz
import time

# =========================================================
# 1. CONFIG
# =========================================================
st.set_page_config(
    layout="wide",
    page_title="SOVEREIGN | MARKET INTELLIGENCE",
    initial_sidebar_state="collapsed"
)

# =========================================================
# 2. JARVIS / BLOOMBERG CSS
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&family=Inter:wght@400;700;900&display=swap');

.stApp {
    background:#000;
    color:#cfcfcf;
    font-family:'Inter', sans-serif;
}
[data-testid="stHeader"] { display:none; }
.block-container { padding:1rem 1.5rem; }

.mono { font-family:'Roboto Mono', monospace; }
.pos { color:#00ffcc; }
.neg { color:#ff4d4d; }
.warn { color:#ffcc00; }
.cyan { color:#00f0ff; }

.panel {
    background:#080808;
    border:1px solid #222;
    padding:14px;
    height:100%;
}

.panel-header {
    display:flex;
    justify-content:space-between;
    border-bottom:1px solid #333;
    padding-bottom:6px;
    margin-bottom:10px;
}

.panel-title {
    font-size:11px;
    font-weight:900;
    letter-spacing:1px;
    text-transform:uppercase;
    color:#fff;
}

.regime-strip {
    display:grid;
    grid-template-columns:repeat(5,1fr);
    border:1px solid #222;
    margin-bottom:10px;
}

.regime-cell {
    padding:8px;
    text-align:center;
    border-right:1px solid #222;
}
.regime-cell:last-child { border-right:none; }

.regime-label {
    font-size:9px;
    color:#666;
    letter-spacing:1px;
}
.regime-val {
    font-size:13px;
    font-weight:900;
    font-family:'Roboto Mono';
}

.tweet {
    border-left:2px solid #333;
    padding:8px;
    margin-bottom:8px;
    background:#000;
}
.tweet-handle { font-size:11px; font-weight:bold; color:#fff; }
.tweet-time { font-size:9px; color:#555; }
.tweet-body { font-size:11px; color:#ccc; }

.delta-row {
    display:flex;
    justify-content:space-between;
    padding:6px 0;
    border-bottom:1px dashed #222;
    font-size:11px;
}

.footer {
    position:fixed;
    bottom:0;
    left:0;
    width:100%;
    background:#000;
    border-top:1px solid #222;
    padding:3px 12px;
    font-family:'Roboto Mono';
    font-size:9px;
    color:#666;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. SAFE HELPERS
# =========================================================
def safe_last(series, fallback=0):
    try:
        val = series.iloc[-1]
        return fallback if pd.isna(val) else val
    except:
        return fallback

# =========================================================
# 4. DATA (CACHED)
# =========================================================
@st.cache_data(ttl=300)
def fetch_prices():
    tickers = ["^GSPC","^VIX","^TNX","NVDA"]
    df = yf.download(tickers, period="2mo", interval="1d", progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df = df["Close"]
    return df.ffill().bfill()

@st.cache_data(ttl=300)
def fetch_intraday():
    df = yf.download("NVDA", period="5d", interval="15m", progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df.ffill().bfill()

@st.cache_data(ttl=300)
def fetch_news():
    try:
        return yf.Ticker("QQQ").news[:6]
    except:
        return []

# =========================================================
# 5. ENGINE
# =========================================================
prices = fetch_prices()
intraday = fetch_intraday()
news = fetch_news()

vix = safe_last(prices.get("^VIX", pd.Series()))
tnx = safe_last(prices.get("^TNX", pd.Series()))
nvda = safe_last(prices.get("NVDA", pd.Series()))

regime = {
    "RISK": "RISK-ON" if vix < 20 else "RISK-OFF",
    "VOL": f"{vix:.2f}",
    "LIQ": "TIGHT" if tnx > 4.2 else "NEUTRAL",
    "RATES": f"{tnx:.2f}%",
    "ALIGN": "MIXED"
}

# =========================================================
# 6. RENDER REGIME
# =========================================================
st.markdown("""
<div class="regime-strip">
""" + "".join([
    f"""
    <div class="regime-cell">
        <div class="regime-label">{k}</div>
        <div class="regime-val {'pos' if 'ON' in v else ''}">{v}</div>
    </div>
    """ for k,v in regime.items()
]) + "</div>", unsafe_allow_html=True)

st.markdown(
    "<div class='cyan mono' style='font-size:10px;margin-bottom:10px;'>"
    "AI SITUATION AWARENESS ONLINE — CONTINUOUS SCAN ACTIVE"
    "</div>",
    unsafe_allow_html=True
)

# =========================================================
# 7. LAYOUT
# =========================================================
c1, c2, c3 = st.columns([1,1.2,1])

# ----------------- RISK & DELTA -----------------
with c1:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div class='panel-header'><span class='panel-title'>RISK & DELTA</span></div>", unsafe_allow_html=True)

    st.markdown(f"<div class='delta-row'><span>US10Y</span><span>{tnx:.2f}%</span></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='delta-row'><span>VIX</span><span>{vix:.2f}</span></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='delta-row'><span>NVDA</span><span>${nvda:.2f}</span></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- CHART -----------------
with c2:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div class='panel-header'><span class='panel-title'>PRICE ACTION</span><span class='panel-title cyan'>NVDA</span></div>", unsafe_allow_html=True)

    if not intraday.empty:
        fig = go.Figure(go.Candlestick(
            x=intraday.index,
            open=intraday["Open"],
            high=intraday["High"],
            low=intraday["Low"],
            close=intraday["Close"],
            increasing_line_color="#00ffcc",
            decreasing_line_color="#ff4d4d"
        ))
        fig.update_layout(
            template="plotly_dark",
            height=260,
            paper_bgcolor="#080808",
            plot_bgcolor="#080808",
            xaxis_rangeslider_visible=False,
            yaxis=dict(side="right", gridcolor="#222")
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown("<div class='mono warn'>DATA STALE — USING LAST SNAPSHOT</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- INTEL FEED -----------------
with c3:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div class='panel-header'><span class='panel-title'>INTEL FEED</span></div>", unsafe_allow_html=True)

    if news:
        for n in news:
            st.markdown(f"""
            <div class='tweet'>
                <div class='tweet-handle'>@MarketWire <span class='tweet-time'>LIVE</span></div>
                <div class='tweet-body'>{n.get("title","Market Update")}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<div class='tweet'><div class='tweet-body'>NO ACTIVE NEWS — MONITORING FLOWS</div></div>", unsafe_allow_html=True)

    # --------- ADS (NATIVE BANNER) ---------
    st.markdown("""
    <div style="margin-top:10px;">
        <script async data-cfasync="false" src="https://pl28519010.effectivegatecpm.com/7f2ad764010d514cdee2fdac0b042524/invoke.js"></script>
        <div id="container-7f2ad764010d514cdee2fdac0b042524"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 8. FOOTER
# =========================================================
now = datetime.now(pytz.timezone("US/Eastern")).strftime("%H:%M:%S")
st.markdown(f"""
<div class="footer">
STATUS: SECURE UPLINK | CACHE ACTIVE | {now} ET
</div>
""", unsafe_allow_html=True)
