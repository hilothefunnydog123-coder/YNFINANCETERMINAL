import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
df = st.session_state.get('matrix_data', None)
label = st.session_state.get('matrix_label', 'UNKNOWN')

st.markdown("""
<style>
    .lattice-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px; }
    .data-tile {
        background: rgba(255, 255, 255, 0.03);
        border-left: 4px solid #00f0ff;
        padding: 15px; border-radius: 10px;
        transition: 0.3s;
    }
    .data-tile:hover { background: rgba(0, 255, 65, 0.05); border-left: 4px solid #00ff41; }
    .tile-label { color: #888; font-size: 10px; text-transform: uppercase; font-family: monospace; }
    .tile-val { color: #fff; font-size: 17px; font-weight: bold; font-family: 'Courier New', monospace; }
</style>
""", unsafe_allow_html=True)

st.markdown(f"<h1 style='color:#00ff41; text-shadow:0 0 10px #00ff41;'>// DEEP_DIVE_MATRIX: {label}</h1>", unsafe_allow_html=True)

if df is not None:
    if st.button("<< RETURN_TO_COMMAND"): st.switch_page("pages/02_Financials.py")
    
    # We take the most recent data point (latest year/quarter)
    latest = df.iloc[:, 0]
    
    st.markdown("<div class='lattice-grid'>", unsafe_allow_html=True)
    for k, v in latest.items():
        # Smart formatting: if it's a number, add commas and decimals
        if isinstance(v, (int, float)) and not pd.isna(v):
            display_val = f"{v:,.2f}"
        else:
            display_val = str(v)
            
        st.markdown(f"""
            <div class='data-tile'>
                <div class='tile-label'>{k}</div>
                <div class='tile-val'>{display_val}</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.error("NO_DATA_STREAM_AVAILABLE")
