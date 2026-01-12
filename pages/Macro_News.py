import streamlit as st
import requests
import google.generativeai as genai

# 1. SETUP & THEME
st.set_page_config(layout="wide")

# 2. SECURE KEY RETRIEVAL
try:
    FMP_KEY = st.secrets["FMP_KEY"]
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    ticker = st.session_state.get('ticker', 'NVDA')
except KeyError as e:
    st.error(f"SYSTEM_OFFLINE: Missing {e} in Secrets.")
    st.stop()

st.title(f"// MACRO_INTELLIGENCE_WIRE: {ticker}")

# 3. VALIDATED NEWS ENGINE
@st.cache_data(ttl=1800)
def fetch_institutional_news(symbol):
    url = f"https://financialmodelingprep.com/api/v3/stock_news?tickers={symbol}&limit=5&apikey={FMP_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        # Ensure data is a list of articles, not an error dictionary
        if isinstance(data, list):
            return data
        return []
    except:
        return []

# 4. PROTECTED AI ENGINE
def get_ai_briefing(news_list):
    if not news_list:
        return "INSUFFICIENT_DATA_FOR_SYNTHESIS"
        
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Safely build context using .get() to avoid TypeErrors
    context = "\n".join([f"TITLE: {n.get('title', 'N/A')} | TEXT: {n.get('text', 'N/A')}" for n in news_list])
    
    prompt = f"Act as a hedge fund analyst. Summarize these news items for {ticker}. Give a Sentiment Score (0-100) and a Trade Verdict."
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI_OFFLINE: {str(e)}"

# 5. RENDER WORKSPACE
raw_news = fetch_institutional_news(ticker)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### // LIVE_WIRE")
    if raw_news:
        for article in raw_news:
            st.markdown(f"""
                <div style="border-left: 3px solid #00ff41; padding:15px; margin-bottom:20px; background:rgba(0,255,65,0.05);">
                    <p style="color:#00f0ff; font-size:10px;">{article.get('site', 'WIRE').upper()}</p>
                    <a href="{article.get('url', '#')}" style="color:#00ff41; text-decoration:none; font-size:18px; font-weight:bold;">{article.get('title', 'No Title')}</a>
                    <p style="color:#cccccc; font-size:13px; margin-top:5px;">{article.get('text', '')[:200]}...</p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("NO_INSTITUTIONAL_DATA_FOUND: Verify your FMP_KEY in secrets or check API limits.")

with col2:
    st.markdown("### // AI_BRIEFING")
    if raw_news:
        with st.spinner("SYNTHESIZING..."):
            briefing = get_ai_briefing(raw_news)
            st.markdown(f"<div style='border:1px solid #00f0ff; padding:15px;'>{briefing}</div>", unsafe_allow_html=True)
    else:
        st.info("WAITING_FOR_DATA_STREAM...")
