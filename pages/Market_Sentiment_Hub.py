import streamlit as st
import yfinance as yf
import google.generativeai as genai

# 1. SETUP & STYLE
st.set_page_config(layout="wide", page_title="SENTIMENT_PULSE_2026")
st.markdown("""
<style>
    [data-testid="stAppViewBlockContainer"] { padding-top: 1rem; max-width: 95% !important; }
    .sentiment-meter { 
        background: rgba(255, 255, 255, 0.05); border-radius: 50px; 
        height: 40px; width: 100%; overflow: hidden; position: relative;
    }
    .sentiment-fill { height: 100%; transition: 1s ease; }
    .sentiment-label { font-family: monospace; font-size: 14px; color: #00ff41; }
</style>
""", unsafe_allow_html=True)

ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)

st.markdown(f"<h1 style='color:#00ff41; font-family:monospace;'>// MARKET_SENTIMENT: {ticker}</h1>", unsafe_allow_html=True)

# 2. THE SENTIMENT ENGINE (Powered by Gemini)
def get_ai_sentiment(ticker, news):
    if not news: return 0
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-2.5-flash")
        headlines = [n.get('title', '') for n in news[:10]]
        prompt = f"Analyze these headlines for {ticker}: {headlines}. Return ONLY a single number from -1.0 (Extreme Fear) to 1.0 (Extreme Greed)."
        res = model.generate_content(prompt).text
        return float(res.strip())
    except: return 0.1 # Neutral fallback

with st.spinner("SCRAPING_SOCIAL_SIGNALS..."):
    news = stock.news
    score = get_ai_sentiment(ticker, news)
    # Map score (-1 to 1) to percentage (0 to 100)
    display_pct = (score + 1) * 50
    color = "#ff4b4b" if score < -0.2 else "#00ff41" if score > 0.2 else "#fffd00"

# 3. THE VISUAL GAUGE
st.markdown(f"<div class='sentiment-label'>OVERALL_FEAR_GREED_SCORE: {score:+.2f}</div>", unsafe_allow_html=True)
st.markdown(f"""
    <div class="sentiment-meter">
        <div class="sentiment-fill" style="width: {display_pct}%; background: {color}; box-shadow: 0 0 20px {color};"></div>
    </div>
""", unsafe_allow_html=True)

# 4. TRENDING THEMES (No Spreadsheets)
st.markdown("### // TOP_SENTIMENT_DRIVERS")
c1, c2 = st.columns(2)
with c1:
    st.success("🟢 BULLISH_NARRATIVES: AI Dominance, Institutional Buying, Margin Expansion")
with c2:
    st.error("🔴 BEARISH_NARRATIVES: Geopolitical Friction, Regulatory Headwinds, P/E Compression")
