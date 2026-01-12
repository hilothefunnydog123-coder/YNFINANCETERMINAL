import streamlit as st
import requests
import google.generativeai as genai
import yfinance as yf

# 1. AUTHENTICATION & TICKER
try:
    FMP_KEY = st.secrets["FMP_KEY"]
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    ticker = st.session_state.get('ticker', 'NVDA')
except KeyError:
    st.error("SYSTEM_OFFLINE: Missing API keys in Secrets.")
    st.stop()

st.title(f"// MACRO_INTELLIGENCE: {ticker}")

# 2. THE HYBRID DATA BRIDGE
@st.cache_data(ttl=1800)
def fetch_news_stream(symbol):
    # Try Institutional Stream (FMP) first
    fmp_url = f"https://financialmodelingprep.com/api/v3/stock_news?tickers={symbol}&limit=10&apikey={FMP_KEY}"
    try:
        res = requests.get(fmp_url).json()
        if isinstance(res, list) and len(res) > 0:
            return res, "FMP_PRO_WIRE"
    except:
        pass

    # Fallback to Public Stream (yfinance)
    try:
        yf_news = yf.Ticker(symbol).news
        formatted_news = []
        for n in yf_news[:10]:
            formatted_news.append({
                'title': n.get('title'),
                'text': n.get('publisher', 'Public Stream'),
                'url': n.get('link'),
                'site': 'Yahoo Finance'
            })
        if formatted_news:
            return formatted_news, "YF_BACKUP_WIRE"
    except:
        pass
        
    return [], "NO_ACTIVE_STREAMS"

# 3. GEMINI 3.0 ANALYSIS
def get_ai_sentiment(news_list):
    if not news_list: return "NO_DATA_TO_ANALYZE"
    
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    context = "\n".join([f"HEADLINE: {n.get('title')}" for n in news_list])
    prompt = f"Analyze these 10 news items for {ticker}. Provide a Sentiment Score (0-100) and a brief Trade Thesis."
    
    try:
        return model.generate_content(prompt).text
    except:
        return "AI_OFFLINE"

# 4. RENDER UI
news, source = fetch_news_stream(ticker)
st.caption(f"SIGNAL_SOURCE: {source}")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### // LIVE_WIRE")
    if news:
        for item in news:
            st.markdown(f"""
            <div style="border-left: 2px solid #00ff41; padding-left: 10px; margin-bottom: 15px;">
                <a href="{item.get('url')}" style="color:#00ff41; text-decoration:none; font-weight:bold;">{item.get('title')}</a>
                <p style="color:gray; font-size:12px;">{item.get('site', 'Finance Wire')}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("ALL_STREAMS_OFFLINE: Verify Symbol or API Limits.")

with col2:
    st.markdown("### // AI_BRIEFING")
    if news:
        with st.spinner("SYNTHESIZING..."):
            st.info(get_ai_sentiment(news))
