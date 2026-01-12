import streamlit as st
import requests
import google.generativeai as genai

# 1. CORE AUTH
try:
    FMP_KEY = st.secrets["FMP_KEY"]
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    ticker = st.session_state.get('ticker', 'NVDA')
except KeyError:
    st.error("SYSTEM_OFFLINE: Rename folder to .streamlit and add keys.")
    st.stop()

st.title(f"// MACRO_INTELLIGENCE: {ticker}")

# 2. THE 2026 DATA BRIDGE (FMP + REQUISITION)
@st.cache_data(ttl=600)
def fetch_verified_news(symbol, api_key):
    # Using the 'stable' v3 endpoint which is the most reliable in 2026
    url = f"https://financialmodelingprep.com/api/v3/stock_news?tickers={symbol}&limit=10&apikey={api_key}"
    try:
        response = requests.get(url)
        data = response.json()
        # Ensure we got a list, not an error dict
        return data if isinstance(data, list) else []
    except:
        return []

# 3. AI ANALYTICS ENGINE
def generate_ai_alpha(news_items):
    if not news_items: return "NO_SIGNAL_FOUND"
    
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Feeding the 'text' snippet from FMP is 10x better than just titles
    context = "\n".join([f"HEADLINE: {n.get('title')}\nSUMMARY: {n.get('text')}" for n in news_items])
    prompt = f"Analyze these news items for {ticker}. Provide: 1. Sentiment Score (0-100) 2. Key Risk 3. Trade Verdict."
    
    try:
        return model.generate_content(prompt).text
    except:
        return "AI_THROTTLED"

# 4. MAJESTIC UI
news_data = fetch_verified_news(ticker, FMP_KEY)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### // LIVE_WIRE")
    if news_data:
        for n in news_data:
            st.markdown(f"""
            <div style="border-left: 3px solid #00ff41; padding-left: 10px; margin-bottom: 20px;">
                <p style="color:#00f0ff; font-size:10px;">{n.get('site', 'WIRE')}</p>
                <a href="{n.get('url')}" target="_blank" style="color:white; text-decoration:none; font-weight:bold;">{n.get('title')}</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("DATA_STREAM_EMPTY: Verify FMP_KEY or Ticker.")

with col2:
    st.markdown("### // AI_ANALYTICS")
    if news_data:
        with st.spinner("SYNTHESIZING..."):
            st.info(generate_ai_alpha(news_data))
