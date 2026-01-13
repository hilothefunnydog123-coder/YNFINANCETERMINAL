import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. AI HANDSHAKE (Fixes SIGNAL_LOST)
def trigger_oracle(metric, val):
    if "GEMINI_API_KEY" not in st.secrets:
        st.session_state.oracle_msg = "SIGNAL_LOST: Add GEMINI_API_KEY to secrets.toml"
        return
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"As a Quant Manager, explain {metric} ({val}) for {st.session_state.get('ticker')}. High-stakes, captivating, 75 words."
        st.session_state.oracle_msg = model.generate_content(prompt).text
    except Exception as e:
        st.session_state.oracle_msg = f"ORACLE_ERROR: {str(e)}"

# 2. SESSION STATE
if 'oracle_msg' not in st.session_state: st.session_state.oracle_msg = "SELECT A SIGNAL TO DECODE..."

# 3. MAJESTIC LIST VIEW
st.markdown(f"<h1>// DATA_MATRIX: {st.session_state.get('matrix_label')}</h1>", unsafe_allow_html=True)
if st.button("<< RETURN_TO_COMMAND"): st.switch_page("pages/02_Financials.py")

with st.sidebar:
    st.markdown("<h2 style='color:#00ff41;'>// AI_ORACLE_FEED</h2>", unsafe_allow_html=True)
    st.markdown(f"<div style='border:1px solid #00ff41; padding:15px; border-radius:10px; background:rgba(0,255,65,0.05); color:#fff;'>{st.session_state.oracle_msg}</div>", unsafe_allow_html=True)

df = st.session_state.get('matrix_data')
if df is not None:
    # Take latest snapshot
    latest = df.iloc[:, 0]
    # SORT BY IMPORTANCE: Largest numbers at the top
    items = sorted(list(latest.items()), key=lambda x: abs(x[1]) if isinstance(x[1], (int, float)) else 0, reverse=True)

    for i, (k, v) in enumerate(items):
        display_v = f"{v:,.2f}" if isinstance(v, (int, float)) else str(v)
        
        # SLEEK DATA ROW (Ordered by Significance)
        c1, c2, c3 = st.columns([4, 2, 1])
        c1.markdown(f"<p style='color:#888; font-family:monospace;'>{k.upper()}</p>", unsafe_allow_html=True)
        c2.markdown(f"<p style='color:#00ff41; font-family:Courier; font-weight:bold;'>{display_v}</p>", unsafe_allow_html=True)
        # CALLBACK LOCK: Triggers AI before the page reruns
        c3.button("DECODE", key=f"d_{i}", on_click=trigger_oracle, args=(k, display_v))
