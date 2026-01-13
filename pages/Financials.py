import streamlit as st
import yfinance as yf

ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)
info = stock.info

st.markdown(f"<h1 style='color: #00ff41;'>// FINANCIAL_INTELLIGENCE: {ticker}</h1>", unsafe_allow_html=True)

# --- CATEGORY 7: ESTIMATES & FORECASTS ---
st.markdown("### // ANALYST_FORECASTS_2026")
f1, f2, f3, f4 = st.columns(4)

# Professional fallback logic for 2026
target = info.get('targetMedianPrice') or info.get('targetMeanPrice') or "N/A"
current = info.get('currentPrice') or info.get('regularMarketPrice') or 1
reco = info.get('recommendationKey', 'N/A').upper()

# Calculate Upside %
upside = "N/A"
if isinstance(target, (int, float)):
    upside = f"{((target / current) - 1) * 100:.2f}%"

with st.container():
    f1.metric("TARGET_PRICE", f"${target}")
    f2.metric("CURRENT_PRICE", f"${current}")
    f3.metric("UPSIDE_POTENTIAL", upside)
    f4.metric("CONSENSUS", reco)

st.markdown("---")

# --- CATEGORY 5: THE FINANCIALS (RESTORED) ---
st.markdown("### // CORE_STATEMENTS")
tab1, tab2, tab3 = st.tabs(["INCOME", "BALANCE_SHEET", "CASH_FLOW"])
with tab1:
    st.dataframe(stock.income_stmt, use_container_width=True)
with tab2:
    st.dataframe(stock.balance_sheet, use_container_width=True)
with tab3:
    st.dataframe(stock.cashflow, use_container_width=True)
