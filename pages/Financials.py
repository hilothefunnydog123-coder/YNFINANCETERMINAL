import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# 1. SECURE KEY RETRIEVAL
try:
    FMP_KEY = st.secrets["FMP_KEY"]
    ticker = st.session_state.ticker
except KeyError:
    st.error("SECRET_ERROR: 'FMP_KEY' missing in Secrets.")
    st.stop()

# 2. UPDATED DATA ENGINE (STABLE ENDPOINT)
# We move from 'api/v3' to 'developer/docs/stable' as per new FMP protocol
url = f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?period=quarter&limit=10&apikey={FMP_KEY}"

# FIX: If the above v3 still fails, FMP now directs free users to the stable path:
stable_url = f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?period=quarter&limit=10&apikey={FMP_KEY}"

@st.cache_data(ttl=3600)
def fetch_financial_matrix(api_url):
    response = requests.get(api_url)
    data = response.json()
    
    # Check for the Legacy Error or Empty Response
    if isinstance(data, dict) and "Error Message" in data:
        return None, data["Error Message"]
    return pd.DataFrame(data), None

st.title(f"// FINANCIAL_MATRIX: {ticker}")
df, error_msg = fetch_startup_data(url)

# 3. RENDER LOGIC
if df is not None and not df.empty:
    # Display Quarterly Revenue
    fig = go.Figure(data=[
        go.Bar(x=df['date'], y=df['revenue'], name="REVENUE", marker_color='#00ff41'),
        go.Scatter(x=df['date'], y=df['netIncome'], name="NET_INCOME", line=dict(color='#ff00ff'))
    ])
    fig.update_layout(template="plotly_dark", title="Quarterly Growth Metrics")
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### // RAW_FINANCIAL_TAPE")
    st.dataframe(df[['date', 'revenue', 'costOfRevenue', 'grossProfit', 'netIncome', 'eps']])
else:
    st.error(f"UPGRADE_REQUIRED: {error_msg}")
    st.info("NOTE: FMP Free Tier sometimes requires the 'annual' period instead of 'quarter' for some tickers.")
