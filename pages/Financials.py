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

# 2. SMART DATA NORMALIZER (Fixes AttributeError & 2026 Index Issues)
def normalize_matrix(data):
    if data is None: return None
    # Dictionary Handler (stock.info / ESG)
    if isinstance(data, dict):
        if not data: return None
        return pd.DataFrame.from_dict(data, orient='index', columns=['Value'])
    # DataFrame Handler (Income / Balance)
    if isinstance(data, pd.DataFrame):
        if data.empty: return None
        # Peel any number of MultiIndex levels (2026 specific)
        while isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(-1)
        return data
    return None

st.markdown(f"<h1 class='glow-header'>// COMMAND_HUB: {ticker}</h1>", unsafe_allow_html=True)

# 3. HUB RENDER ENGINE
def render_blade(raw_data, label, analysis):
    df = normalize_matrix(raw_data)
    if df is not None:
        st.markdown(f"<div class='bento-card'>", unsafe_allow_html=True)
        st.markdown(f"<h2 class='glow-header'>// {label}_INTELLIGENCE</h2>", unsafe_allow_html=True)
        c1, c2 = st.columns([2, 1])
        with c1:
            # RELATIONSHIP CHART: Layered Area (Top 3 Metrics)
            plot_df = df.iloc[:3].T if df.shape[1] > 1 else df.iloc[:10]
            fig = px.area(plot_df, template="plotly_dark", color_discrete_sequence=['#00ff41', '#00f0ff', '#ff4b4b'])
            fig.update_layout(height=400, margin=dict(l=0,r=0,t=20,b=0), legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.markdown(f"<div class='summary-box'><b>TACTICAL_LOG:</b><br>{analysis}</div>", unsafe_allow_html=True)
            if st.button(f"LAUNCH_{label}_DATA_STREAM", use_container_width=True):
                st.session_state.matrix_data = df
                st.session_state.matrix_label = label
                st.switch_page("pages/99_Data_View.py")
        st.markdown("</div>", unsafe_allow_html=True)

tabs = st.tabs(["INCOME", "BALANCE", "CASH_FLOW", "RATIOS_&_ESG"])
with tabs[0]: render_blade(stock.income_stmt, "INCOME", "Revenue velocity vs Margin compression analysis.")
with tabs[1]: render_blade(stock.balance_sheet, "BALANCE", "Capital architecture surveillance and liquidity check.")
with tabs[2]: render_blade(stock.cashflow, "CASH_FLOW", "Operational efficiency and reinvestment logic.")
with tabs[3]: 
    combined = {**stock.info, **(stock.sustainability.to_dict() if stock.sustainability is not None else {})}
    render_blade(combined, "QUANT_SIGNAL", "ESG risk factors and valuation multiples.")
