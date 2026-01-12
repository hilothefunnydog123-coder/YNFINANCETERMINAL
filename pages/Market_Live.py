import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# 1. RETRIEVE THE SECRET FOR THIS SPECIFIC PAGE
try:
    ALPHA_KEY = st.secrets["ALPHA_VANTAGE_KEY"]
    ticker = st.session_state.ticker
except KeyError:
    st.error("SECRET_ERROR: 'ALPHA_VANTAGE_KEY' not found in Secrets.")
    st.stop()

st.title(f"// MARKET_LIVE: {ticker}")

# 2. FETCH REAL-TIME QUOTE
url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={ALPHA_KEY}"
response = requests.get(url)
raw_data = response.json()

# 3. SAFETY GATE: Handle API Throttling or Errors
if "Global Quote" in raw_data and raw_data["Global Quote"]:
    quote = raw_data["Global Quote"]
    
    # Majestic HUD Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("LAST_PRICE", f"${float(quote['05. price']):,.2f}")
    c2.metric("CHANGE", quote['10. change percent'], delta=quote['09. change'])
    c3.metric("VOLUME", f"{int(quote['06. volume']):,}")

    st.markdown("---")
    # Category 2: VWAP & High/Low Data Grid
    st.write(f"**Opening:** ${quote['02. open']} | **High:** ${quote['03. high']} | **Low:** ${quote['04. low']}")
else:
    # This happens if you hit the 5-calls-per-minute limit
    st.warning("API_LIMIT_REACHED: Alpha Vantage is throttled. Please wait 60 seconds.")
    if "Information" in raw_data:
        st.info(raw_data["Information"])
