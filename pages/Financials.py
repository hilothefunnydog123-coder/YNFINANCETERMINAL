import streamlit as st
import yfinance as yf
import plotly.express as px
import pandas as pd

# 1. STYLE ENGINE
st.set_page_config(layout="wide", page_title="SOVEREIGN_HUB_v46")
st.markdown("""
<style>
    .bento-card { background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(0, 255, 65, 0.2); 
                  padding: 25px; border-radius: 20px; backdrop-filter: blur(15px); margin-bottom: 25px; }
    .summary-box { background: rgba(0, 255, 65, 0.05); border-left: 4px solid #00ff41; padding: 15px; 
                   font-family: monospace; color: #888; font-size: 13px; }
    .glow-header { color: #00ff41; text-shadow: 0 0 10px #00ff41; letter-spacing: 2px; }
</style>
""", unsafe_allow_html=True)

ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)

# 2. HUB RENDER ENGINE
def render_blade(df_raw, label, intel):
    if df_raw is not None and not df_raw.empty:
        # Peel Multi-Index for 2026 data
        if isinstance(df_raw.columns, pd.MultiIndex): df_raw.columns = df_raw.columns.get_level_values(-1)
        
        st.markdown(f"<div class='bento-card'>", unsafe_allow_html=True)
        st.markdown(f"<h2 class='glow-header'>// {label}_COMMAND_CENTER</h2>", unsafe_allow_html=True)
        c1, c2 = st.columns([2, 1])
        with c1:
            # Multi-Metric Relationship Chart
            fig = px.area(df_raw.iloc[:2].T, template="plotly_dark", color_discrete_sequence=['#00ff41', '#00f0ff'])
            fig.update_layout(height=350, margin=dict(l=0,r=0,t=20,b=0))
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.markdown(f"<div class='summary-box'><b>TACTICAL_INTEL:</b><br>{intel}</div>", unsafe_allow_html=True)
            if st.button(f"LAUNCH_{label}_DATA_MATRIX", use_container_width=True):
                st.session_state.matrix_data = df_raw
                st.session_state.matrix_label = label
                st.switch_page("pages/99_Data_View.py")
        st.markdown("</div>", unsafe_allow_html=True)

tabs = st.tabs(["INCOME", "BALANCE", "CASHFLOW"])
with tabs[0]: render_blade(stock.income_stmt, "INCOME", "Revenue velocity vs Margin compression analysis.")
with tabs[1]: render_blade(stock.balance_sheet, "BALANCE", "Capital architecture and asset liquidity surveillance.")
with tabs[2]: render_blade(stock.cashflow, "CASHFLOW", "Operational cash burn vs Capex reinvestment logic.")
