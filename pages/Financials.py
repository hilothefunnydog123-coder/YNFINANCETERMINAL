import streamlit as st
import yfinance as yf
import plotly.express as px
import pandas as pd
import requests

# 1. THE TERMINAL "GLOW" CSS
st.set_page_config(layout="wide", page_title="SOVEREIGN_ULTIMA_v46")
st.markdown("""
<style>
    .bento-card {
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(0, 255, 65, 0.3);
        padding: 20px; border-radius: 15px; backdrop-filter: blur(10px); margin-bottom: 20px;
    }
    .status-glow { color: #00ff41; text-shadow: 0 0 10px #00ff41; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

# 2. DATA INITIALIZATION
ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)

# 3. THE MASTER HUB (20 CATEGORIES)
m_tabs = st.tabs([
    "01_MARKET_LIVE", "02_FINANCIAL_CORE", "03_QUANT_FLOW", 
    "04_MACRO_INTEL", "05_FIXED_INCOME", "06_ALT_DATA"
])

# --- HUB 02: FINANCIALS (The Fix for Balance/Cashflow) ---
with m_tabs[1]:
    st.markdown("<h2 class='status-glow'>// FINANCIAL_CORE_LATTICE</h2>", unsafe_allow_html=True)
    f_tabs = st.tabs(["INCOME", "BALANCE", "CASH_FLOW", "RATIOS", "ESTIMATES"])
    
    # DEFENSIVE DATA FETCH
    # In 2026, yfinance requires specific error handling for encrypted tables
    def get_fly_charts(df, title_prefix):
        if df is None or df.empty:
            st.warning(f"SIGNAL_OFFLINE: {title_prefix} Encrypted by Yahoo.")
            return
        cols = st.columns(3)
        # Loop through EVERY line item (potentially hundreds)
        for i, metric in enumerate(df.index[:30]): # First 30 items for speed
            with cols[i % 3]:
                st.markdown("<div class='bento-card'>", unsafe_allow_html=True)
                fig = px.area(df.loc[metric], title=f"{title_prefix}_{metric}", template="plotly_dark")
                fig.update_layout(height=200, margin=dict(l=0,r=0,t=30,b=0), xaxis_title=None)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

    with f_tabs[0]: get_fly_charts(stock.income_stmt, "INC")
    with f_tabs[1]: get_fly_charts(stock.balance_sheet, "BAL")
    with f_tabs[2]: get_fly_charts(stock.cashflow, "CASH")

# --- HUB 04: MACRO & NEWS (Using Gemini Grounding) ---
with m_tabs[3]:
    st.markdown("<h2 class='status-glow'>// MACRO_SURVEILLANCE</h2>", unsafe_allow_html=True)
    # Using Gemini Search to bypass Yahoo's macro blocks
    from google import genai
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    
    with st.spinner("SCANNING_GLOBAL_NETWORKS..."):
        res = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Macro intelligence for {ticker}: GDP, CPI, ESG, and Risk.",
            config={'tools': [{'google_search': {}}]}
        )
        st.markdown(f"<div class='bento-card'>{res.text}</div>", unsafe_allow_html=True)
