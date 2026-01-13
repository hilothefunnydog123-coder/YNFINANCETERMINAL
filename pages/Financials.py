import streamlit as st
import yfinance as yf
import pandas as pd

# 1. TECHY CSS INJECTION
st.markdown("""
    <style>
    /* Glassmorphism Hub Effect */
    .stDataFrame {
        border: 1px solid rgba(0, 255, 65, 0.2);
        border-radius: 15px;
        overflow: hidden;
        background: rgba(10, 10, 10, 0.8);
        backdrop-filter: blur(10px);
    }
    /* Techy Data Header */
    .stat-header {
        color: #00f0ff;
        font-family: 'Courier New', monospace;
        letter-spacing: 2px;
        text-transform: uppercase;
        border-left: 4px solid #00f0ff;
        padding-left: 10px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. DATA INITIALIZATION
ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)
info = stock.info

st.markdown(f"<h1 style='color: #00ff41;'>// FINANCIAL_INTELLIGENCE: {ticker}</h1>", unsafe_allow_html=True)

# 3. FORECASTS (TECHY METRICS)
st.markdown("<p class='stat-header'>// ANALYST_TARGETS_v46</p>", unsafe_allow_html=True)
f1, f2, f3 = st.columns(3)

target = info.get('targetMedianPrice', 0)
current = info.get('currentPrice', 1)
upside = ((target / current) - 1) * 100 if target else 0

with st.container():
    f1.metric("EST_VALUE", f"${target}", delta=f"{upside:.2f}%")
    f2.metric("RECO_KEY", info.get('recommendationKey', 'N/A').upper())
    f3.metric("ANALYST_COUNT", info.get('numberOfAnalystOpinions', '0'))

# 4. MAJESTIC FINANCIAL STATEMENTS
st.markdown("<p class='stat-header'>// CORE_FINANCIAL_MATRIX</p>", unsafe_allow_html=True)

# Use st.tabs with techy labels
tab1, tab2, tab3 = st.tabs(["INCOME_MTX", "BALANCE_MTX", "CASH_FLOW_MTX"])

with tab1:
    # Transpose and clean for a vertical "App-like" scroll
    income = stock.income_stmt.transpose()
    st.data_editor(income, use_container_width=True, disabled=True, hide_index=False)

with tab2:
    st.data_editor(stock.balance_sheet.transpose(), use_container_width=True, disabled=True)

with tab3:
    st.data_editor(stock.cashflow.transpose(), use_container_width=True, disabled=True)
