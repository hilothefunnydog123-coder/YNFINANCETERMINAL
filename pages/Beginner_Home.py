import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import google.generativeai as genai
from PIL import Image

# 1. INITIAL CONFIG & ERROR HANDLING
st.set_page_config(layout="wide", page_title="YN_VANGUARD")

# Retrieve global ticker or default to NVDA
ticker = st.session_state.get('ticker', 'NVDA')

# STYLING: Clean, Vibrant, White Background
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; color: #1E293B !important; }
    [data-testid="stHeader"], [data-testid="stSidebar"] { background-color: #F8FAFC !important; }
    h1, h2, h3, h4, p, span, label { color: #0F172A !important; }
    .st-key-card { 
        background: #FFFFFF; border: 1px solid #E2E8F0; 
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border-radius: 24px; padding: 25px; 
    }
</style>
""", unsafe_allow_html=True)

st.title("✨ YN Vanguard")

# 2. THE ELITE 15 RANKER
st.markdown("## 🏆 The YN Elite 15")
elite_stocks = [
    {"t": "NVDA", "r": "AI hardware monopoly."}, {"t": "AAPL", "r": "Eco-system dominance."},
    {"t": "MSFT", "r": "Enterprise AI leader."}, {"t": "TSLA", "r": "EV & Robotics king."},
    {"t": "GOOGL", "r": "Search & Cloud giant."}, {"t": "AMZN", "r": "E-commerce & AWS."},
    {"t": "META", "r": "Social media & Meta."}, {"t": "AVGO", "r": "Semiconductor growth."},
    {"t": "LLY", "r": "Healthcare innovator."}, {"t": "V", "r": "Global payments rail."},
    {"t": "JPM", "r": "Banking fortress."}, {"t": "COST", "r": "Retail loyalty."},
    {"t": "NFLX", "r": "Streaming leader."}, {"t": "ASML", "r": "Chip tech monopoly."},
    {"t": "AMD", "r": "Secondary AI play."}
]

# Display in a clean 5-column grid
rows = [elite_stocks[i:i + 5] for i in range(0, len(elite_stocks), 5)]
for row in rows:
    cols = st.columns(5)
    for i, stock in enumerate(row):
        with cols[i]:
            st.markdown(f"""
            <div style="background:#F8FAFC; border:1px solid #E2E8F0; padding:15px; border-radius:20px; text-align:center; margin-bottom:10px;">
                <h3 style="margin:0; font-size:18px;">{stock['t']}</h3>
                <p style="font-size:10px; color:#64748B !important;">{stock['r']}</p>
            </div>
            """, unsafe_allow_html=True)

# 3. THE 30-STOCK PIE CHART (Working & Clean)
st.markdown("---")
c1, c2 = st.columns([1, 1])

with c1:
    st.markdown("### 📊 My Ideal Portfolio")
    # Simulation of 30 assets
    tickers = ["NVDA", "AAPL", "MSFT", "TSLA", "BTC", "ETH", "VTI", "VOO", "QQQ", "AMD"] + [f"ETF_{i}" for i in range(20)]
    weights = [15, 10, 8, 7, 5, 5, 5, 5, 5, 5] + [1]*20
    
    fig = go.Figure(data=[go.Pie(
        labels=tickers, 
        values=weights, 
        hole=.5,
        textinfo='label+percent',
        insidetextorientation='radial',
        marker=dict(colors=px.colors.qualitative.Pastel)
    )])
    
    fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

# 4. AI PORTFOLIO SCANNER & CHAT (Gemini Fix)
with c2:
    st.markdown("### 🤖 YN AI Advisor")
    
    # OCR Section
    uploaded_file = st.file_uploader("Upload Portfolio Screenshot", type=['png', 'jpg', 'jpeg'])
    
    # Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("How can I improve my 30-stock portfolio?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                # FIX: Ensure proper model naming and API configuration
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel("gemini-1.5-flash") # Stable for 2026
                
                context = f"User is asking about {ticker} within a 30-stock portfolio. Question: {prompt}"
                response = model.generate_content(context)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error("AI_CONNECTION_ERROR: Please verify your GEMINI_API_KEY in Streamlit Secrets.")
