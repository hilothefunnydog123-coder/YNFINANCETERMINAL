import streamlit as st
import yfinance as yf

# Ensure ticker exists
if 'ticker' not in st.session_state: st.session_state.ticker = "NVDA"
stock = yf.Ticker(st.session_state.ticker)

st.title(f"// FUNDAMENTAL_INTELLIGENCE: {st.session_state.ticker}")

# Tabs to separate the massive data lists
tab1, tab2, tab3, tab4 = st.tabs(["STATEMENTS (Cat 5)", "RATIOS (Cat 6)", "FORECASTS (Cat 7)", "OWNERSHIP (Cat 8)"])

with tab1:
    st.subheader("Income, Balance Sheet, Cash Flow")
    st.dataframe(stock.income_stmt, use_container_width=True)
    st.dataframe(stock.balance_sheet, use_container_width=True)

with tab2:
    st.subheader("Profitability & Valuation Ratios")
    r1, r2, r3 = st.columns(3)
    r1.metric("P/E Ratio", stock.info.get('trailingPE'))
    r2.metric("EV/EBITDA", stock.info.get('enterpriseToEbitda'))
    r3.metric("ROE", f"{stock.info.get('returnOnEquity', 0)*100:.2f}%")

with tab4:
    st.subheader("Institutional & Insider Flows")
    st.write("Major Holders:")
    st.dataframe(stock.major_holders)
    st.write("Institutional Holders:")
    st.dataframe(stock.institutional_holders)
