import streamlit as st
import requests
import google.generativeai as genai

# 1. CORE AUTHENTICATION
try:
    # Rename folder to .streamlit for these to work locally!
    FMP_KEY = st.secrets["FMP_KEY"]
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    ticker = st.session_state.get('ticker', 'NVDA')
except KeyError:
    st.error("SYSTEM_OFFLINE: Rename folder to .streamlit or add keys to Cloud Dashboard.")
    st.stop()

st.title(f"// MACRO_INTELLIGENCE: {ticker}")

# 2. STABLE NEWS BRIDGE (FMP)
@st.cache_data(ttl=600)
def fetch_institutional_news(symbol, api_key):
    # FMP v3 news endpoint provides clean JSON: title, text, and url
    url = f"https://financialmodelingprep.com/api/v3/stock_news?tickers={symbol}&limit=10&apikey={api_key}"
    try:
        response = requests.get(url)
        data = response.json()
        return data if isinstance(data, list) else []
    except:
        return []

# 3. AI ANALYTICS (GEMINI)
def analyze_market_alpha(news_items):
    if not news_items: return "NO_SIGNAL_DETECTED"
    
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Feeding full snippets (text) to Gemini, not just headlines
    context = "\n".join([f"HEADLINE: {n.get('title')}\nCONTEXT: {n.get('text')}" for n in news_items])
    
    prompt = f"""
    Act as a Hedge Fund Strategy Lead. Analyze this news for {ticker}:
    - Sentiment Score (0-100)
    - Macro Risk Assessment
    - Immediate Trade Verdict (Bullish/Bearish/Neutral)
    NEWS:
    {context}
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI_BRIDGE_ERROR: {str(e)}"

# 4. RENDER MAJESTIC INTERFACE
news_data = fetch_institutional_news(ticker, FMP_KEY)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### // LIVE_WIRE")
    if news_data:
        for n in news_data:
            st.markdown(f"""
            <div style="border-left: 3px solid #00ff41; padding-left: 10px; margin-bottom: 20px;">
                <p style="color:#00f0ff; font-size:10px; margin:0;">{n.get('site', 'WIRE')}</p>
                <a href="{n.get('url')}" target="_blank" style="color:white; text-decoration:none; font-weight:bold;">{n.get('title')}</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("DATA_STREAM_EMPTY: Verify FMP_KEY or check API limits (250/day).")

with col2:
    st.markdown("### // AI_ANALYTICS")
    if news_data:
        with st.spinner("SYNTHESIZING..."):
            st.info(analyze_market_alpha(news_data))
    else:
        st.write("WAITING_FOR_SIGNAL...")
