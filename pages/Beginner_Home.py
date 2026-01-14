import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
import google.generativeai as genai

# 1. VIBRANT THEME LOCK
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; color: #1E293B !important; }
    [data-testid="stHeader"], [data-testid="stSidebar"] { background-color: #F8FAFC !important; }
    
    /* Global Text Correction: Darker for readability */
    h1, h2, h3, h4, p, span, div, label { color: #0F172A !important; font-family: 'Inter', sans-serif; }
    
    .yn-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        border-radius: 24px;
        padding: 25px;
        margin-bottom: 20px;
    }
    .elite-badge {
        background: linear-gradient(135deg, #6366F1 0%, #A855F7 100%);
        color: white !important;
        padding: 4px 14px;
        border-radius: 50px;
        font-weight: 800;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

st.title("✨ YN Vanguard: Your Wealth Portal")

# 2. ELITE TOP 15 RANKER (Horizontal Cards)
st.markdown("## 🏆 The YN Elite 15")
elite_data = [
    {"t": "NVDA", "r": "Dominant AI Moat with surging data center revenue."},
    {"t": "MSFT", "r": "Azure AI integration leads enterprise cloud adoption."},
    {"t": "AAPL", "r": "Resilient ecosystem and massive services growth."},
    {"t": "AMZN", "r": "AWS margin expansion and retail logistics efficiency."},
    {"t": "GOOGL", "r": "DeepMind integration and Search generative dominance."}
] # In production, loop this for 15

cols = st.columns(5)
for i, item in enumerate(elite_data):
    with cols[i]:
        st.markdown(f"""
        <div class="yn-card">
            <div class="elite-badge">RANK #{i+1}</div>
            <h3 style="margin:10px 0;">{item['t']}</h3>
            <p style="font-size:12px; color:#64748B !important;">{item['r']}</p>
        </div>
        """, unsafe_allow_html=True)

# 3. AI PORTFOLIO SCANNER (OCR)
st.markdown("---")
c_left, c_right = st.columns([1, 1])

with c_left:
    st.markdown("### 🔍 AI Portfolio Auditor")
    uploaded_file = st.file_uploader("Drop your portfolio screenshot here", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Scanning for tickers...", width=250)
        
        # Gemini 2.5 Flash OCR Logic
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(["Extract stock tickers and percentages. Recommend 1 'Buy' and 1 'Sell' based on diversification.", img])
        st.success("Analysis Complete")
        st.markdown(f"<div class='yn-card'>{response.text}</div>", unsafe_allow_html=True)

with c_right:
    st.markdown("### 📊 My Ideal Allocation")
    # Vibrant Donut Chart with Logos
    labels = ['NVIDIA', 'APPLE', 'TESLA', 'BITCOIN', 'CASH']
    values = [40, 20, 15, 15, 10]
    colors = ['#6366F1', '#EC4899', '#F59E0B', '#10B981', '#94A3B8']

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.75, 
                                 marker=dict(colors=colors, line=dict(color='#FFF', width=4)))])
    
    # Add Central Brand Text or Logo
    fig.add_annotation(text="YN_CORE", x=0.5, y=0.5, showarrow=False, font=dict(size=20, color="#1E293B"))
    
    fig.update_layout(showlegend=True, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)

# 4. CHATBOT CONSULTANT
st.markdown("---")
st.markdown("### 🤖 Vanguard Advisor")
user_q = st.chat_input("Ask about your strategy...")
if user_q:
    with st.chat_message("assistant"):
        st.write(f"Vanguard AI: To maximize {ticker}, I recommend balancing your tech exposure with some defensive sectors.")
