import streamlit as st
import yfinance as yf
import datetime

# --- 1. INSTANT CACHING ENGINE ---
@st.cache_data(ttl=300) # Data stays fresh for 5 mins, loads INSTANTLY after first fetch
def get_clean_news(ticker):
    try:
        sn = yf.Ticker(ticker)
        return sn.news
    except:
        return []

# --- 2. TERMINAL GLASS STYLING ---
st.markdown("""
<style>
    .news-container {
        display: grid;
        grid-template-columns: 1fr;
        gap: 10px;
    }
    .news-card {
        background: rgba(0, 255, 65, 0.02);
        border: 1px solid rgba(0, 255, 65, 0.1);
        padding: 15px;
        border-radius: 12px;
        transition: 0.3s ease;
        text-decoration: none !important;
        display: block;
    }
    .news-card:hover {
        background: rgba(0, 255, 65, 0.08);
        border-color: #00ff41;
        transform: translateX(8px);
    }
    .news-source { color: #00ff41; font-size: 10px; font-weight: 800; letter-spacing: 1px; }
    .news-headline { color: #ffffff; font-size: 16px; font-weight: 500; margin: 4px 0; }
    .news-time { color: #555; font-size: 10px; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

ticker = st.session_state.get('ticker', 'NVDA')
st.markdown(f"<h1 style='color:#00ff41;'>// NEWS_STREAM: {ticker}</h1>", unsafe_allow_html=True)

# --- 3. EXECUTION ---
with st.spinner("INTERCEPTING_GLOBAL_SIGNALS..."):
    news_data = get_clean_news(ticker)

if news_data:
    st.markdown("<div class='news-container'>", unsafe_allow_html=True)
    for item in news_data:
        # DEFENSIVE KEY CHECK (Fixes the KeyError)
        source = item.get('publisher', 'REDACTED_SOURCE')
        headline = item.get('title', 'SIGNAL_DECRYPT_FAILURE')
        link = item.get('link', '#')
        
        # Safe time conversion
        raw_ts = item.get('providerPublishTime')
        if raw_ts:
            dt = datetime.datetime.fromtimestamp(raw_ts)
            time_str = dt.strftime('%H:%M // %Y-%m-%d')
        else:
            time_str = "TIMESTAMP_UNKNOWN"

        st.markdown(f"""
            <a href="{link}" target="_blank" class="news-card">
                <div class="news-source">{source}</div>
                <div class="news-headline">{headline}</div>
                <div class="news-time">{time_str}</div>
            </a>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.warning("SIGNAL_SILENT: No recent news detected for this asset.")
