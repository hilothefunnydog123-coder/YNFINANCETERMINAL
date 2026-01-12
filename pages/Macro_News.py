import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import plotly.graph_objects as go

# --- 1. PAGE CONFIG & SECRETS ---
st.set_page_config(layout="wide", page_title="MACRO_PULSE")

# Ensure the app doesn't crash if the user hasn't set a ticker in app.py
if 'ticker' not in st.session_state:
    st.session_state.ticker = "NVDA"

try:
    ALPHA_KEY = st.secrets["ALPHA_VANTAGE_KEY"]
except KeyError:
    st.error("SECRET_ERROR: 'ALPHA_VANTAGE_KEY' not found in Streamlit Secrets.")
    st.stop()

ticker = st.session_state.ticker
st.title(f"// MACRO_PULSE_WIRE: {ticker}")

# --- 2. DATA ENGINE: MACRO & NEWS ---
@st.cache_data(ttl=3600)
def fetch_macro_data(api_key):
    # Category 12: Consumer Price Index (CPI) - Inflation Data
    cpi_url = f"https://www.alphavantage.co/query?function=CPI&interval=semiannual&apikey={api_key}"
    # Category 12: Federal Funds Rate
    ir_url = f"https://www.alphavantage.co/query?function=FEDERAL_FUNDS_RATE&interval=monthly&apikey={api_key}"
    
    try:
        cpi_res = requests.get(cpi_url).json()
        ir_res = requests.get(ir_url).json()
        return cpi_res, ir_res
    except:
        return None, None

cpi_data, ir_data = fetch_macro_data(ALPHA_KEY)

# --- 3. MAJESTIC VISUALIZATION (Category 12) ---
st.markdown("### // GLOBAL_MACRO_INDICATORS")
col1, col2 = st.columns(2)

with col1:
    if cpi_data and "data" in cpi_data:
        df_cpi = pd.DataFrame(cpi_data["data"])
        fig_cpi = go.Figure(data=[go.Scatter(x=df_cpi['date'], y=df_cpi['value'], line=dict(color='#00ff41', width=3))])
        fig_cpi.update_layout(template="plotly_dark", title="US CPI (Inflation Trend)", height=300)
        st.plotly_chart(fig_cpi, use_container_width=True)
    else:
        st.warning("CPI_DATA_THROTTLED")

with col2:
    if ir_data and "data" in ir_data:
        df_ir = pd.DataFrame(ir_data["data"])
        fig_ir = go.Figure(data=[go.Scatter(x=df_ir['date'], y=df_ir['value'], line=dict(color='#00f0ff', width=3))])
        fig_ir.update_layout(template="plotly_dark", title="Fed Funds Rate", height=300)
        st.plotly_chart(fig_ir, use_container_width=True)
    else:
        st.warning("INTEREST_RATE_DATA_THROTTLED")

[Image of a professional real-time financial news terminal showing scrolling headlines and sentiment indicators]

# --- 4. THE NEWS WIRE (Category 15 & 16) ---
st.markdown("### // LIVE_NEWS_FEED")

# Defensive News Rendering Loop
news_data = yf.Ticker(ticker).news

if news_data:
    for item in news_data[:10]:
        # .get() prevents KeyError if fields are missing
        title = item.get('title', 'Headline Unavailable')
        link = item.get('link', '#')
        publisher = item.get('publisher', 'FINANCIAL WIRE')
        
        # Build the majestic news card
        st.markdown(f"""
            <div style="border-left: 2px solid #00ff41; padding-left: 15px; margin-bottom: 25px;">
                <p style="font-size: 11px; color: #00f0ff; letter-spacing: 1px; margin-bottom: 4px;">{publisher.upper()}</p>
                <a href="{link}" target="_blank" style="text-decoration: none; color: #ffffff; font-weight: bold; font-size: 16px;">
                    {title}
                </a>
            </div>
        """, unsafe_allow_html=True)
else:
    st.info("NO_NEWS_DATA_STREAMING: Check back later or verify symbol.")

# --- 5. ESG INSIGHT (Category 16) ---
with st.expander("// VIEW_ESG_SUSTAINABILITY_SCORES"):
    esg_data = yf.Ticker(ticker).sustainability
    if esg_data is not None:
        st.dataframe(esg_data, use_container_width=True)
    else:
        st.info("ESG_DATA_NOT_REPORTED_FOR_THIS_SYMBOL")
