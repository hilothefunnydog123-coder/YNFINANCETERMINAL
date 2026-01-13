import streamlit as st
import yfinance as yf
import pandas as pd

# 1. THE LAYOUT LOCK (Must be the first command)
st.set_page_config(layout="wide", page_title="STREET_INTEL_v2")

# 2. THE CUSTOM STYLING ENGINE
st.markdown("""
<style>
    /* Remove padding and maximize width */
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 2rem;
        max-width: 100% !important;
    }
    
    /* Card Container Styling */
    .st-key-whale_card {
        background: rgba(0, 255, 65, 0.03);
        border: 1px solid rgba(0, 255, 65, 0.2);
        border-radius: 15px;
        padding: 20px;
        transition: 0.3s ease;
    }
    .st-key-whale_card:hover {
        border-color: #00ff41;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.1);
    }
    .metric-label { color: #888; font-family: monospace; font-size: 11px; text-transform: uppercase; }
    .metric-value { color: #fff; font-family: 'Courier New', Courier, monospace; font-weight: bold; font-size: 16px; }
</style>
""", unsafe_allow_html=True)

ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)

st.markdown(f"<h1 style='color:#00ff41; font-family:monospace;'>// STREET_INTEL: {ticker}</h1>", unsafe_allow_html=True)

def render_whale_section(df, title):
    st.markdown(f"<h3 style='color:#00ff41; margin-top:20px;'>// {title}</h3>", unsafe_allow_html=True)
    
    if df is not None and not df.empty:
        # 3. NATIVE FLEX-GRID
        # We use st.columns with a loop to ensure responsiveness without glitching
        cols_per_row = 4
        rows = [df.iloc[i:i + cols_per_row] for i in range(0, len(df), cols_per_row)]
        
        for row_df in rows:
            cols = st.columns(cols_per_row)
            for i, (_, item) in enumerate(row_df.iterrows()):
                with cols[i]:
                    # Using key for custom CSS targeting
                    with st.container(border=True):
                        # DEFENSIVE DATA FETCH
                        name = item.get('Holder', 'N/A')
                        shares = f"{int(item.get('Shares', 0)):,}"
                        val = f"${int(item.get('Value', 0)):,}"
                        
                        # PERCENTAGE LOGIC
                        raw_pct = item.get('% Out', 0)
                        pct = raw_pct * 100 if raw_pct < 1 else raw_pct
                        
                        st.markdown(f"<div style='color:#00ff41; font-weight:bold; font-size:18px; margin-bottom:10px;'>{name}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='metric-label'>Position</div><div class='metric-value'>{shares}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='metric-label'>Value</div><div class='metric-value'>{val}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='metric-label'>Ownership</div><div class='metric-value'>{pct:.2f}%</div>", unsafe_allow_html=True)
                        
                        # Simple Progress Bar
                        st.progress(min(pct / 10, 1.0))
    else:
        st.info("SIGNAL_OFFLINE: No Whale data found.")

# RENDER BOTH SECTIONS
render_whale_section(stock.institutional_holders, "INSTITUTIONAL_WHALES")
render_whale_section(stock.mutualfund_holders, "MUTUAL_FUND_EXPOSURE")
