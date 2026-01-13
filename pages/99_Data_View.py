import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="TERMINAL_MATRIX_v46")

# THE SEXY MATRIX CSS
st.markdown("""
<style>
    .matrix-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 20px;
        padding: 20px;
    }
    .data-cell {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 255, 65, 0.2);
        padding: 20px;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        transition: 0.3s;
    }
    .data-cell:hover {
        background: rgba(0, 255, 65, 0.05);
        border: 1px solid #00ff41;
        transform: translateY(-5px);
    }
    .cell-label { color: #888; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; }
    .cell-val { color: #00ff41; font-size: 20px; font-weight: bold; font-family: 'Courier New', monospace; }
</style>
""", unsafe_allow_html=True)

# LOAD THE UNENDING DATA
data = st.session_state.get('matrix_data', None)
label = st.session_state.get('matrix_label', 'UNKNOWN_STREAM')

st.markdown(f"<h1 style='color:#00ff41; text-shadow:0 0 10px #00ff41;'>// DEEP_DIVE_MATRIX: {label}</h1>", unsafe_allow_html=True)

if st.button("<< RETURN_TO_HUB"):
    st.switch_page("pages/02_Financials.py") # VERIFY THIS FILENAME MATCHES EXACTLY

if data is not None:
    # We take the latest snapshot (first column)
    latest = data.iloc[:, 0]
    
    st.markdown("<div class='matrix-container'>", unsafe_allow_html=True)
    for k, v in latest.items():
        # Smart formatting for the unending data
        if isinstance(v, (int, float)):
            v_str = f"{v:,.2f}"
        else:
            v_str = str(v)
            
        st.markdown(f"""
            <div class='data-cell'>
                <div class='cell-label'>{k}</div>
                <div class='cell-val'>{v_str}</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.error("NO_DATA_STREAM_FOUND")
