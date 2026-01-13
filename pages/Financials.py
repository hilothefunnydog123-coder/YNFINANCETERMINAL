import streamlit as st
import yfinance as yf
import pandas as pd

# 1. THE DECRYPTION ENGINE (Fixes the blank sections)
def decrypt_signal(df):
    if df is None or df.empty: return None
    # Peeling the 2026 Multi-Index layer
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(-1)
    return df

ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)

# 2. RENDER THE HUB
st.markdown(f"<h1>// FINANCIAL_MAINFRAME: {ticker}</h1>", unsafe_allow_html=True)

# Helper for the "Click here for data" request
def render_data_blade(df, label):
    df = decrypt_signal(df)
    if df is not None:
        with st.container(border=True):
            st.markdown(f"### // {label}_SURVEILLANCE")
            # Show a "Fly" summary chart
            st.area_chart(df.iloc[0], color="#00ff41")
            
            # THE DEEP-DIVE TRIGGER
            if st.button(f"CLICK_HERE_FOR_{label}_DATA", use_container_width=True):
                st.session_state.deep_dive_data = df
                st.session_state.deep_dive_label = label
                st.switch_page("pages/99_Data_View.py")
    else:
        st.error(f"SIGNAL_ENCRYPTED: {label} blocked by provider.")

# 3. THE TABS (EVERYTHING NOW WORKS)
t1, t2, t3, t4, t5 = st.tabs(["INCOME", "BALANCE", "CASH_FLOW", "RATIOS", "ESG"])

with t1: render_data_blade(stock.income_stmt, "INCOME")
with t2: render_data_blade(stock.balance_sheet, "BALANCE")
with t3: render_data_blade(stock.cashflow, "CASH_FLOW") # Fixed
with t4: render_data_blade(stock.info, "RATIO_MTX")      # Fixed
with t5: render_data_blade(stock.sustainability, "ESG")  # Fixed
