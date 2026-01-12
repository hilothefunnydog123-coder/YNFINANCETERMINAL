import streamlit as st
import yfinance as yf
import requests

st.title("// MACRO_PULSE_WIRE")
ALPHA_KEY = st.secrets["ALPHA_VANTAGE_KEY"]

# Category 12: Macro (CPI/GDP)
macro_url = f"https://www.alphavantage.co/query?function=CPI&interval=semiannual&apikey={ALPHA_KEY}"
cpi_data = requests.get(macro_url).json()

# Category 15: News Wire
st.markdown("### // LIVE_NEWS_FEED")
news = yf.Ticker(st.session_state.ticker).news
for item in news[:5]:
    st.write(f"**{item['publisher']}**: [{item['title']}]({item['link']})")
