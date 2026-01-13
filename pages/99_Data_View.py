import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. AI ORACLE INITIALIZATION
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def trigger_oracle(metric, val):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"As a top-tier Quant, explain {metric} ({val}) for {st.session_state.get('ticker')}. High-stakes, captivating, 70 words."
        response = model.generate_content(prompt)
        st.session_state.oracle_msg = response.text
    except:
        st.session_state.oracle_msg = "ORACLE_SIGNAL_LOST: Check API Link."

# 2. SESSION STATE
if 'oracle_msg' not in st.session_state: st.session_state.oracle_msg = "SELECT A SIGNAL TO DECODE..."

# 3. MAJESTIC LIST VIEW
st.markdown(f"<h1>// DATA_MATRIX: {st.session_state.get('matrix_label')}</h1>", unsafe_allow_html=True)
if st.button("<< RETURN_TO_HUB"): st.switch_page("pages/02_Financials.py")

with st.sidebar:
    st.markdown("<h2 style='color:#00ff41;'>// AI_ORACLE_FEED</h2>", unsafe_allow_html=True)
    st.markdown(f"<div style='border:1px solid #00ff41; padding:20px; border-radius:10px; background:rgba(0,255,65,0.05);'>{st.session_state.oracle_msg}</div>", unsafe_allow_html=True)

df = st.session_state.get('matrix_data')
if df is not None:
    latest = df.iloc[:, 0]
    # SORT BY IMPORTANCE (Magnitude of the number)
    items = sorted(list(latest.items()), key=lambda x: abs(x[1]) if isinstance(x[1], (int, float)) else 0, reverse=True)

    for i, (k, v) in enumerate(items):
        display_v = f"{v:,.2f}" if isinstance(v, (int, float)) else str(v)
        
        # TERMINAL ROW STYLING
        c1, c2, c3 = st.columns([3, 2, 1])
        with c1: st.markdown(f"<p style='color:#888; font-family:monospace;'>{k.upper()}</p>", unsafe_allow_html=True)
        with c2: st.markdown(f"<p style='color:#00ff41; font-family:Courier; font-weight:bold;'>{display_v}</p>", unsafe_allow_html=True)
        with c3:
            # CALLBACK FIX: on_click handles the data before rerun
            st.button("DECODE", key=f"dec_{i}", on_click=trigger_oracle, args=(k, display_v))
