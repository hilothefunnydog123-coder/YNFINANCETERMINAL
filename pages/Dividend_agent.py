import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 1. STYLE CONFIG
st.set_page_config(layout="wide", page_title="DIVIDEND_ENGINE_2026")

st.markdown("""
<style>
    [data-testid="stAppViewBlockContainer"] { padding-top: 1rem; max-width: 98% !important; }
    .div-card {
        background: rgba(0, 255, 65, 0.03);
        border: 1px solid rgba(0, 255, 65, 0.2);
        padding: 25px; border-radius: 20px;
        text-align: center;
    }
    .div-value { font-size: 32px; font-weight: 800; color: #00ff41; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)
info = stock.info

st.markdown(f"<h1 style='color:#00ff41; font-family:monospace;'>// DIVIDEND_ENGINE: {ticker}</h1>", unsafe_allow_html=True)

# 2. DATA EXTRACTION
div_yield = info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0
payout_ratio = info.get('payoutRatio', 0) * 100 if info.get('payoutRatio') else 0
div_rate = info.get('dividendRate', 0)

# 3. TOP-LEVEL METRICS
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("<div class='div-card'><span style='color:#888;'>ANNUAL_YIELD</span>", unsafe_allow_html=True)
    st.markdown(f"<div class='div-value'>{div_yield:.2f}%</div></div>", unsafe_allow_html=True)

with c2:
    status = "SAFE" if payout_ratio < 60 else "CAUTION" if payout_ratio < 90 else "DANGER"
    st.markdown(f"<div class='div-card'><span style='color:#888;'>PAYOUT_RATIO ({status})</span>", unsafe_allow_html=True)
    st.markdown(f"<div class='div-value'>{payout_ratio:.1f}%</div></div>", unsafe_allow_html=True)

with c3:
    st.markdown("<div class='div-card'><span style='color:#888;'>CASH_DISTRIBUTION</span>", unsafe_allow_html=True)
    st.markdown(f"<div class='div-value'>${div_rate:.2f}</div></div>", unsafe_allow_html=True)

# 4. DIVIDEND HISTORY CHART
st.markdown("### // PAYOUT_HISTORY_LATTICE")
history = stock.dividends
if not history.empty:
    df_div = history.to_frame().reset_index()
    fig = px.area(df_div, x='Date', y='Dividends', title="DIVIDEND_GROWTH_TRAJECTORY",
                  template="plotly_dark", color_discrete_sequence=['#00ff41'])
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No dividend history detected for this ticker. Growth-focused asset.")
