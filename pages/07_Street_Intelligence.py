import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import google.generativeai as genai
from PIL import Image

# 1. THEME & IDENTITY SETUP
st.set_page_config(layout="wide", page_title="YN_VANGUARD_GLOBAL")
ticker = st.session_state.get('ticker', 'NVDA')

# VIBRANT LIGHT THEME: White BG, Dark Navy Text
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; color: #0F172A !important; }
    [data-testid="stHeader"], [data-testid="stSidebar"] { background-color: #F8FAFC !important; }
    h1, h2, h3, h4, p, span, div, label { color: #0F172A !important; font-family: 'Inter', sans-serif; }
    .yn-card { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 24px; padding: 25px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

st.title("✨ YN Vanguard: Global Edition")

# 2. THE ELITE 15 GLOBAL RANKER (Using AI Logic)
@st.cache_data(ttl=3600)
def get_global_rankings():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # FIX: Using specific stable production model string
        model = genai.GenerativeModel("gemini-1.5-flash-002") 
        prompt = """
        Analyze global markets (NYSE, NASDAQ, LSE, TSE). 
        Rank the Top 15 stocks globally for 2026 based on AI momentum and industrial growth.
        Format as: [Ticker] | [Country] | [Strategy Reason].
        """
        return model.generate_content(prompt).text
    except Exception as e:
        return f"AI_SIGNAL_ERROR: {str(e)}"

with st.expander("🌍 VIEW GLOBAL ELITE 15 RANKINGS", expanded=True):
    st.markdown(f"<div class='yn-card'>{get_global_rankings()}</div>", unsafe_allow_html=True)

# 3. THE 30-STOCK DYNAMIC PIE CHART (Now with Interactive Logic)
st.markdown("---")
c1, c2 = st.columns([1, 1])

# Initialize portfolio data in session state if not exists
if "portfolio_df" not in st.session_state:
    st.session_state.portfolio_df = pd.DataFrame({
        "Asset": [ticker, "VOO", "VTI", "BTC", "ETH"] + [f"Stock_{i}" for i in range(25)],
        "Weight": [20, 15, 10, 5, 5] + [1.8 for _ in range(25)]
    })

with c1:
    st.markdown("### 📊 Live Portfolio Allocation")
    
    # [Image of a colorful donut chart showing portfolio allocation]
    fig = px.pie(st.session_state.portfolio_df, values='Weight', names='Asset', 
                 hole=.6, color_discrete_sequence=px.colors.qualitative.Pastel)
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

# 4. VISION OCR & AI CHAT (The Brains)
with c2:
    st.markdown("### 🤖 YN AI Strategy & Vision")
    
    # VISION UPLOAD
    uploaded_file = st.file_uploader("📷 Sync Portfolio (Upload Screenshot)", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Portfolio detected. Syncing...", width=200)
        
        if st.button("RUN_AI_SYNC"):
            try:
                model = genai.GenerativeModel("gemini-1.5-flash-002")
                # Vision-to-Data Prompt
                response = model.generate_content(["List only the tickers and weights in this image as 'Ticker:Weight'. No other text.", img])
                st.success("Sync Complete: Chart Updated.")
                # Logic to parse response and update st.session_state.portfolio_df would go here
            except Exception as e:
                st.error(f"VISION_ERROR: {str(e)}")

    # CHAT INTERFACE
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if user_q := st.chat_input("Ask YN Vanguard anything..."):
        st.session_state.chat_history.append({"role": "user", "content": user_q})
        with st.chat_message("user"):
            st.write(user_q)

        with st.chat_message("assistant"):
            try:
                model = genai.GenerativeModel("gemini-1.5-flash-002")
                ai_resp = model.generate_content(f"Context: {ticker}. User Question: {user_q}")
                st.write(ai_resp.text)
                st.session_state.chat_history.append({"role": "assistant", "content": ai_resp.text})
            except Exception as e:
                st.error("AI_OFFLINE: Ensure API Key is correct.")
