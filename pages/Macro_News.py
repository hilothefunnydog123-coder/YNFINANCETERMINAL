import streamlit as st
import yfinance as yf
import google.generativeai as genai

# 1. AUTHENTICATION
try:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    ticker = st.session_state.get('ticker', 'NVDA')
except KeyError:
    st.error("SYSTEM_OFFLINE: API keys missing. Rename folder to .streamlit")
    st.stop()

st.title(f"// MACRO_INTELLIGENCE: {ticker}")

# 2. DEFENSIVE DATA FETCHING
def get_sanitized_news(symbol):
    try:
        raw_news = yf.Ticker(symbol).news
        clean_news = []
        for n in raw_news[:8]:
            # Check all known keys used by Yahoo in 2026
            title = n.get('title') or n.get('headline') or n.get('text')
            if title:
                clean_news.append({'title': title, 'link': n.get('link', '#')})
        return clean_news
    except:
        return []

# 3. AI SYNTHESIS
def get_ai_briefing(news_data):
    if not news_data: return "INSUFFICIENT_SIGNAL_DATA"
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        # Combine only valid titles into context
        context = "\n".join([item['title'] for item in news_data])
        prompt = f"Summarize these headlines for {ticker} in 3 bullet points. Verdict: Bullish or Bearish?"
        return model.generate_content(prompt).text
    except Exception as e:
        return f"AI_BRIDGE_FAILED: {str(e)}"

# 4. RENDER
news = get_sanitized_news(ticker)
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### // LIVE_WIRE")
    for item in news:
        st.markdown(f"""
        <div style="border-left: 3px solid #00ff41; padding-left: 10px; margin-bottom: 10px;">
            <a href="{item['link']}" style="color:#00ff41; text-decoration:none;">{item['title']}</a>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("### // AI_BRIEFING")
    with st.spinner("ANALYZING..."):
        st.info(get_ai_briefing(news))
