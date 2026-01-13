import streamlit as st
import yfinance as yf
import plotly.express as px
import pandas as pd

# 1. MAJESTIC TERMINAL STYLING
st.set_page_config(layout="wide", page_title="SOVEREIGN_HUB_v46")
st.markdown("""
<style>
    .bento-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(0, 255, 65, 0.2);
        padding: 25px; border-radius: 20px;
        backdrop-filter: blur(15px); margin-bottom: 25px;
    }
    .summary-box {
        background: rgba(0, 255, 65, 0.05);
        border-left: 4px solid #00ff41;
        padding: 15px; font-family: 'Courier New', monospace; color: #888; font-size: 13px;
    }
    .glow-header { color: #00ff41; text-shadow: 0 0 10px #00ff41; letter-spacing: 2px; }
</style>
""", unsafe_allow_html=True)

ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)

# 2. DATA DECRYPTION (Multi-Index Bypass)
def decrypt_signal(data):
    if isinstance(data, dict): return pd.DataFrame.from_dict(data, orient='index', columns=['Value'])
    if isinstance(data, pd.DataFrame) and not data.empty:
        if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(-1)
        return data
    return None

st.markdown(f"<h1 class='glow-header'>// FINANCIAL_MAINFRAME: {ticker}</h1>", unsafe_allow_html=True)

# 3. HUB RENDER ENGINE
def render_blade(raw_data, label, intel):
    df = decrypt_signal(raw_data)
    if df is not None:
        st.markdown(f"<div class='bento-card'>", unsafe_allow_html=True)
        st.markdown(f"<h2 class='glow-header'>// {label}_INTELLIGENCE</h2>", unsafe_allow_html=True)
        c1, c2 = st.columns([2, 1])
        with c1:
            # Multi-Chart Plot: Primary vs Secondary
            fig = px.area(df.iloc[:2].T, template="plotly_dark", color_discrete_sequence=['#00ff41', '#00f0ff'])
            fig.update_layout(height=350, margin=dict(l=0,r=0,t=30,b=0), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.markdown(f"<div class='summary-box'><b>TERMINAL_ANALYSIS:</b><br>{intel}</div>", unsafe_allow_html=True)
            if st.button(f"LAUNCH_{label}_MATRIX", use_container_width=True):
                st.session_state.matrix_data = df
                st.session_state.matrix_label = label
                st.switch_page("pages/99_Data_View.py")
        st.markdown("</div>", unsafe_allow_html=True)

# 4. TABS
t1, t2, t3, t4 = st.tabs(["INCOME", "BALANCE", "CASHFLOW", "QUANT_ESG"])
with t1: render_blade(stock.income_stmt, "INCOME", "Revenue velocity at peak. Margin expansion confirmed.")
with t2: render_blade(stock.balance_sheet, "BALANCE", "Safety moat robust. Asset liquidity high.")
with t3: render_blade(stock.cashflow, "CASHFLOW", "Operational efficiency driving FCF acceleration.")
with t4: 
    combined = {**stock.info, **(stock.sustainability.to_dict() if stock.sustainability is not None else {})}
    render_blade(combined, "QUANT_ESG", "Decoded ESG risk and Valuation multiples.")
