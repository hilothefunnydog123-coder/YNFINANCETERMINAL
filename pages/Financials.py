import streamlit as st
import requests
import pandas as pd

# 1. SECURE KEY RETRIEVAL
try:
    FMP_KEY = st.secrets["FMP_KEY"]
    ticker = st.session_state.ticker
except KeyError:
    st.error("SECRET_ERROR: 'FMP_KEY' not found in Streamlit Secrets.")
    st.stop()

# 2. DATA FETCHING WITH ERROR HANDLING
url = f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?period=quarter&limit=10&apikey={FMP_KEY}"
response = requests.get(url)
data = response.json()

# 3. SAFETY GATE: Check if data is a list
if isinstance(data, list) and len(data) > 0:
    # SUCCESS: Data is a list of quarters, Pandas handles this automatically
    financials = pd.DataFrame(data)
    st.title(f"// FINANCIAL_MATRIX: {ticker}")
    st.dataframe(financials[['date', 'revenue', 'netIncome', 'eps']])
else:
    # FAILURE: API likely returned an error dictionary or empty list
    st.error(f"API_ERROR: Could not fetch data for {ticker}. Verify your FMP Key or Ticker.")
    if isinstance(data, dict):
        st.write("Server Message:", data.get("Error Message", "Unknown Error"))
