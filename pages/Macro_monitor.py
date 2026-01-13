import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. SYSTEM CONFIG
st.set_page_config(layout="wide", page_title="MACRO_MONITOR_2026")

st.markdown("""
<style>
    [data-testid="stAppViewBlockContainer"] { padding-top: 1rem; max-width: 98% !important; }
    .macro-card {
        background: rgba(0, 150, 255, 0.05);
        border: 1px solid rgba(0, 150, 255, 0.2);
        padding: 20px; border-radius: 15px;
    }
    .macro-value { font-family: monospace; font-size: 24px; color: #0096ff; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)

st.markdown(f"<h1 style='color:#0096ff; font-family:monospace;'>// MACRO_CORRELATION: {ticker}</h1>", unsafe_allow_html=True)

# 2. FETCH MACRO SIGNALS (Treasury Yields & Dollar Index)
@st.cache_data(ttl=3600)
def fetch_macro_data():
    # ^TNX = 10-Year Treasury Yield, DX-Y.NYB = US Dollar Index
    tnx = yf.Ticker("^TNX").history(period="1y")['Close']
    dxy = yf.Ticker("DX-Y.NYB").history(period="1y")['Close']
    return tnx, dxy

tnx_data, dxy_data = fetch_macro_data()

# 3. MACD/TICKER CORRELATION CHART
st.markdown("### // YIELD_SENSITIVITY_ANALYSIS (10Y_TREASURY vs TICKER)")

stock_price = stock.history(period="1y")['Close']

fig = go.Figure()
# Normalize data for comparison (0 to 100 scale)
def normalize(s): return (s - s.min()) / (s.max() - s.min()) * 100

fig.add_trace(go.Scatter(x=stock_price.index, y=normalize(stock_price), name=f"{ticker}_PRICE", line=dict(color='#00ff41', width=3)))
fig.add_trace(go.Scatter(x=tnx_data.index, y=normalize(tnx_data), name="10Y_TREASURY_YIELD", line=dict(color='#0096ff', width=2, dash='dot')))

fig.update_layout(template="plotly_dark", height=500, margin=dict(l=0,r=0,t=0,b=0), legend=dict(orientation="h", yanchor="bottom", y=1.02))
st.plotly_chart(fig, use_container_width=True)

# 4. MACRO BENTO BOX
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("<div class='macro-card'>", unsafe_allow_html=True)
    st.markdown("<span style='color:#888;'>CURRENT_10Y_YIELD</span>", unsafe_allow_html=True)
    st.markdown(f"<div class='macro-value'>{tnx_data.iloc[-1]:.2f}%</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='macro-card'>", unsafe_allow_html=True)
    st.markdown("<span style='color:#888;'>US_DOLLAR_INDEX (DXY)</span>", unsafe_allow_html=True)
    st.markdown(f"<div class='macro-value'>{dxy_data.iloc[-1]:.2f}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c3:
    # Correlation Math
    correlation = stock_price.corr(tnx_data)
    color = "#ff4b4b" if correlation < -0.5 else "#00ff41" if correlation > 0.5 else "#888"
    st.markdown("<div class='macro-card'>", unsafe_allow_html=True)
    st.markdown("<span style='color:#888;'>YIELD_CORRELATION</span>", unsafe_allow_html=True)
    st.markdown(f"<div class='macro-value' style='color:{color}'>{correlation:.2f}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# 5. AI MACRO DECODE
st.markdown("### // STRATEGIST_DECODE")
correlation_text = "Highly Inverse" if correlation < -0.5 else "Positively Correlated" if correlation > 0.5 else "Decoupled"

st.info(f"""
**ORACLE_MACRO:** {ticker} is currently **{correlation_text}** to rising yields. 
In the current 2026 environment, this suggests the stock acts as a 
{'Safe Haven' if correlation > 0.5 else 'Risk-On Asset'} relative to the debt market. 
Monitor the DXY at {dxy_data.iloc[-1]:.2f} for signs of international liquidity tightening.
""")
