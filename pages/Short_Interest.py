import streamlit as st
import yfinance as yf

# 1. STYLE CONFIG
st.set_page_config(layout="wide", page_title="SHORT_SURVEILLANCE_2026")

st.markdown("""
<style>
    [data-testid="stAppViewBlockContainer"] { padding-top: 1rem; max-width: 95% !important; }
    .short-box {
        background: rgba(255, 75, 75, 0.05);
        border-left: 5px solid #ff4b4b;
        padding: 20px; border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)
info = stock.info

st.markdown(f"<h1 style='color:#ff4b4b; font-family:monospace;'>// SHORT_SURVEILLANCE: {ticker}</h1>", unsafe_allow_html=True)

# 2. SQUEEZE METRICS
short_float = info.get('shortPercentOfFloat', 0) * 100
short_ratio = info.get('shortRatio', 0) # Also known as Days to Cover
shares_short = info.get('sharesShort', 0)

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("SHORT_%_OF_FLOAT", f"{short_float:.2f}%", delta="HIGH_PRESSURE" if short_float > 15 else "LOW", delta_color="inverse")
with c2:
    st.metric("DAYS_TO_COVER", f"{short_ratio:.2f}", delta="SQUEEZE_ZONE" if short_ratio > 5 else "LIQUID", delta_color="inverse")
with c3:
    st.metric("SHARES_SHORTED", f"{shares_short:,}")

# 3. THE SQUEEZE VERDICT
st.markdown("### // SQUEEZE_PROBABILITY_DECODE")

squeeze_score = 0
if short_float > 10: squeeze_score += 40
if short_ratio > 5: squeeze_score += 40
if info.get('forwardPE', 0) < info.get('trailingPE', 1): squeeze_score += 20 # Undervalued growth

color = "#00ff41" if squeeze_score < 30 else "#fffd00" if squeeze_score < 70 else "#ff4b4b"

st.markdown(f"""
<div class='short-box'>
    <h4 style='margin:0; color:#ff4b4b;'>SQUEEZE_SCORE: {squeeze_score}/100</h4>
    <p style='color:#eee;'>
        Analysis indicates a <b>{'LOW' if squeeze_score < 30 else 'MODERATE' if squeeze_score < 70 else 'EXTREME'}</b> 
        probability of a short squeeze. {'Shorts are in a comfortable position.' if squeeze_score < 30 else 'High borrowing costs and days to cover suggest shorts are trapped if price breaks resistance.'}
    </p>
</div>
""", unsafe_allow_html=True)
