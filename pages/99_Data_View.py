import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
df = st.session_state.get('matrix_data', None)
label = st.session_state.get('matrix_label', 'UNKNOWN')

st.markdown("""
<style>
    .lattice-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; }
    .data-tile {
        background: rgba(255, 255, 255, 0.03);
        border-left: 4px solid #00f0ff;
        padding: 20px; border-radius: 10px;
    }
    .tile-label { color: #888; font-size: 11px; text-transform: uppercase; }
    .tile-val { color: #00ff41; font-size: 18px; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

st.markdown(f"<h1 style='color:#00ff41;'>// DEEP_DIVE_MATRIX: {label}</h1>", unsafe_allow_html=True)

if df is not None:
    if st.button("<< RETURN_TO_COMMAND"): st.switch_page("pages/02_Financials.py")
    
    # Display the latest snapshot as Sexy Tiles
    latest = df.iloc[:, 0]
    st.markdown("<div class='lattice-grid'>", unsafe_allow_html=True)
    for k, v in latest.items():
        val = f"{v:,.2f}" if isinstance(v, (int, float)) else str(v)
        st.markdown(f"""
            <div class='data-tile'>
                <div class='tile-label'>{k}</div>
                <div class='tile-val'>{val}</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
