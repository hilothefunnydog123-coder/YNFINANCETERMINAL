import streamlit as st
import yfinance as yf
import datetime

# --- 1. INSTANT BROADCAST CACHE ---
@st.cache_data(ttl=300)
def fetch_newspaper_feed(ticker):
    try:
        return yf.Ticker(ticker).news
    except:
        return []

# --- 2. NEWSPAPER TYPOGRAPHY & GRID ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Source+Sans+Pro:wght@400;700&display=swap');
    
    .newspaper-container {
        column-count: 2; /* Creates traditional newspaper columns */
        column-gap: 40px;
        column-rule: 1px solid rgba(255, 255, 255, 0.1);
    }
    .article-block {
        break-inside: avoid;
        margin-bottom: 30px;
        padding-bottom: 20px;
        border-bottom: 1px double rgba(255, 255, 255, 0.2);
    }
    .masthead {
        font-family: 'Playfair Display', serif;
        font-size: 4rem; text-align: center;
        border-bottom: 4px double #00ff41;
        margin-bottom: 40px; color: #00ff41;
    }
    .headline {
        font-family: 'Playfair Display', serif;
        font-size: 1.6rem; line-height: 1.2;
        color: #ffffff; text-decoration: none;
    }
    .headline:hover { color: #00ff41; }
    .dateline {
        font-family: 'Source Sans Pro', sans-serif;
        font-size: 0.8rem; color: #00ff41;
        text-transform: uppercase; margin-bottom: 8px;
    }
    .excerpt {
        font-family: 'Source Sans Pro', sans-serif;
        font-size: 1rem; color: #bbb; line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

ticker = st.session_state.get('ticker', 'NVDA')
st.markdown(f"<div class='masthead'>THE {ticker} GAZETTE</div>", unsafe_allow_html=True)

# --- 3. THE FEED ---
news_data = fetch_newspaper_feed(ticker)

if news_data:
    st.markdown("<div class='newspaper-container'>", unsafe_allow_html=True)
    for i, item in enumerate(news_data):
        source = item.get('publisher', 'WIRE_SERVICE')
        title = item.get('title', 'Headline Encrypted')
        link = item.get('link', '#')
        
        # Safe time formatting
        raw_ts = item.get('providerPublishTime')
        dt_str = datetime.datetime.fromtimestamp(raw_ts).strftime('%b %d, %Y') if raw_ts else "MARKET_TIME"

        st.markdown(f"""
            <div class='article-block'>
                <div class='dateline'>{source} // {dt_str}</div>
                <a href='{link}' target='_blank' class='headline'>{title}</a>
                <div class='excerpt'>Analyzing market shifts for {ticker}. Detailed intelligence available via link.</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
