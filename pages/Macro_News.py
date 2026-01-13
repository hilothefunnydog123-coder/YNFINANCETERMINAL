import streamlit as st
import yfinance as yf
import datetime
import google.generativeai as genai

# 1. AI EDITOR-IN-CHIEF CONFIG
@st.cache_data(ttl=600)
def generate_editorial(news_items, ticker):
    if not news_items or "GEMINI_API_KEY" not in st.secrets:
        return "EDITORIAL_PENDING: Signal connection encrypted or news feed dry."
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-2.5-flash") # 2026 Stable Tier
        headlines = [item.get('title', '') for item in news_items[:8]]
        prompt = f"Act as a financial editor. Write a sharp 3-sentence editorial for {ticker} based on these headlines: {headlines}. Tone: Sophisticated, Broadsheet style."
        return model.generate_content(prompt).text
    except:
        return "MARKET_INTELLIGENCE: High volatility detected. Editorial staff investigating."

# 2. FAST CACHE ENGINE
@st.cache_data(ttl=300)
def fetch_gazette_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        return news
    except:
        return []

# 3. NEWSPAPER TYPOGRAPHY & GRID
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Source+Serif+Pro&display=swap');
    
    .masthead { text-align: center; border-bottom: 5px double #00ff41; padding-bottom: 10px; margin-bottom: 30px; }
    .masthead-title { font-family: 'Playfair Display', serif; font-size: 50px; color: #00ff41; letter-spacing: -1px; }
    
    .editorial-box {
        background: rgba(0, 255, 65, 0.03); border: 1px solid #00ff41;
        padding: 20px; margin-bottom: 30px; font-family: 'Source Serif Pro', serif;
        font-style: italic; font-size: 17px; line-height: 1.5; color: #e0e0e0;
    }

    .newspaper-columns {
        column-count: 2; column-gap: 40px; column-rule: 1px solid rgba(255, 255, 255, 0.1);
    }
    .article-block { break-inside: avoid; margin-bottom: 25px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding-bottom: 15px; }
    .headline { font-family: 'Playfair Display', serif; font-size: 22px; color: #fff; text-decoration: none; display: block; line-height: 1.2; }
    .headline:hover { color: #00ff41; }
    .dateline { font-size: 10px; color: #00ff41; text-transform: uppercase; margin-bottom: 5px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

ticker = st.session_state.get('ticker', 'NVDA')
news_data = fetch_gazette_data(ticker)
ai_editorial = generate_editorial(news_data, ticker)

# --- RENDERING THE GAZETTE ---
st.markdown(f"<div class='masthead'><div class='masthead-title'>THE {ticker} GAZETTE</div><div style='color:#888; font-size:11px;'>VOL. 2026.01 // AI-EDITOR BY GEMINI // PRICE: $0.00</div></div>", unsafe_allow_html=True)

st.markdown(f"<div class='editorial-box'><b>THE LEAD:</b> {ai_editorial}</div>", unsafe_allow_html=True)

