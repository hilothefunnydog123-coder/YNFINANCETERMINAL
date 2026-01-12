import streamlit as st
import requests
import google.generativeai as genai

# 1. AUTHENTICATION & SECURITY
try:
    # These must be set in your Streamlit Cloud "Secrets" dashboard
    FMP_KEY = st.secrets["FMP_KEY"]
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    ticker = st.session_state.get('ticker', 'NVDA')
except KeyError:
    st.error("FATAL_ERROR: API keys missing. Check your Streamlit Cloud Secrets.")
    st.stop()

st.title(f"// MACRO_INTELLIGENCE: {ticker}")

# 2. THE 2026 DATA ENGINE (FMP)
@st.cache_data(ttl=600)
def fetch_institutional_wire(symbol, api_key):
    # FMP v3 provides structured title and full text snippets
    url = f"https://financialmodelingprep.com/api/v3/stock_news?tickers={symbol}&limit=10&apikey={api_key}"
    try:
        response = requests.get(url)
        data = response.json()
        # Ensure we only process a valid list of articles
        if isinstance(data, list) and len(data) > 0:
            return data
    except Exception:
        pass
    return []

# 3. AI ANALYTICS ENGINE (GEMINI)
def generate_alpha_briefing(news_data):
    if not news_data:
        return "SIGNAL_LOST: No data available for synthesis."
        
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # We feed snippets (text) to the AI for deeper context
    context = "\n".join([f"HEADLINE: {n.get('title')}\nSUMMARY: {n.get('text')}" for n in news_data])
    
    prompt = f"""
    Act as a Hedge Fund Strategy Lead. Analyze this news for {ticker}:
    - Identify the 'Market Sentiment Score' (0-100).
    - Extract 3 'Critical Risks'.
    - Provide a 'Trade Verdict' (Bullish/Bearish/Neutral).
    
    NEWS_STREAM:
    {context}
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI_BRIDGE_OFFLINE: {str(e)}"

# 4. MAJESTIC UI RENDERING
raw_news = fetch_institutional_wire(ticker, FMP_KEY)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### // LIVE_WIRE")
    if raw_news:
        for n in raw_news:
            # High-contrast institutional layout
            st.markdown(f"""
            <div style="border-left: 2px solid #00ff41; padding-left: 10px; margin-bottom: 20px;">
                <p style="color:#00f0ff; font-size:10px; margin:0;">{n.get('site', 'WIRE').upper()}</p>
                <a href="{n.get('url')}" target="_blank" style="color:white; text-decoration:none; font-weight:bold; font-size:16px;">{n.get('title')}</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("DATA_STREAM_EMPTY: FMP Free Tier limit reached or invalid Ticker.")

with col2:
    st.markdown("### // AI_ANALYTICS")
    if raw_news:
        with st.spinner("SYNTHESIZING..."):
            st.info(generate_alpha_briefing(raw_news))
    else:
        st.write("WAITING_FOR_MARKET_SIGNAL...")
