import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from PIL import Image
import google.generativeai as genai

# 1. FIX NAMEERROR: Define Ticker early
ticker = st.session_state.get('ticker', 'NVDA')

# 2. VIBRANT THEME LOCK (White Background / Dark Text)
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; color: #1E293B !important; }
    h1, h2, h3, h4, p, span, div, label { color: #0F172A !important; font-family: 'Inter', sans-serif; }
    .st-key-card { 
        background: #FFFFFF; border: 1px solid #E2E8F0; 
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border-radius: 24px; padding: 25px; 
    }
</style>
""", unsafe_allow_html=True)

st.title("✨ YN Vanguard: Your Wealth Portal")

# 3. ELITE TOP 15 RANKER (Vibrant Grid)
st.markdown("## 🏆 The YN Elite 15")
# Logic: Top 15 stocks based on AI momentum scores
elite_stocks = [
    {"t": "NVDA", "r": "Institutional buying is surging before earnings."},
    {"t": "PLTR", "r": "S&P inclusion catalyst + massive AI contract flow."},
    {"t": "MSFT", "r": "Cloud dominance with GenAI integration at scale."},
    {"t": "TSLA", "r": "FSD licensing potential outweighs auto-margin stress."},
    {"t": "AMD", "r": "MI300 ramp-up competing directly for AI market share."},
] # Add 10 more to complete 15

cols = st.columns(5)
for i, stock_item in enumerate(elite_stocks):
    with cols[i]:
        st.markdown(f"""
        <div style="background:#F8FAFC; border:1px solid #E2E8F0; padding:15px; border-radius:20px; text-align:center;">
            <div style="background:linear-gradient(135deg, #6366F1, #A855F7); color:white; border-radius:50px; display:inline-block; padding:2px 10px; font-size:10px;">RANK #{i+1}</div>
            <h3 style="margin:5px 0;">{stock_item['t']}</h3>
            <p style="font-size:11px; color:#64748B !important;">{stock_item['r']}</p>
        </div>
        """, unsafe_allow_html=True)

# 4. AI PORTFOLIO SCANNER (OCR)
st.markdown("---")
c1, c2 = st.columns([1, 1])

with c1:
    st.markdown("### 🔍 AI Portfolio Audit")
    uploaded_file = st.file_uploader("Upload Portfolio Screenshot", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        # Gemini 2.5 Flash Vision Logic
        model = genai.GenerativeModel("gemini-2.5-flash")
        with st.spinner("AI is reading your positions..."):
            response = model.generate_content(["Extract stock tickers/percentages and give a 2-sentence advice for diversification.", img])
            st.markdown(f"<div style='background:#F1F5F9; padding:20px; border-radius:15px;'>{response.text}</div>", unsafe_allow_html=True)

# 5. THE LOGO PIE CHART
with c2:
    st.markdown("### 📊 My Ideal Allocation")
    labels = ['NVDA', 'AAPL', 'TSLA', 'BTC', 'ETH']
    values = [35, 25, 20, 10, 10]
    logos = [
        "https://logo.clearbit.com/nvidia.com",
        "https://logo.clearbit.com/apple.com",
        "https://logo.clearbit.com/tesla.com",
        "https://logo.clearbit.com/bitcoin.org",
        "https://logo.clearbit.com/ethereum.org"
    ]
    colors = ['#6366F1', '#EC4899', '#F59E0B', '#10B981', '#3B82F6']

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.6, 
                                 textinfo='label+percent', marker=dict(colors=colors))])

    # ADD LOGOS TO PIE SLICES
    for i, (label, val) in enumerate(zip(labels, values)):
        # Math to find center of the wedge
        angle = (sum(values[:i]) + val/2) / sum(values) * 2 * np.pi
        x = 0.5 + 0.3 * np.cos(angle)
        y = 0.5 + 0.3 * np.sin(angle)
        
        fig.add_layout_image(
            dict(source=logos[i], xref="paper", yref="paper",
                 x=x, y=y, sizex=0.1, sizey=0.1,
                 xanchor="center", yanchor="middle")
        )

    fig.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)

# 6. VANGUARD AI ADVISOR
st.markdown("---")
st.markdown("### 🤖 Vanguard AI Assistant")
if user_input := st.chat_input("Ask me anything about your portfolio..."):
    with st.chat_message("assistant"):
        # Fixed the NameError by using the pre-defined 'ticker' variable
        st.write(f"Vanguard AI: To maximize **{ticker}**, I recommend balancing your tech exposure with defensive sectors like Healthcare.")
