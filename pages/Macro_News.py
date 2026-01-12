import streamlit as st
import yfinance as yf

# 1. PAGE SETUP
st.set_page_config(layout="wide")
st.title("// MACRO_PULSE_WIRE")

# 2. SESSION STATE SYNC
ticker_symbol = st.session_state.get('ticker', 'NVDA')

# 3. ROBUST NEWS FETCHING
st.markdown(f"### // LIVE_NEWS_STREAM: {ticker_symbol}")

try:
    ticker_obj = yf.Ticker(ticker_symbol)
    # yf.Ticker(ticker).news returns a list of dictionaries
    news_list = ticker_obj.news
    
    if news_list:
        for item in news_list[:10]:
            # Use .get() to safely check for keys without crashing
            title = item.get('title') or item.get('headline')
            link = item.get('link', '#')
            publisher = item.get('publisher', 'FINANCIAL_WIRE')
            
            # Skip entries that have no usable title
            if not title:
                continue

            # RENDER: Majestic High-Density Card
            with st.container():
                # Display Publisher in cyan, Title as a neon green link
                st.markdown(f"<span style='color: #00f0ff; font-size: 10px;'>{publisher.upper()}</span>", unsafe_allow_html=True)
                st.markdown(f"#### [{title}]({link})")
                st.markdown("---")
    else:
        st.info("SYSTEM_IDLE: No recent headlines found in the Yahoo data stream.")

except Exception as e:
    st.error(f"STREAM_ERROR: Connection to news bridge failed. {e}")
