import streamlit as st

st.set_page_config(layout="wide")
label = st.session_state.get('deep_dive_label', 'UNKNOWN_STREAM')
df = st.session_state.get('deep_dive_data', None)

st.markdown(f"<h1 style='color:#00ff41;'>// DEEP_DIVE_MATRIX: {label}</h1>", unsafe_allow_html=True)

if df is not None:
    # THE "UNENDING DATA" VIEW
    st.markdown("### // SYSTEM_RAW_FEED")
    st.data_editor(
        df, 
        use_container_width=True, 
        height=800, # Large view for thousands of numbers
        disabled=True
    )
    if st.button("<< RETURN_TO_HUB"):
        st.switch_page("pages/02_Financials.py")
else:
    st.error("NO_DATA_STREAM_FOUND")
