import streamlit as st
import requests
import google.generativeai as genai
import pandas as pd

# 1. SETUP & THEME
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    .reportview-container { background: #000000; }
    .news-card { border-left: 3px solid #00ff41; padding: 15px; margin-bottom: 20px; background: rgba(0,255,65,0.05); }
    .ai-badge { background: #00f0ff; color: black; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 10px; }
    </style>
""", unsafe_allow_html=True)

# 2. SECURE KEY RETRIEVAL
try:
    FMP_KEY = st.secrets["FMP_KEY"]
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    ticker = st.session_state.get('ticker', 'NVDA')
except KeyError as e:
    st.error(f"SYSTEM_OFFLINE: Missing {e} in Secrets.")
    st.stop()

st.title(f"// MACRO_INTELLIGENCE_WIRE: {ticker}")

# 3. FMP NEWS ENGINE
@st.cache_data(ttl=1800)
def fetch_institutional_news(symbol):
    url = f"https://financialmodelingprep.com/api/v3/stock_news?tickers={symbol}&limit=5&apikey={FMP_KEY}"
    response = requests.get(url)
    return response.json()

# 4. GEMINI ANALYST ENGINE
def get_ai_briefing(news_list):
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Bundle news for the AI
    context = "\n".join([f"TITLE: {n['title']} | TEXT: {n['text']}" for n in news_list])
    prompt = f"Act as a cynical hedge fund analyst. Summarize these 5 news items for {ticker}. Give a 'Sentiment Score' (0-100) and a one-sentence 'Trade Verdict'. \n\n {context}"
    
    response = model.generate_content(prompt)
    return response.text

# 5. RENDER WORKSPACE
raw_news = fetch_institutional_news(ticker)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### // LIVE_WIRE")
    if isinstance(raw_news, list) and len(raw_news) > 0:
        for article in raw_news:
            st.markdown(f"""
                <div class="news-card">
                    <p style="color:#00f0ff; font-size:10px;">{article['site'].upper()} | {article['publishedDate']}</p>
                    <a href="{article['url']}" style="color:#00ff41; text-decoration:none; font-size:18px; font-weight:bold;">{article['title']}</a>
                    <p style="color:#cccccc; font-size:13px; margin-top:5px;">{article['text'][:200]}...</p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("NO_INSTITUTIONAL_DATA_FOUND")

with col2:
    st.markdown("### // AI_BRIEFING <span class='ai-badge'>GEMINI_1.5</span>", unsafe_allow_html=True)
    if raw_news:
        with st.spinner("SYNTHESIZING..."):
            briefing = get_ai_briefing(raw_news)
            st.markdown(f"<div style='border:1px solid #00f0ff; padding:15px; border-radius:5px;'>{briefing}</div>", unsafe_allow_html=True)
    else:
        st.write("WAITING_FOR_DATA_STREAM...")
