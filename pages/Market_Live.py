import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime

# 1. INITIALIZATION & SESSION SAFETY
if 'ticker' not in st.session_state:
    st.session_state.ticker = "NVDA"

ticker = st.session_state.ticker

# 2. SECURE API RETRIEVAL
try:
    ALPHA_KEY = st.secrets["ALPHA_VANTAGE_KEY"]
except KeyError:
    st.error("SECRET_ERROR: 'ALPHA_VANTAGE_KEY' not found in Secrets.")
    st.stop()

# 3. REAL-TIME PULSE ENGINE (Alpha Vantage)
def fetch_realtime_pulse(symbol, api_key):
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
    try:
        data = requests.get(url).json().get("Global Quote", {})
        return data
    except:
        return {}

# 4. INSTITUTIONAL CHARTING ENGINE (yfinance + Plotly)
def get_candlestick_chart(symbol):
    # Fetch 1-day intraday data with 5-minute intervals
    df = yf.download(symbol, period="1d", interval="5min")
    
    if df.empty:
        return None

    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name="MARKET_PRICE"
    )])
    
    fig.update_layout(
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        height=500,
        margin=dict(l=0, r=0, t=30, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig

# 5. MAJESTIC UI RENDERING
st.title(f"// MARKET_LIVE_PULSE: {ticker}")

pulse = fetch_realtime_pulse(ticker, ALPHA_KEY)

# High-Density Metric Row
c1, c2, c3, c4 = st.columns(4)
if pulse:
    price = float(pulse.get('05. price', 0))
    change = pulse.get('10. change percent', '0%')
    high = pulse.get('03. high', '0')
    low = pulse.get('04. low', '0')
    
    c1.metric("LAST_PRICE", f"${price:,.2f}", delta=change)
    c2.metric("SESSION_HIGH", f"${float(high):,.2f}")
    c3.metric("SESSION_LOW", f"${float(low):,.2f}")
    c4.metric("VOLUME", pulse.get('06. volume', '0'))
else:
    st.warning("API_THROTTLED: Real-time pulse waiting for refresh.")

st.markdown("---")

# Main Chart Workspace
st.markdown("### // INTRADAY_CANDLESTICK_V5")
chart_fig = get_candlestick_chart(ticker)

if chart_fig:
    st.plotly_chart(chart_fig, use_container_width=True)
else:
    st.info("DATA_LOADING: Initializing intraday stream...")

# 6. TECHNICAL TAPE
with st.expander("// VIEW_ORDER_BOOK_TAPE"):
    raw_data = yf.download(ticker, period="1d", interval="1m").tail(10)
    st.dataframe(raw_data, use_container_width=True)
