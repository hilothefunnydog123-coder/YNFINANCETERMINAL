import streamlit as st
import yfinance as yf
import pandas as pd

# 1. TECHY CSS INJECTION (The "Startup" Look)
st.markdown("""
    <style>
    /* Glassmorphism Card Effect */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 255, 65, 0.2);
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(5px);
    }
    /* Techy Sidebar/Header Style */
    .stat-header {
        color: #00f0ff;
        font-family: 'Courier New', monospace;
        letter-spacing: 1px;
        border-left: 3px solid #00f0ff;
        padding-left: 10px;
        margin-top: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. DATA INITIALIZATION
ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)
info = stock.info

st.markdown(f"<h1 style='color: #00ff41;'>// FINANCIAL_CORE_INTELLIGENCE: {ticker}</h1>", unsafe_allow_html=True)

# 3. ANALYSIS & FORECASTS (The "Impressive" Section)
st.markdown("<p class='stat-header'>// ANALYST_CONSENSUS_ENGINE</p>", unsafe_allow_html=True)
f1, f2, f3, f4 = st.columns(4)

# Professional Defensive Logic
target = info.get('targetMedianPrice') or info.get('targetMeanPrice') or 0
current = info.get('currentPrice') or info.get('regularMarketPrice') or 1
upside = ((target / current) - 1) * 100 if target else 0

with st.container():
    f1.metric("EST_TARGET", f"${target:,.2f}", delta=f"{upside:.2f}%")
    f2.metric("RECO_KEY", info.get('recommendationKey', 'N/A').upper())
    f3.metric("ANALYSTS", info.get('numberOfAnalystOpinions', '0'))
    f4.metric("PE_RATIO", f"{info.get('trailingPE', 0):.2f}")

# 4. DATA MATRIX (MAJESTIC TABS)
st.markdown("<p class='stat-header'>// CORE_FINANCIAL_MATRICES</p>", unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["INCOME_MTX", "BALANCE_MTX", "CASH_FLOW_MTX"])

def style_df(df):
    # Transpose so dates are rows and line items are columns (App-like look)
    return df.transpose().style.format(precision=0, thousands=",")

with tab1:
    st.write("### [INCOME_STATEMENT_HISTORY]")
    st.dataframe(style_df(stock.income_stmt), use_container_width=True)

with tab2:
    st.write("### [BALANCE_SHEET_SNAPSHOT]")
    st.dataframe(style_df(stock.balance_sheet), use_container_width=True)

with tab3:
    st.write("### [CASH_FLOW_BRIDGE]")
    st.dataframe(style_df(stock.cashflow), use_container_width=True)
