import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai
import datetime

# 1. THE AI EDITOR-IN-CHIEF
def generate_editorial(news_items, ticker):
    if not news_items: return "MARKET_SILENCE: No recent signals detected."
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        headlines = [item['title'] for item in news_items[:10]]
        prompt = f"""
        Act as the Lead Editor of a prestigious financial newspaper. 
        Write a 3-sentence 'Front Page Editorial' for {ticker} based on these headlines: {headlines}. 
        Focus on the 'Main Narrative'. Use sophisticated, broadsheet-style language.
        """
        return model.generate_content(prompt).text
    except:
        return "EDITORIAL_PENDING: AI connection encrypted."

# 2. INSTANT CACHE ENGINE
@st.cache_data(ttl=600)
def get_newspaper_data(ticker):
    stock = yf.Ticker(ticker)
    news = stock.news
    editorial = generate_editorial(news, ticker)
    return news, editorial

# 3. BROADSHEET CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=Source+Serif+Pro&display=swap');
    
    .masthead {
        text-align: center; border-bottom: 5px double #00ff41;
        padding-bottom: 10px; margin-bottom: 30px;
    }
    .masthead-title { font-family: 'Playfair Display', serif; font-size: 55px; color: #00ff41; }
    
    .editorial-box {
        background: rgba(0, 255, 65, 0.03); border: 1px solid #00ff41;
        padding: 25px; margin-bottom: 40px; font-style: italic;
        font-family: 'Source Serif Pro', serif; font-size: 18px; line-height: 1.6;
    }

    .newspaper-grid {
        display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 30px;
        border-top: 1px solid rgba(255, 255, 255, 0.1); padding-top: 20px;
    }
    
    .main-story { border-right: 1px solid rgba(255, 255, 255, 0.1); padding-right: 20px; }
    .side-story { border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding-bottom: 15px; margin-bottom: 15px; }

    .headline { font-family: 'Playfair Display', serif; color: #fff; font-size: 24px; text-decoration: none; }
    .headline:hover { color: #00ff41; }
    .dateline { font-size: 11px; color: #00ff41; text-transform: uppercase; letter-spacing: 1px; }
</style>
""", unsafe_allow_html=True)

ticker = st.session_state.get('ticker', 'NVDA')
news, ai_editorial = get_newspaper_data(ticker)

# --- RENDERING ---
st.markdown(f"""
    <div class='masthead'>
        <div class='masthead-title'>THE {ticker} GAZETTE</div>
        <div style='color:#888; font-size:12px;'>VOL. 2026-01 // PRICED IN REAL-TIME // AI-GENERATED EDITORIAL</div>
    </div>
""", unsafe_allow_html=True)

st.markdown(f"<div class='editorial-box'><b>EDITORIAL:</b> {ai_editorial}</div>", unsafe_allow_html=True)

if news:
    st.markdown("<div class='newspaper-grid'>", unsafe_allow_html=True)
    
    # MAIN STORY (Top Story)
    with st.container():
        st.markdown("<div class='main-story'>", unsafe_allow_html=True)
        top = news[0]
        st.markdown(f"<div class='dateline'>{top['publisher']} // LATEST</div>", unsafe_allow_html=True)
        st.markdown(f"<a href='{top['link']}' class='headline' style='font-size:35px;'>{top['title']}</a>", unsafe_allow_html=True)
        st.markdown("<p style='color:#bbb; margin-top:15px;'>Our primary signal indicates high-volatility shifts following recent releases. Market participants are advised to monitor the volume delta closely as this narrative unfolds across global desks.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # SIDE COLUMNS
    for i in range(1, 3): # Two columns of side stories
        with st.container():
            for item in news[i*2:(i*2)+3]:
                st.markdown("<div class='side-story'>", unsafe_allow_html=True)
                st.markdown(f"<div class='dateline'>{item['publisher']}</div>", unsafe_allow_html=True)
                st.markdown(f"<a href='{item['link']}' class='headline'>{item['title']}</a>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
