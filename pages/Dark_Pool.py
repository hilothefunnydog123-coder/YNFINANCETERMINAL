import streamlit as st
import pandas as pd

def render_dark_pool_hud():
    st.markdown("### 🌑 DARK_POOL_SENTINEL")
    
    # Mock data representing 'Off-Exchange' prints vs Lit Market
    dp_data = pd.DataFrame({
        "Exchange": ["Public (NASDAQ/NYSE)", "Dark Pool (Off-Exchange)"],
        "Volume": [4500000, 5200000] # Over 50% in Dark Pools is a major signal
    })
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.write("**OFF_EXCHANGE_RATIO**")
        st.title("53.6%")
        st.warning("INSTITUTIONAL_HEAVY_POSITIONING")
    with col2:
        st.bar_chart(dp_data.set_index("Exchange"), horizontal=True, color="#00ff41")

# Add this to your main terminal.py
render_dark_pool_hud()
