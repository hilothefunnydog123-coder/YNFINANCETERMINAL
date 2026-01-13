import streamlit as st
import yfinance as yf
import pandas as pd

# 1. THE UNIVERSAL SIGNAL DECRYPTOR
def decrypt_signal(data):
    # Check if it's a dictionary (like stock.info)
    if isinstance(data, dict):
        if not data: return None
        # Convert dict to a clean DataFrame for the deep-dive matrix
        return pd.DataFrame.from_dict(data, orient='index', columns=['Value'])
    
    # Check if it's a DataFrame (like income_stmt)
    if isinstance(data, pd.DataFrame):
        if data.empty: return None
        # Peel the 2026 Multi-Index layer if present
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(-1)
        return data
    
    return None

ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)

st.markdown(f"<h1>// FINANCIAL_MAINFRAME: {ticker}</h1>", unsafe_allow_html=True)

# 2. THE MAJESTIC BLADE ENGINE
def render_blade(raw_data, label):
    df = decrypt_signal(raw_data)
    if df is not None:
        with st.container(border=True):
            st.markdown(f"### // {label}_SURVEILLANCE")
            
            # Show a summary chart for DataFrames, or a metric for Info
            if df.shape[1] > 1: # It's a time-series table
                st.area_chart(df.iloc[0], color="#00ff41")
            else: # It's a Ratio list
                st.metric(label, f"{len(df)} DATA_POINTS", "STABLE")
            
            # THE DEEP-DIVE TRIGGER
            if st.button(f"CLICK_HERE_FOR_{label}_DATA", use_container_width=True):
                st.session_state.deep_dive_data = df
                st.session_state.deep_dive_label = label
                st.switch_page("pages/99_Data_View.py")
    else:
        st.error(f"SIGNAL_ENCRYPTED: {label} is returning no data.")

# 3. THE TABS (EVERYTHING NOW LOADS)
t1, t2, t3, t4, t5 = st.tabs(["INCOME", "BALANCE", "CASH_FLOW", "RATIOS", "ESG"])

with t1: render_blade(stock.income_stmt, "INCOME")
with t2: render_blade(stock.balance_sheet, "BALANCE")
with t3: render_blade(stock.cashflow, "CASH_FLOW")
with t4: render_blade(stock.info, "RATIO_MTX")      # FIXED: No more AttributeError
with t5: render_blade(stock.sustainability, "ESG")  # FIXED
