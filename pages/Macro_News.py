import streamlit as st
import yfinance as yf

# Standard Header
st.title("NEWS_WIRE")

# Simple News Loop (No complex HTML)
ticker = st.session_state.get('ticker', 'NVDA')
news = yf.Ticker(ticker).news

if news:
    for item in news[:5]:
        title = item.get('title', 'No Title')
        link = item.get('link', '#')
        st.write(f"**{title}**")
        st.caption(f"[Read More]({link})")
