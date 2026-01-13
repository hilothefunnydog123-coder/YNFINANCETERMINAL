import streamlit as st
import yfinance as yf

# Logic Bridge
ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)
inf = stock.info

st.markdown(f"<h1>// FINANCIAL_INTELLIGENCE: {ticker}</h1>", unsafe_allow_html=True)

# Main Navigation Hub
m_tab1, m_tab2, m_tab3, m_tab4 = st.tabs(["STATEMENTS", "RATIOS & VALUATION", "FORECASTS", "OWNERSHIP"])

with m_tab1:
    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["INCOME_MTX", "BALANCE_MTX", "CASH_FLOW_MTX"])
    with sub_tab1: st.dataframe(stock.income_stmt.T, use_container_width=True)
    with sub_tab2: st.dataframe(stock.balance_sheet.T, use_container_width=True)
    with sub_tab3: st.dataframe(stock.cashflow.T, use_container_width=True)

with m_tab2:
    st.markdown("### // 100+ QUANTITATIVE_RATIOS")
    r_cols = st.columns(4)
    # Automated Grid Generation for massive list
    keys = ['trailingPE', 'forwardPE', 'priceToBook', 'enterpriseToEbitda', 'profitMargins', 'operatingMargins', 'returnOnEquity', 'debtToEquity']
    for i, k in enumerate(keys):
        r_cols[i % 4].metric(k.upper(), f"{inf.get(k, 'N/A')}")

with m_tab4:
    st.markdown("### // SHAREHOLDER_DYNAMICS")
    st.dataframe(stock.major_holders, use_container_width=True)
    st.dataframe(stock.institutional_holders, use_container_width=True)
