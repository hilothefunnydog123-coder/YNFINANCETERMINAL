import streamlit as st
import yfinance as yf

# 1. Page Configuration
st.set_page_config(layout="wide")
st.title("// MACRO_PULSE_WIRE")

# 2. Get Global Ticker from Session State
# If not set, default to NVDA so the page doesn't crash
ticker_symbol = st.session_state.get('ticker', 'NVDA')

# 3. Fetch News Data
st.markdown(f"### // LIVE_NEWS: {ticker_symbol}")
try:
    ticker_obj = yf.Ticker(ticker_symbol)
    news_list = ticker_obj.news
    
    if news_list and len(news_list) > 0:
        for item in news_list[:10]: # Show top 10 news items
            # Use .get() to avoid KeyErrors if data is missing
            title = item.get('title')
            link = item.get('link', '#')
            publisher = item.get('publisher', 'Financial Wire')
            
            # If title is missing, use a placeholder or skip
            if not title:
                continue

            # Display in a clean, professional card format
            with st.container():
                st.markdown(f"**{publisher.upper()}**")
                st.markdown(f"[{title}]({link})")
                st.markdown("---")
    else:
        st.warning("SYSTEM_IDLE: No recent news found for this symbol.")

except Exception as e:
    st.error(f"STREAM_ERROR: Could not connect to news wire. {e}")
