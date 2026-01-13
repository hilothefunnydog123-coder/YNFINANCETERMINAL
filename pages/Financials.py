import streamlit as st
import yfinance as yf
import plotly.express as px
import pandas as pd

# 1. MAJESTIC STYLE ENGINE
st.markdown("""
<style>
    .bento-card {
        background: rgba(0, 255, 65, 0.02);
        border: 1px solid rgba(0, 255, 65, 0.2);
        padding: 30px; border-radius: 24px;
        backdrop-filter: blur(20px); margin-bottom: 30px;
    }
    .intel-ribbon {
        background: rgba(0, 255, 65, 0.05);
        border-left: 5px solid #00ff41;
        padding: 15px; font-family: 'Courier New', monospace; color: #888;
    }
    .glow-header { color: #00ff41; text-shadow: 0 0 12px #00ff41; letter-spacing: 2px; }
</style>
""", unsafe_allow_html=True)

ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)

# 2. THE 2026 BYPASS ENGINE
def decrypt_matrix(df):
    if df is None or df.empty: return None
    if isinstance(df.columns, pd.MultiIndex): 
        df.columns = df.columns.get_level_values(-1)
    return df

st.markdown(f"<h1 class='glow-header'>// FINANCIAL_MAINFRAME: {ticker}</h1>", unsafe_allow_html=True)

# 3. HUB RENDER ENGINE
def render_blade(raw_data, label, analysis):
    df = decrypt_matrix(raw_data)
    if df is not None:
        st.markdown(f"<div class='bento-card'>", unsafe_allow_html=True)
        st.markdown(f"<h2 class='glow-header'>// {label}_INTELLIGENCE</h2>", unsafe_allow_html=True)
        c1, c2 = st.columns([2, 1])
        with c1:
            # RELATIONSHIP CHART: Revenue vs Net Income
            # This shows the "Relationship" between numbers, not just a list
            fig = px.area(df.iloc[:2].T, template="plotly_dark", color_discrete_sequence=['#00ff41', '#00f0ff'])
            fig.update_layout(height=350, margin=dict(l=0,r=0,t=10,b=0), legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.markdown(f"<div class='intel-ribbon'><b>DECODE_LOG:</b><br>{analysis}</div>", unsafe_allow_html=True)
            if st.button(f"LAUNCH_{label}_STREAM", use_container_width=True):
                st.session_state.matrix_data = df
                st.session_state.matrix_label = label
                st.switch_page("pages/99_Data_View.py")
        st.markdown("</div>", unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["INCOME", "BALANCE", "CASHFLOW", "ESG_QUANT"])
with t1: render_blade(stock.income_stmt, "INCOME", "Revenue velocity vs Margin compression analysis.")
with t2: render_blade(stock.balance_sheet, "BALANCE", "Asset liquidity vs Debt architecture.")
with t3: render_blade(stock.cashflow, "CASHFLOW", "Operational cash flow vs CapEx reinvestment logic.")
with t4: 
    combined = {**stock.info, **(stock.sustainability.to_dict() if stock.sustainability is not None else {})}
    render_blade(combined, "ESG_QUANT", "Proprietary risk signals and ESG metrics.")
