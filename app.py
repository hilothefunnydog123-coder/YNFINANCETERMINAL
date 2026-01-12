import streamlit as st
import yfinance as yf
import requests
import google.generativeai as genai

st.set_page_config(layout="wide", page_title="SOVEREIGN_V45_PLATFORM")

# --- 0. SECURE KEY INJECTION ---
try:
    FMP_KEY = st.secrets["FMP_KEY"]
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
except:
    st.error("SYSTEM_OFFLINE: Configure Secrets first.")
    st.stop()

# --- 1. HUD & GLOBAL STATE ---
if 'ticker' not in st.session_state: st.session_state.ticker = "NVDA"

with st.sidebar:
    st.title("SOVEREIGN_V45")
    t_input = st.text_input("SET_ACTIVE_SYMBOL", value=st.session_state.ticker).upper()
    if t_input != st.session_state.ticker:
        st.session_state.ticker = t_input
        st.rerun()

# --- 2. CATEGORY 1: SECURITY IDENTIFICATION ---
@st.cache_data(ttl=3600)
def fetch_ident_data(ticker):
    # FMP is the 'Gold' source for IDs (ISIN, CUSIP, FIGI)
    url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={FMP_KEY}"
    try:
        data = requests.get(url).json()[0]
        return data
    except:
        return yf.Ticker(ticker).info

profile = fetch_ident_data(st.session_state.ticker)

# --- 3. MAJESTIC LAYOUT ---
l, r = st.columns([1, 2])
with l:
    st.markdown("### // IDENTIFICATION")
    st.table({
        "Ticker": profile.get('symbol'),
        "ISIN": profile.get('isin', 'N/A'),
        "CUSIP": profile.get('cusip', 'N/A'),
        "Exchange": profile.get('exchangeShortName'),
        "Sector": profile.get('sector'),
        "Industry": profile.get('industry'),
        "Currency": profile.get('currency')
    })

with r:
    st.markdown("### // SOVEREIGN_GAZETTE")
    # Category 20: Proprietary AI Insight
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"Write a professional Bloomberg Intelligence report for {st.session_state.ticker}. Summary of risk, current sentiment, and valuation roasts."
    if st.button("GENERATE_INTELLIGENCE"):
        response = model.generate_content(prompt)
        st.write(response.text)
