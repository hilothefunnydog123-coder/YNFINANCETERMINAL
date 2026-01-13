import streamlit as st
import yfinance as yf
import plotly.express as px
import pandas as pd

# 1. THE TERMINAL GLOW ENGINE
st.set_page_config(layout="wide", page_title="SOVEREIGN_V46_CORE")

st.markdown("""
<style>
    /* Glassmorphism Matrix Styling */
    .stApp { background-color: #050505; color: #00ff41; }
    div[data-testid="stMetric"] {
        background: rgba(0, 255, 65, 0.05);
        border: 1px solid rgba(0, 255, 65, 0.3);
        padding: 20px; border-radius: 15px;
        backdrop-filter: blur(10px);
    }
    .status-text { font-family: 'Courier New', monospace; font-size: 10px; color: #888; }
</style>
""", unsafe_allow_html=True)

# 2. DATA DECRYPTION ENGINE
ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)

def get_majestical_data(df, label):
    """Bypasses Multi-Index blocks and renders 'Fly' visual cards"""
    if df is None or df.empty:
        return st.warning(f"SIGNAL_OFFLINE: {label} is currently encrypted by provider.")
    
    # PEELING THE INDEX: Crucial for 2026 yfinance
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
        
    st.markdown(f"### // {label}_MATRIX")
    # THE 5000+ TAB STRATEGY: One tab per line item
    metrics = df.index.tolist()
    m_tabs = st.tabs([m.replace(" ", "_").upper() for m in metrics[:20]]) # Limit to top 20 for speed
    
    for i, metric in enumerate(metrics[:20]):
        with m_tabs[i]:
            c1, c2 = st.columns([1, 2])
            with c1:
                st.markdown("<div style='padding:20px;'>", unsafe_allow_html=True)
                st.metric(metric, f"${df.loc[metric].iloc[0]:,.0f}", 
                          delta=f"{(df.loc[metric].iloc[0]/df.loc[metric].iloc[1]-1)*100:.2f}%")
                st.markdown("</div>", unsafe_allow_html=True)
            with c2:
                # Rendering fly area charts instead of spreadsheets
                fig = px.area(df.loc[metric], template="plotly_dark", color_discrete_sequence=['#00ff41'])
                fig.update_layout(height=200, margin=dict(l=0,r=0,t=0,b=0), xaxis_visible=False)
                st.plotly_chart(fig, use_container_width=True)

# 3. THE 20-HUB MAIN MENU
st.markdown("<h1>// FINANCIAL_INTELLIGENCE_LATTICE</h1>", unsafe_allow_html=True)
st.caption("DECRYPTING_SIGNAL: ENHANCED_MULTI_INDEX_BYPASS_v4.6")

hub_tabs = st.tabs(["INCOME", "BALANCE", "CASH_FLOW", "RATIOS", "OWNERSHIP", "ESG", "OPTIONS"])

with hub_tabs[0]: get_majestical_data(stock.income_stmt, "INCOME")
with hub_tabs[1]: get_majestical_data(stock.balance_sheet, "BALANCE")
with hub_tabs[2]: get_majestical_data(stock.cashflow, "CASH_FLOW")

with hub_tabs[4]: # OWNERSHIP (Category 8)
    st.markdown("### // INSTITUTIONAL_FLOWS")
    o1, o2 = st.columns(2)
    with o1:
        holders = stock.major_holders
        if holders is not None:
            st.dataframe(holders, use_container_width=True)
    with o2:
        inst = stock.institutional_holders
        if inst is not None:
            # Charting institutional holdings
            fig_inst = px.bar(inst, x='Holder', y='Value', template="plotly_dark")
            st.plotly_chart(fig_inst, use_container_width=True)

with hub_tabs[6]: # OPTIONS (Category 9)
    st.markdown("### // DERIVATIVES_SURVEILLANCE")
    try:
        expiry = st.selectbox("EXPIRATION_CYCLE", stock.options)
        chain = stock.option_chain(expiry)
        st.dataframe(chain.calls, use_container_width=True)
    except:
        st.error("DERIVATIVES_LINK_BROKEN")
