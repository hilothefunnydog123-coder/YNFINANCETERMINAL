import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. THE ORACLE FIX (Correct Model Name for 2026)
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# USE THE LATEST 2026 STABLE FLASH MODEL
# If gemini-3-flash-preview isn't available, fallback to gemini-2.5-flash
MODEL_ID = "gemini-3-flash-preview" 

def get_oracle_insight(metric, value, ticker):
    try:
        model = genai.GenerativeModel(MODEL_ID)
        prompt = f"""
        ACT AS: A legendary Quant Hedge Fund Manager.
        DECODE: The metric '{metric}' which is currently {value} for {ticker}.
        FORMAT: High-impact, terminal-style intelligence. 
        CONTENT: What does this move lead to? Why is it high-stakes?
        MAX WORDS: 80.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"ORACLE_OFFLINE: Model ID conflict. Verify API access for {MODEL_ID}."

# 2. MAJESTIC UI STYLING (The Sexy Green Look)
st.markdown("""
<style>
    .lattice-container { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px; }
    .stButton>button {
        background: rgba(0, 255, 65, 0.05) !important;
        border: 1px solid rgba(0, 255, 65, 0.3) !important;
        color: #00ff41 !important;
        height: 120px; border-radius: 15px;
        transition: 0.4s ease; font-family: monospace;
    }
    .stButton>button:hover {
        background: rgba(0, 255, 65, 0.15) !important;
        border: 1px solid #00ff41 !important;
        transform: scale(1.03);
    }
    .oracle-box {
        background: rgba(0, 255, 65, 0.05);
        border: 1px solid #00ff41;
        padding: 20px; border-radius: 15px;
        color: #e0e0e0; font-family: 'Courier New', monospace;
    }
</style>
""", unsafe_allow_html=True)

# 3. HUB NAVIGATION
if 'oracle_feed' not in st.session_state:
    st.session_state.oracle_feed = "CLICK A SIGNAL TILE TO DECODE THE MATRIX..."

st.markdown(f"<h1>// DATA_LATTICE_ORACLE: {st.session_state.get('matrix_label')}</h1>", unsafe_allow_html=True)

if st.button("<< RETURN_TO_HUB"):
    st.switch_page("pages/02_Financials.py")

# 4. THE AI SIDEBAR (Majestic Overlays)
with st.sidebar:
    st.markdown("<h2 style='color:#00ff41;'>// AI_ORACLE_FEED</h2>", unsafe_allow_html=True)
    st.markdown(f"<div class='oracle-box'>{st.session_state.oracle_feed}</div>", unsafe_allow_html=True)

# 5. THE UNENDING DATA GRID
df = st.session_state.get('matrix_data')
ticker = st.session_state.get('ticker', 'NVDA')

if df is not None:
    latest = df.iloc[:, 0]
    # Interactive Grid
    for i in range(0, len(latest), 4):
        cols = st.columns(4)
        for j, (k, v) in enumerate(latest.items()[i:i+4]):
            with cols[j]:
                # Button format: Metric Name \n Value
                display_v = f"{v:,.2f}" if isinstance(v, (int, float)) else str(v)
                if st.button(f"{k}\n{display_v}", key=f"cell_{i+j}"):
                    with st.spinner(f"DECRYPTING {k}..."):
                        st.session_state.oracle_feed = get_oracle_insight(k, display_v, ticker)
                        st.rerun()
