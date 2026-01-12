import streamlit as st
import requests
import pandas as pd
# RIGHT: Use the name of the variable you wrote in your secrets.toml
FMP_KEY = st.secrets["FMP_KEY"]
ticker = st.session_state.ticker

# Category 5: Fundamentals
url = f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?period=quarter&apikey={FMP_KEY}"
financials = pd.DataFrame(requests.get(url).json())
st.dataframe(financials[['date', 'revenue', 'netIncome']])
