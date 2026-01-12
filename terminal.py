import streamlit as st
import yfinance as yf

# Standard Platform Setup
st.set_page_config(layout="wide", page_title="SOVEREIGN_V46_PLATFORM")

# Secure Secret Retrieval
try:
    FMP_KEY = st.secrets["FMP_KEY"]
except:
    st.error("SYSTEM_OFFLINE: FMP_KEY missing in Secrets.")
    st.stop()

# Persistent Global State
if 'ticker' not in st.session_state: st.session_state.ticker = "NVDA"

st.title("// SOVEREIGN_IDENTIFICATION_CORE")
# Identification Logic (Category 1)
ticker_input = st.sidebar.text_input("SET_ACTIVE_SYMBOL", value=st.session_state.ticker).upper()
if ticker_input != st.session_state.ticker:
    st.session_state.ticker = ticker_input
    st.rerun()

info = yf.Ticker(st.session_state.ticker).info
st.write(f"**Security Name:** {info.get('longName')}")
st.write(f"**ISIN:** {info.get('isin', 'N/A')}")
