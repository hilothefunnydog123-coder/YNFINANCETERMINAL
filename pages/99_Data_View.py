import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. ORACLE FIX (2026 Stable Model ID)
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def trigger_ai_oracle(metric, val):
    try:
        # Use the 2026 production stable model
        model = genai.GenerativeModel("gemini-1.5-flash") 
        prompt = f"As a Quant Manager, explain {metric} ({val}) for {st.session_state.get('ticker')}. High-stakes, max 75 words."
        st.session_state.oracle_msg = model.generate_content(prompt).text
    except Exception as e:
        st.session_state.oracle_msg = "ORACLE_SIGNAL_LOST: Check API Link/Model ID."

# 2. UI SESSION STATE
if 'oracle_msg' not in st.session_state: st.session_state.oracle_msg = "AWAITING SIGNAL SELECTION..."

# 3. MAJESTIC DATA LIST
st.markdown(f"<h1>// DATA_MATRIX: {st.session_state.get('matrix_label')}</h1>", unsafe_allow_html=True)
if st.button("<< RETURN_TO_COMMAND"): st.switch_page("pages/02_Financials.py")

with st.sidebar:
    st.markdown("<h2 style='color:#00ff41;'>// AI_ORACLE_FEED</h2>", unsafe_allow_html=True)
    st.markdown(f"<div style='border:1px solid #00ff41; padding:15px; border-radius:10px; background:rgba(0,255,65,0.05);'>{st.session_state.oracle_msg}</div>", unsafe_allow_html=True)

df = st.session_state.get('matrix_data')
if df is not None:
    latest = df.iloc[:, 0]
    # SORT BY IMPORTANCE: Biggest numbers first
    items = sorted(list(latest.items()), key=lambda x: abs(x[1]) if isinstance(x[1], (int, float)) else 0, reverse=True)

    for i, (k, v) in enumerate(items):
        display_v = f"{v:,.2f}" if isinstance(v, (int, float)) else str(v)
        
        # SLEEK DATA ROW (No Spreadsheet Look)
        row_cols = st.columns([4, 2, 1])
        row_cols[0].markdown(f"<p style='color:#888; font-family:monospace;'>{k.upper()}</p>", unsafe_allow_html=True)
        row_cols[1].markdown(f"<p style='color:#00ff41; font-family:Courier; font-weight:bold;'>{display_v}</p>", unsafe_allow_html=True)
        
        # THE FIX: CALLBACK HANDLES THE DATA BEFORE REFRESH
        row_cols[2].button("DECODE", key=f"d_{i}", on_click=trigger_ai_oracle, args=(k, display_v))
