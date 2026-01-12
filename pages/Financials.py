import streamlit as st
import requests
import pandas as pd

st.title(f"// FINANCIAL_MATRIX: {st.session_state.ticker}")
FMP_KEY = st.secrets["FMP_KEY"]

# Category 5: Fundamental Statements
url = f"https://financialmodelingprep.com/api/v3/income-statement/{st.session_state.ticker}?period=quarter&limit=10&apikey={FMP_KEY}"
financials = requests.get(url).json()

df = pd.DataFrame(financials)
st.markdown("### // QUARTERLY_INCOME_STATEMENT")
st.dataframe(df[['date', 'revenue', 'netIncome', 'epsBasic']])

# Category 6: Ratios
st.markdown("### // CORE_RATIOS")
st.write(f"**P/E Ratio:** {df['epsBasic'].iloc[0]}") # Simple logic example
