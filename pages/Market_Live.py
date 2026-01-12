import streamlit as st
import requests

ALPHA_VANTAGE_KEY = "YHXXV65N36WSEMAF"
ticker = st.session_state.ticker

# Category 2: Real-time Market Data
url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={ALPHA_KEY}"
data = requests.get(url).json().get("Global Quote", {})

st.metric("LAST_PRICE", f"${data.get('05. price', '0.00')}")
st.metric("CHANGE", data.get('10. change percent', '0%'))
