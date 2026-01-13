import streamlit as st
import yfinance as yf

# Global majestic theme logic
st.set_page_config(layout="wide", page_title="SOVEREIGN_V46")

if 'ticker' not in st.session_state:
    st.session_state.ticker = "NVDA"

st.sidebar.title("COMMAND_CENTER")
st.session_state.ticker = st.sidebar.text_input("SET_ACTIVE_SYMBOL", value=st.session_state.ticker).upper()

# --- CATEGORY 1: SECURITY IDENTIFICATION ---
st.markdown(f"<h1 style='color: #00ff41;'>// SECURITY_MASTER: {st.session_state.ticker}</h1>", unsafe_allow_html=True)

stock = yf.Ticker(st.session_state.ticker)
info = stock.info

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.write("**PRIMARY_IDS**")
    st.code(f"Ticker: {st.session_state.ticker}\nISIN: {info.get('isin')}\nCUSIP: {info.get('cusip')}")
with col2:
    st.write("**EXCHANGE_DATA**")
    st.code(f"Exchange: {info.get('exchange')}\nMIC: {info.get('exchangeTimezoneName')}\nCurrency: {info.get('currency')}")
with col3:
    st.write("**ASSET_CLASS**")
    st.code(f"Type: {info.get('quoteType')}\nSector: {info.get('sector')}\nCountry: {info.get('country')}")
with col4:
    st.write("**PROPRIETARY_SCORES (Cat 20)**")
    st.metric("LIQUIDITY", "HIGH", "98.2")
    st.metric("B_FAIR_VALUE", f"${info.get('targetMedianPrice')}")
