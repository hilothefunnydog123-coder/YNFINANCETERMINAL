import streamlit as st
import yfinance as yf

stock = yf.Ticker(st.session_state.ticker)
info = stock.info

st.markdown("<h1 style='color:#00ff41;'>// FUNDAMENTAL_HUB</h1>", unsafe_allow_html=True)

# CATEGORY 7: ESTIMATES & FORECASTS (Fixed)
st.markdown("### // ANALYST_ESTIMATES")
f1, f2, f3 = st.columns(3)

# Use .get() with fallback values to prevent "NoneType" errors
f1.metric("TARGET_PRICE", f"${info.get('targetMedianPrice', 'N/A')}")
f2.metric("RECO_SCORE", info.get('recommendationMean', 'N/A'), help="1.0 Strong Buy -> 5.0 Sell")
f3.metric("UPSIDE", f"{info.get('targetMeanPrice', 0) / info.get('currentPrice', 1) * 100 - 100:.2f}%")

# CATEGORY 5: STATEMENTS
with st.expander("VIEW_FULL_FINANCIAL_STATEMENTS"):
    st.dataframe(stock.income_stmt, use_container_width=True)
