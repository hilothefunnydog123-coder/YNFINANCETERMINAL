import streamlit as st
import yfinance as yf

st.set_page_config(layout="wide", page_title="SOVEREIGN_V45")

# Sync the ticker across all pages using Session State
if 'ticker' not in st.session_state:
    st.session_state.ticker = "NVDA"

st.title("// SOVEREIGN_IDENTIFICATION_HUB")

# Global Ticker Input
ticker_input = st.sidebar.text_input("SET_ACTIVE_SYMBOL", value=st.session_state.ticker).upper()
if ticker_input != st.session_state.ticker:
    st.session_state.ticker = ticker_input
    st.rerun()

# Category 1: Identification Data
info = yf.Ticker(st.session_state.ticker).info
col1, col2 = st.columns(2)
with col1:
    st.markdown("### // SECURITY_KEYS")
    st.write(f"**Name:** {info.get('longName')}")
    st.write(f"**ISIN:** {info.get('isin', 'N/A')}")
    st.write(f"**Exchange:** {info.get('exchange')}")
with col2:
    st.markdown("### // CLASSIFICATION")
    st.write(f"**Sector:** {info.get('sector')}")
    st.write(f"**Asset Class:** Equity")
