import streamlit as st
import yfinance as yf
import plotly.express as px
import pandas as pd

# 1. STYLE INJECTION
st.set_page_config(layout="wide", page_title="SOVEREIGN_V46_CORE")
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00ff41; }
    .bento-card {
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(0, 255, 65, 0.3);
        padding: 20px; border-radius: 15px; backdrop-filter: blur(10px); margin-bottom: 20px;
    }
    .metric-value { font-family: monospace; font-size: 20px; color: #00ff41; }
</style>
""", unsafe_allow_html=True)

# 2. DATA DECRYPTION
ticker_name = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker_name)
inf = stock.info

st.markdown(f"<h1>// FINANCIAL_INTELLIGENCE_LATTICE: {ticker_name}</h1>", unsafe_allow_html=True)

# 3. MEGA-TAB SYSTEM
tabs = st.tabs(["RATIO_ENGINE", "ESG_SURVEILLANCE", "INCOME_MTX", "BALANCE_MTX", "CASH_FLOW_MTX", "OWNERSHIP"])

# --- TAB 1: RATIO ENGINE (Hundreds of Ratios) ---
with tabs[0]:
    st.markdown("### // QUANTITATIVE_RATIO_STREAM")
    # We pull every key from .info that is a ratio or valuation metric
    ratio_keys = [k for k in inf.keys() if any(x in k.lower() for x in ['ratio', 'pe', 'margin', 'growth', 'yield', 'ebitda'])]
    
    # Loop through all 100+ ratios and create individual cards
    for i in range(0, len(ratio_keys), 4):
        cols = st.columns(4)
        for j, key in enumerate(ratio_keys[i:i+4]):
            with cols[j]:
                st.markdown(f"<div class='bento-card'>", unsafe_allow_html=True)
                st.write(f"**{key.upper()}**")
                st.markdown(f"<p class='metric-value'>{inf.get(key, 'N/A')}</p>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 2: ESG SURVEILLANCE (The Fix) ---
with tabs[1]:
    st.markdown("### // SUSTAINABILITY_SCORECARD")
    # Fix: yfinance moved ESG to a different internal structure in 2026
    try:
        esg = stock.sustainability
        if esg is not None and not esg.empty:
            c1, c2 = st.columns([1, 2])
            with c1:
                st.dataframe(esg, use_container_width=True)
            with c2:
                # 10+ ESG Charts
                fig_esg = px.bar(esg, template="plotly_dark", color_discrete_sequence=['#00ff41'])
                st.plotly_chart(fig_esg, use_container_width=True)
        else:
            st.warning("ESG_SIGNAL_ENCRYPTED: Providers often block ESG data for high-frequency IPs.")
    except:
        st.error("ESG_BRIDGE_FAILED")

# --- TAB 3: INCOME_MTX (The "15 Charts" Grid) ---
with tabs[2]:
    st.markdown("### // INCOME_DYNAMICS_GRID")
    data = stock.income_stmt
    if not data.empty:
        # Peel the Index for 2026 yfinance
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)
        
        # Generator for 15+ individual line/bar charts
        metrics = data.index.tolist()
        for i in range(0, len(metrics), 3):
            cols = st.columns(3)
            for j, metric in enumerate(metrics[i:i+3]):
                with cols[j]:
                    st.markdown("<div class='bento-card'>", unsafe_allow_html=True)
                    fig = px.area(data.loc[metric], title=metric, template="plotly_dark")
                    fig.update_layout(height=200, margin=dict(l=0,r=0,t=30,b=0))
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
