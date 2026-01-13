import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. ORACLE CONFIG
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def get_oracle_insight(metric, value, ticker):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash") # Stable 2026 ID
        prompt = f"As a Quant Manager, explain {metric} ({value}) for {ticker}. High-stakes, captivating, max 80 words."
        return model.generate_content(prompt).text
    except: return "ORACLE_LINK_INTERRUPTED"

# 2. STYLING
st.markdown("""
<style>
    .stButton>button {
        background: rgba(0, 255, 65, 0.05) !important;
        border: 1px solid rgba(0, 255, 65, 0.3) !important;
        color: #00ff41 !important; height: 130px; border-radius: 15px;
        transition: 0.3s; font-family: monospace;
    }
    .stButton>button:hover { border: 1px solid #00ff41 !important; transform: scale(1.02); }
    .oracle-feed { background: rgba(0, 255, 65, 0.05); padding: 20px; border-radius: 15px; border: 1px solid #00ff41; }
</style>
""", unsafe_allow_html=True)

# 3. DATA PERSISTENCE
if 'oracle_msg' not in st.session_state:
    st.session_state.oracle_msg = "SELECT A DATA POINT TO DECODE..."

label = st.session_state.get('matrix_label', 'DATA')
df = st.session_state.get('matrix_data')

st.markdown(f"<h1>// DATA_LATTICE: {label}</h1>", unsafe_allow_html=True)
if st.button("<< RETURN_TO_HUB"): st.switch_page("pages/02_Financials.py")

with st.sidebar:
    st.markdown("<h2 style='color:#00ff41;'>// AI_ORACLE_FEED</h2>", unsafe_allow_html=True)
    st.markdown(f"<div class='oracle-feed'>{st.session_state.oracle_msg}</div>", unsafe_allow_html=True)

# 4. UNENDING GRID ENGINE
if df is not None:
    latest = df.iloc[:, 0]
    items = list(latest.items()) # FIXED: LIST CONVERSION
    for i in range(0, len(items), 4):
        cols = st.columns(4)
        for j, (k, v) in enumerate(items[i:i+4]):
            with cols[j]:
                display_v = f"{v:,.2f}" if isinstance(v, (int, float)) else str(v)
                if st.button(f"{k}\n{display_v}", key=f"cell_{i+j}"):
                    with st.spinner("DECODING..."):
                        st.session_state.oracle_msg = get_oracle_insight(k, display_v, "THIS_TICKER")
                        st.rerun()
