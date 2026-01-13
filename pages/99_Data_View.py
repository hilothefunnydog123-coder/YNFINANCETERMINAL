import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. GEMINI CONFIGURATION
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def trigger_gemini_analysis(metric, val):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"As a Quant Hedge Fund Manager, explain {metric} ({val}) for {st.session_state.get('ticker')}. Make it high-stakes and captivating. Max 80 words."
        response = model.generate_content(prompt)
        st.session_state.gemini_analysis = response.text
    except Exception as e:
        st.session_state.gemini_analysis = f"SIGNAL_LOST: Ensure your GEMINI_API_KEY is in secrets.toml"

# 2. SESSION STATE & UI
if 'gemini_analysis' not in st.session_state:
    st.session_state.gemini_analysis = "SELECT A DATA SIGNAL TO DECODE THE MATRIX..."

st.markdown(f"<h1>// DATA_MATRIX: {st.session_state.get('matrix_label')}</h1>", unsafe_allow_html=True)
if st.button("<< RETURN_TO_COMMAND"): st.switch_page("pages/02_Financials.py")

with st.sidebar:
    st.markdown("<h2 style='color:#00ff41;'>// AI_ANALYSIS_FEED</h2>", unsafe_allow_html=True)
    st.markdown(f"<div style='border:1px solid #00ff41; padding:20px; border-radius:15px; background:rgba(0,255,65,0.05); color:#e0e0e0; font-family:monospace;'>{st.session_state.gemini_analysis}</div>", unsafe_allow_html=True)

# 3. HIGH-DENSITY LIST ENGINE
df = st.session_state.get('matrix_data')
if df is not None:
    latest = df.iloc[:, 0]
    # SORT BY IMPORTANCE (Magnitude of the value)
    items = sorted(list(latest.items()), key=lambda x: abs(x[1]) if isinstance(x[1], (int, float)) else 0, reverse=True)

    for i, (k, v) in enumerate(items):
        display_v = f"{v:,.2f}" if isinstance(v, (int, float)) else str(v)
        
        # ROW STYLING
        c1, c2, c3 = st.columns([4, 2, 1])
        c1.markdown(f"<p style='color:#888; font-family:monospace;'>{k.upper()}</p>", unsafe_allow_html=True)
        c2.markdown(f"<p style='color:#00ff41; font-family:Courier; font-weight:bold;'>{display_v}</p>", unsafe_allow_html=True)
        
        # THE DECODE BUTTON (Uses on_click callback to prevent state loss)
        c3.button("DECODE", key=f"d_{i}", on_click=trigger_gemini_analysis, args=(k, display_v))
