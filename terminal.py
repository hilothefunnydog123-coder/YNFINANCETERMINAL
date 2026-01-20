import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import json
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="STREET_INTEL",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- STYLE ----------------
st.markdown("""
<style>
body { background-color: #0b0f14; color: #e6e6e6; }
.block-container { padding-top: 1rem; }
h1, h2, h3 { color: #00ff88; font-family: monospace; }
.metric { background:#111; padding:12px; border-radius:6px; }
.card { background:#0f141c; padding:16px; border-radius:10px; border:1px solid #1f2937; }
.small { font-size:12px; opacity:0.7; }
hr { border:0; border-top:1px solid #1f2937; }
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("## // STREET_INTEL :: TERMINAL")

# ---------------- LIVE MARKET DATA ----------------
tickers = {
    "SPX": "^GSPC",
    "NDX": "^NDX",
    "VIX": "^VIX",
    "NVDA": "NVDA",
    "AAPL": "AAPL",
    "MSFT": "MSFT"
}

cols = st.columns(len(tickers))
for col, (name, symbol) in zip(cols, tickers.items()):
    data = yf.Ticker(symbol).history(period="1d")
    if not data.empty:
        price = data["Close"].iloc[-1]
        change = data["Close"].iloc[-1] - data["Open"].iloc[-1]
        pct = (change / data["Open"].iloc[-1]) * 100
        col.metric(name, f"{price:,.2f}", f"{pct:+.2f}%")

st.divider()

# ---------------- MARKET REGIME ----------------
spx = yf.Ticker("^GSPC").history(period="6mo")
vix = yf.Ticker("^VIX").history(period="1mo")

trend = "RISK ON" if spx["Close"].iloc[-1] > spx["Close"].rolling(50).mean().iloc[-1] else "RISK OFF"
vol = "LOW VOL" if vix["Close"].iloc[-1] < 18 else "HIGH VOL"

st.markdown("### // MARKET REGIME")
st.markdown(f"""
<div class="card">
<b>{trend}</b> | {vol}<br>
<span class="small">SPX Trend + Volatility Conditions</span>
</div>
""", unsafe_allow_html=True)

st.divider()

# ---------------- INSTITUTIONAL HOLDERS ----------------
st.markdown("### // INSTITUTIONAL WHALES :: NVDA")

holders = yf.Ticker("NVDA").institutional_holders
if holders is not None:
    st.dataframe(holders.head(10), use_container_width=True)

# ---------------- ADSTERAA NATIVE AD ----------------
st.markdown("### // SPONSORED LIQUIDITY")
st.components.v1.html("""
<script async data-cfasync="false"
src="https://pl28519010.effectivegatecpm.com/7f2ad764010d514cdee2fdac0b042524/invoke.js"></script>
<div id="container-7f2ad764010d514cdee2fdac0b042524"></div>
""", height=250)

st.divider()

# ---------------- TWITTER INTEL FEED ----------------
st.markdown("### // REAL-TIME INTEL (X/TWITTER)")

try:
    with open("cookies.json", "r") as f:
        tweets = json.load(f)

    for t in tweets[:8]:
        st.markdown(f"""
        <div class="card">
        <b>@{t['username']}</b><br>
        {t['text']}<br>
        <span class="small">{t['timestamp']}</span>
        </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error("Twitter feed unavailable")

st.divider()

# ---------------- FOOTER ----------------
st.markdown("""
<div class="small">
DATA DELAYED. FOR INFORMATIONAL USE ONLY. NOT FINANCIAL ADVICE.
</div>
""", unsafe_allow_html=True)
