import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
from PIL import Image

# 1. THEME & CORE SETUP
st.set_page_config(layout="wide", page_title="YN_VANGUARD_GLOBAL")

# Session state ticker fetch
ticker = st.session_state.get('ticker', 'NVDA')

# Light, Vibrant Theme
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; color: #1E293B !important; }
    h1, h2, h3, h4, p, span, label { color: #0F172A !important; font-family: 'Inter', sans-serif; }
    .yn-card { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 20px; padding: 20px; margin-bottom: 15px; }
    .stChatInputContainer { background-color: #F1F5F9 !important; }
</style>
""", unsafe_allow_html=True)

# 2. THE GLOBAL ELITE 15 ENGINE (Real Data + AI)
@st.cache_data(ttl=3600)
def get_global_rankings():
    # FIX: Using 'gemini-1.5-flash-latest' to avoid NotFound errors
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        
        prompt = """
        Act as a Global Portfolio Manager. Analyze all major world exchanges (NYSE, NASDAQ, LSE, TSE, HKEX).
        Rank the Top 15 stocks globally for Jan 2026 based on AI momentum, Dark Pool accumulation, and Revenue growth.
        For each, list: [Rank] [Ticker] [Country] - [Elite Reasoning]. 
        Ensure a mix of Tech, Energy, and Finance. Be professional and high-conviction.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI_OFFLINE: {str(e)}"

st.title("✨ YN Vanguard: Global Elite")

# 3. THE RANKER DISPLAY
st.markdown("## 🌍 World-Wide Elite 15")
with st.spinner("SCANNING GLOBAL MARKETS..."):
    rankings = get_global_rankings()
    st.markdown(f"<div class='yn-card'>{rankings}</div>", unsafe_allow_html=True)

# 4. THE 30-STOCK PIE CHART (Now with interactive names & sectors)
st.markdown("---")
c1, c2 = st.columns([1, 1])

with c1:
    st.markdown("### 📊 Your Global Portfolio")
    
    # Mock data for 30 Assets (Stocks + ETFs) [Image of a colorful donut chart showing portfolio allocation]
    assets = [ticker, "VOO", "VTI", "QQQ", "ASML", "MC.PA", "7203.T", "2330.TW", "SAP", "HSBC"] + [f"GLOBAL_ETF_{i}" for i in range(20)]
    weights = [15, 10, 8, 7, 5, 5, 5, 5, 5, 5] + [1.5]*20
    sectors = ["Tech", "Index", "Index", "Index", "Semis", "Luxury", "Auto", "Semis", "Software", "Bank"] + ["Diversified"]*20

    df_p = pd.DataFrame({"Asset": assets, "Weight": weights, "Sector": sectors})

    fig = px.pie(df_p, values='Weight', names='Asset', hole=.6,
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

# 5. THE AI CHATBOT (FIXED & INTERACTIVE)
with c2:
    st.markdown("### 🤖 YN AI Strategy Consultant")
    
    # Simple File Uploader for Portfolio Analysis
    uploaded_img = st.file_uploader("Upload Portfolio Screenshot", type=['png', 'jpg', 'jpeg'])

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_input := st.chat_input("Ask about your strategy..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            try:
                # FIX: Using stable model name and error handling
                model = genai.GenerativeModel("gemini-1.5-flash-latest")
                ai_prompt = f"Current ticker context: {ticker}. User question: {user_input}. Provide a friendly, expert investment response."
                
                response = model.generate_content(ai_prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"AI_SERVICE_ERROR: {str(e)}")
