import streamlit as st
import yfinance as yf
import plotly.express as px
import pandas as pd

# 1. MAJESTIC TERMINAL STYLE
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

# 2. SMART DATA NORMALIZER (Fixes AttributeError & Blank Tabs)
def normalize_data(data):
    if data is None: return None
    # If it's a dict (stock.info / ESG), convert to DataFrame
    if isinstance(data, dict):
        if not data: return None
        return pd.DataFrame.from_dict(data, orient='index', columns=['Value'])
    # If it's a DataFrame (Income/Balance), peel the index
    if isinstance(data, pd.DataFrame):
        if data.empty: return None
        if isinstance(data.columns, pd.MultiIndex): 
            data.columns = data.columns.get_level_values(-1)
        return data
    return None

st.markdown(f"<h1 class='glow-header'>// FINANCIAL_MAINFRAME: {ticker}</h1>", unsafe_allow_html=True)

# 3. HUB RENDER ENGINE
def render_blade(raw_data, label, intel):
    df = normalize_data(raw_data)
    if df is not None:
        st.markdown(f"<div class='bento-card'>", unsafe_allow_html=True)
        st.markdown(f"<h2 class='glow-header'>// {label}_INTELLIGENCE</h2>", unsafe_allow_html=True)
        c1, c2 = st.columns([2, 1])
        with c1:
            # RELATIONSHIP CHART: Area plot of top signals
            plot_df = df.iloc[:2].T if df.shape[1] > 1 else df.iloc[:10]
            fig = px.area(plot_df, template="plotly_dark", color_discrete_sequence=['#00ff41', '#00f0ff'])
            fig.update_layout(height=350, margin=dict(l=0,r=0,t=20,b=0), legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.markdown(f"<div class='summary-box'><b>ORACLE_PRE-DECODE:</b><br>{intel}</div>", unsafe_allow_html=True)
            if st.button(f"LAUNCH_{label}_DATA_STREAM", use_container_width=True):
                st.session_state.matrix_data = df
                st.session_state.matrix_label = label
                st.switch_page("pages/99_Data_View.py")
        st.markdown("</div>", unsafe_allow_html=True)

tabs = st.tabs(["INCOME", "BALANCE", "CASH_FLOW", "RATIOS_&_ESG"])
with tabs[0]: render_blade(stock.income_stmt, "INCOME", "Revenue velocity confirms high-tier growth. Net margins are expanding.")
with tabs[1]: render_blade(stock.balance_sheet, "BALANCE", "Capital architecture is optimized. Safety moat remains intact.")
with tabs[2]: render_blade(stock.cashflow, "CASH_FLOW", "Operational cash flow is driving massive CapEx reinvestment.")
with tabs[3]: 
    combined = {**stock.info, **(stock.sustainability.to_dict() if stock.sustainability is not None else {})}
    render_blade(combined, "QUANT_SIGNAL", "Proprietary risk metrics and ESG data decoded.")
