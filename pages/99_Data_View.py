import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. ORACLE CONFIG
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def get_oracle_insight(metric, value, ticker):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"As a Quant Analyst, explain {metric} ({value}) for {ticker}. Make it high-stakes and captivating. Max 80 words."
        return model.generate_content(prompt).text
    except: return "ORACLE_LINK_OFFLINE"

# 2. LIST STYLING
st.markdown("""
<style>
    .data-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 10px 20px; border-bottom: 1px solid rgba(0, 255, 65, 0.1);
        transition: 0.2s;
    }
    .data-row:hover { background: rgba(0, 255, 65, 0.05); }
    .label-text { color: #888; font-family: monospace; font-size: 14px; }
    .value-text { color: #00ff41; font-family: 'Courier New'; font-weight: bold; }
    .oracle-box { background: rgba(0, 255, 65, 0.05); border: 1px solid #00ff41; padding: 20px; border-radius: 15px; }
</style>
""", unsafe_allow_html=True)

if 'oracle_msg' not in st.session_state:
    st.session_state.oracle_msg = "AWAITING SIGNAL SELECTION..."

df = st.session_state.get('matrix_data')
label = st.session_state.get('matrix_label', 'DATA')

st.markdown(f"<h1>// DATA_MATRIX: {label}</h1>", unsafe_allow_html=True)
if st.button("<< RETURN_TO_HUB"): st.switch_page("pages/02_Financials.py")

with st.sidebar:
    st.markdown("<h2 style='color:#00ff41;'>// AI_ORACLE_FEED</h2>", unsafe_allow_html=True)
    st.markdown(f"<div class='oracle-box'>{st.session_state.oracle_msg}</div>", unsafe_allow_html=True)

# 3. HIGH-DENSITY LIST ENGINE
if df is not None:
    # Take the latest data point
    latest = df.iloc[:, 0]
    
    # Raking: In finance, items with larger absolute values are often more 'important' 
    # (Revenue > Misc Expenses). We sort by importance for the list.
    items = list(latest.items())
    # Sort by value if numeric, otherwise keep original order
    try:
        items.sort(key=lambda x: abs(float(x[1])) if isinstance(x[1], (int, float)) else 0, reverse=True)
    except: pass

    for i, (k, v) in enumerate(items):
        display_v = f"{v:,.2f}" if isinstance(v, (int, float)) else str(v)
        
        # We use a columns layout to create a "Clickable Row" effect
        c1, c2, c3 = st.columns([3, 2, 1])
        with c1: st.markdown(f"<p class='label-text'>{k.upper()}</p>", unsafe_allow_html=True)
        with c2: st.markdown(f"<p class='value-text'>{display_v}</p>", unsafe_allow_html=True)
        with c3:
            if st.button("DECODE", key=f"decode_{i}"):
                with st.spinner("ANALYZING..."):
                    st.session_state.oracle_msg = get_oracle_insight(k, display_v, "THIS_TICKER")
                    st.rerun()
