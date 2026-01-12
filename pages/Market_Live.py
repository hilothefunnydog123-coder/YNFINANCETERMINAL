import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

st.title(f"// MARKET_LIVE: {st.session_state.ticker}")

# Category 2 & 3: Real-time and Intraday Prices
data = yf.download(st.session_state.ticker, period="1d", interval="1m")

fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
fig.update_layout(template="plotly_dark", title="1-Minute Intraday Flux")
st.plotly_chart(fig, use_container_width=True)

# Metric Grid
c1, c2, c3 = st.columns(3)
c1.metric("LAST_PRICE", f"${data['Close'].iloc[-1]:.2f}")
c2.metric("VWAP", "CALCULATING...")
c3.metric("HALT_STATUS", "NOMINAL")
