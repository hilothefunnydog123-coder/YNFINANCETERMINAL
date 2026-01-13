import streamlit as st
import yfinance as yf
import plotly.express as px
import pandas as pd

# 1. THE GLASS TERMINAL CSS
st.set_page_config(layout="wide", page_title="SOVEREIGN_ULTIMA")

st.markdown("""
<style>
    /* Glassmorphism Bento Cards */
    .bento-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 255, 65, 0.2);
        padding: 20px;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }
    .bento-card:hover { transform: scale(1.02); border: 1px solid #00ff41; }
    .metric-label { color: #888; font-size: 0.8rem; text-transform: uppercase; }
    .metric-value { color: #00ff41; font-size: 1.5rem; font-family: 'monospace'; }
</style>
""", unsafe_allow_html=True)

# 2. DATA INITIALIZATION
ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)
inf = stock.info

st.markdown(f"<h1 style='color:#00ff41; text-shadow:0 0 10px #00ff41;'>// FINANCIAL_MAINFRAME: {ticker}</h1>", unsafe_allow_html=True)

# 3. THE 20-TAB HUB SYSTEM
# We create a tab for every single major category you listed.
m_tabs = st.tabs(["IDENTIFICATION", "REAL-TIME", "FUNDAMENTALS", "RATIOS", "ESTIMATES", "OWNERSHIP", "OPTIONS", "ESG", "DERIVATIVES", "FIXED_INCOME"])

# --- TAB 1: FUNDAMENTALS (REVENUE, EBITDA, ETC) ---
with m_tabs[2]:
    st.markdown("### // CORE_STATEMENTS_MATRIX")
    # Sub-tabs for deep diving
    s_tabs = st.tabs(["INCOME", "BALANCE", "CASH_FLOW", "SEGMENTS"])
    
    with s_tabs[0]:
        # Instead of a spreadsheet, we generate 15+ individual charts for the Income Statement
        income = stock.income_stmt
        cols = st.columns(3)
        metrics = income.index.tolist()
        for i, metric in enumerate(metrics[:15]): # First 15 major line items
            with cols[i % 3]:
                st.markdown(f"<div class='bento-card'>", unsafe_allow_html=True)
                fig = px.bar(income.loc[metric], title=metric, template="plotly_dark", color_discrete_sequence=['#00ff41'])
                fig.update_layout(height=200, margin=dict(l=0,r=0,t=30,b=0), xaxis_title=None, yaxis_title=None)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 2: RATIOS (100+ METRICS) ---
with m_tabs[3]:
    st.markdown("### // QUANTITATIVE_RATIO_LATTICE")
    # We group ratios into logical clusters
    clusters = {
        "Valuation": ["trailingPE", "forwardPE", "priceToBook", "enterpriseToRevenue", "enterpriseToEbitda"],
        "Profitability": ["profitMargins", "operatingMargins", "returnOnEquity", "returnOnAssets"],
        "Liquidity": ["currentRatio", "quickRatio", "debtToEquity", "totalCashPerShare"]
    }
    
    for cluster, keys in clusters.items():
        st.markdown(f"#### {cluster}")
        c_cols = st.columns(len(keys))
        for i, k in enumerate(keys):
            with c_cols[i]:
                st.markdown(f"""
                <div class='bento-card'>
                    <div class='metric-label'>{k}</div>
                    <div class='metric-value'>{inf.get(k, 'N/A')}</div>
                </div>
                """, unsafe_allow_html=True)

# --- TAB 3: OWNERSHIP (13F, INSTITUTIONS) ---
with m_tabs[5]:
    st.markdown("### // SHAREHOLDER_DYNAMICS")
    o1, o2 = st.columns(2)
    with o1:
        holders = stock.major_holders
        fig_pie = px.pie(holders, values=0, names=1, title="Ownership Mix", template="plotly_dark")
        st.plotly_chart(fig_pie, use_container_width=True)
    with o2:
        st.markdown("#### Top Institutional Holders")
        st.dataframe(stock.institutional_holders, use_container_width=True)
