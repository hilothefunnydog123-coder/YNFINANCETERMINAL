import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import google.generativeai as genai

# 1. THEME & IDENTITY SETUP
st.set_page_config(layout="wide", page_title="YN_VANGUARD")
ticker = st.session_state.get('ticker', 'NVDA') # FIXED: No more NameError

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, h4, p, span, div, label { color: #1E293B !important; font-family: 'Inter', sans-serif; }
    [data-testid="stHeader"], [data-testid="stSidebar"] { background-color: #F8FAFC !important; }
    
    .chat-bubble {
        background: #F1F5F9; border-radius: 20px; padding: 15px;
        margin-bottom: 10px; border: 1px solid #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)

st.title("✨ YN Vanguard")

# 2. ELITE 30 GLOBAL RANKER
st.markdown("### 🏆 The Elite 30: AI Rankings")
# Simulate top 30
top_30_tickers = ["NVDA", "AAPL", "MSFT", "AMZN", "META", "TSLA", "GOOGL", "AVGO", "ASML", "COST"] # ... up to 30
cols = st.columns(5)
for i, t in enumerate(top_30_tickers[:10]): # Showing first 10 for space
    with cols[i % 5]:
        st.markdown(f"**{i+1}. {t}**")

# 3. THE 30-STOCK "CIRCLE" (TREEMAP SOLUTION)
# A Pie Chart with 30 slices is unreadable. Treemaps are the pro alternative.
st.markdown("### 📊 Portfolio Composition (30+ Assets)")

# Mock data for 30 stocks
data = {
    'Stock': [f'Asset_{i}' for i in range(30)],
    'Sector': ['Tech']*10 + ['Energy']*5 + ['Finance']*10 + ['Retail']*5,
    'Value': [10, 8, 7, 5, 5, 4, 3, 3, 2, 2] + [1]*20
}
df_p = pd.DataFrame(data)

# Treemaps allow 30+ stocks to look "fire" and organized by sector
fig = px.treemap(df_p, path=['Sector', 'Stock'], values='Value',
                 color='Sector', color_discrete_sequence=px.colors.qualitative.Pastel)
fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='white')
st.plotly_chart(fig, use_container_width=True)

# 4. ACTUAL GEMINI AI ADVISOR
st.markdown("---")
st.markdown("### 🤖 YN AI Strategy Consultant")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about your 30-stock portfolio..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Connect to real Gemini API
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Give Gemini the context of the current ticker and 30-stock goal
        ai_prompt = f"The user is looking at {ticker}. They have a 30-stock portfolio. Answer this question in a friendly, expert tone: {prompt}"
        response = model.generate_content(ai_prompt)
        
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
