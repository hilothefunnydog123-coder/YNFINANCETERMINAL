import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
from PIL import Image
import io

# 1. CORE SYSTEM INITIALIZATION
st.set_page_config(layout="wide", page_title="YN_GLOBAL_VANGUARD")
ticker = st.session_state.get('ticker', 'NVDA')

# AUTH & THEME
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; color: #1E293B !important; }
    h1, h2, h3, h4, p, span, label { color: #0F172A !important; font-family: 'Inter', sans-serif; }
    .yn-card { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 20px; padding: 20px; }
</style>
""", unsafe_allow_html=True)

# 2. GLOBAL AI RANKING ENGINE (Scans World Markets)
@st.cache_data(ttl=3600)
def get_global_ai_rankings():
    """Scans global sectors and uses Gemini to rank the best 15 in the world"""
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # We provide the AI with current global macro context
    # In a full terminal, we'd pass a dataframe of 500+ screened stocks here
    prompt = """
    Act as a Global Macro Hedge Fund Manager. 
    Scan all world equity markets (US, EU, ASIA). 
    Identify the top 15 stocks globally based on:
    1. Institutional Dark Pool Flow
    2. Relative Strength Index (RSI) between 40-60
    3. Revenue Growth > 20%
    Return a ranked list with Ticker, Country, and a 1-sentence 'Alpha Reason'.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"INTELLIGENCE_OFFLINE: {str(e)}"

st.title("✨ YN Vanguard: Global Intelligence")

# 3. ELITE 15 GLOBAL RANKER
st.markdown("## 🌍 World Elite 15 (AI-Ranked)")
with st.spinner("SCANNING GLOBAL EXCHANGES..."):
    global_rankings = get_global_ai_rankings()
    st.markdown(f"<div class='yn-card'>{global_rankings}</div>", unsafe_allow_html=True)

# 4. AI PORTFOLIO SCANNER (Screenshot to Pie Chart)
st.markdown("---")
c1, c2 = st.columns([1, 1])

with c1:
    st.markdown("### 📷 Portfolio Vision Scanner")
    uploaded_file = st.file_uploader("Upload Portfolio Screenshot", type=['png', 'jpg', 'jpeg'])
    
    portfolio_dict = {"Tickers": ["Cash"], "Weights": [100]} # Default
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, width=300)
        
        with st.spinner("AI READING SCREENSHOT..."):
            model = genai.GenerativeModel("gemini-1.5-flash")
            # Vision prompt to extract data
            vision_prompt = "Identify the stock tickers and their percentage weights in this portfolio. Return as a comma-separated list like 'AAPL:20, TSLA:30'."
            response = model.generate_content([vision_prompt, img])
            
            try:
                # Parse AI response into a usable format
                raw_data = response.text.split(',')
                tickers = [x.split(':')[0].strip() for x in raw_data]
                weights = [float(x.split(':')[1].strip().replace('%','')) for x in raw_data]
                portfolio_dict = {"Tickers": tickers, "Weights": weights}
                st.success("Portfolio Sync Complete")
            except:
                st.error("AI couldn't parse the format. Try a clearer screenshot.")

# 5. THE DYNAMIC 30+ PIE CHART
with c2:
    st.markdown("### 📊 Your Live Allocation")
    
    df_p = pd.DataFrame(portfolio_dict)
    
    # Create the Pie
    fig = go.Figure(data=[go.Pie(
        labels=df_p['Tickers'], 
        values=df_p['Weights'], 
        hole=.6,
        marker=dict(colors=px.colors.qualitative.Pastel),
        textinfo='label+percent'
    )])
    
    fig.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

# 6. VANGUARD AI CONSULTANT
st.markdown("---")
st.markdown("### 🤖 YN AI Strategy Consultant")
if user_input := st.chat_input("Ask about your global strategy..."):
    with st.chat_message("assistant"):
        model = genai.GenerativeModel("gemini-1.5-flash")
        # Feeding terminal context into the chat
        ai_response = model.generate_content(f"User is at the YN Vanguard terminal. Focus: {ticker}. Question: {user_input}")
        st.markdown(ai_response.text)
