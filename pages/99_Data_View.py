import streamlit as st

st.set_page_config(layout="wide")
data = st.session_state.get('deep_dive', None)

st.markdown("""
<style>
    .data-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; }
    .data-point {
        background: rgba(255, 255, 255, 0.05);
        border-left: 3px solid #00ff41;
        padding: 15px; border-radius: 5px;
    }
    .label { color: #888; font-size: 10px; text-transform: uppercase; }
    .val { color: #fff; font-size: 16px; font-weight: bold; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color:#00ff41;'>// RAW_DATA_MATRIX_STREAM</h1>", unsafe_allow_html=True)

if data is not None:
    if st.button("<< BACK_TO_COMMAND_CENTER"): st.switch_page("pages/02_Financials.py")
    
    # We display the latest data column as cards
    latest_data = data.iloc[:, 0]
    st.markdown("<div class='data-grid'>", unsafe_allow_html=True)
    for label, val in latest_data.items():
        st.markdown(f"""
            <div class='data-point'>
                <div class='label'>{label}</div>
                <div class='val'>{val:,.2f if isinstance(val, (int, float)) else val}</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
