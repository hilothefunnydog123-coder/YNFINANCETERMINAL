import streamlit as st
import yfinance as yf
import datetime

# --- 1. FAST CACHING LOGIC ---
@st.cache_data(ttl=600) # Cache for 10 mins so it's instant after the first load
def fetch_fast_news(ticker):
    stock = yf.Ticker(ticker)
    return stock.news

# --- 2. MAJESTIC NEWS CSS ---
st.markdown("""
<style>
    .news-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 255, 65, 0.1);
        padding: 20px; border-radius: 15px;
        margin-bottom: 15px; transition: 0.3s;
        cursor: pointer; display: block; text-decoration: none;
    }
    .news-card:hover {
        background: rgba(0, 255, 65, 0.07);
        border: 1px solid #00ff41;
        transform: translateX(5px);
    }
    .source-tag { color: #00ff41; font-weight: bold; font-size: 12px; text-transform: uppercase; }
    .news-title { color: #fff; font-size: 18px; font-weight: 600; margin: 5px 0; }
    .news-meta { color: #888; font-size: 11px; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

ticker = st.session_state.get('ticker', 'NVDA')
st.markdown(f"<h1 style='color:#00ff41;'>// SIGNAL_FEED: {ticker}</h1>", unsafe_allow_html=True)

with st.spinner("SYNCING_GLOBAL_FEEDS..."):
    news_items = fetch_fast_news(ticker)

if news_items:
    for item in news_items:
        # Converting timestamp to a readable signal
        pub_time = datetime.datetime.fromtimestamp(item['providerPublishTime']).strftime('%H:%M | %Y-%m-%d')
        
        st.markdown(f"""
            <a href="{item['link']}" target="_blank" class="news-card">
                <div class="source-tag">{item['publisher']}</div>
                <div class="news-title">{item['title']}</div>
                <div class="news-meta">TIMESTAMP: {pub_time} // TYPE: {item['type']}</div>
            </a>
        """, unsafe_allow_html=True)
else:
    st.error("NO_NEWS_SIGNALS_DETECTED")
