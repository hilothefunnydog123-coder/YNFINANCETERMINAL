import streamlit as st
import requests
import pandas as pd

FMP_KEY = st.secrets["Ksd4nUJfWMKAGWgLJQBpgmpprBfWKILp"]
ticker = st.session_state.ticker

# Category 5: Fundamentals
url = f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?period=quarter&apikey={FMP_KEY}"
financials = pd.DataFrame(requests.get(url).json())
st.dataframe(financials[['date', 'revenue', 'netIncome']])
