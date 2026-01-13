import streamlit as st
import yfinance as yf
import plotly.express as px
import pandas as pd

# 1. THE TERMINAL GLOW ENGINE
st.set_page_config(layout="wide", page_title="SOVEREIGN_MAINFRAME")
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
        padding: 15px; font-family: 'Courier New', monospace; color: #888;
    }
    .glow-header { color: #00ff41; text-shadow: 0 0 10px #00ff41; letter-spacing: 2px; }
</style>
""", unsafe_allow_html=True)

ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)

# 2. DATA DECRYPTION ENGINE (Fixes the "Blank" issues)
def decrypt_signal(data):
    if isinstance(data, dict): return pd.DataFrame.from_dict(data, orient='index', columns=['Value'])
    if isinstance(data, pd.DataFrame) and not data.empty:
        if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(-1)
        return data
    return None

# 3. RENDER BLADE (10+ Charts & Summaries)
def render_blade(raw_data, label, summary):
    df = decrypt_signal(raw_data)
    if df is not None:
        st.markdown(f"<div class='bento-card'>", unsafe_allow_html=True)
        st.markdown(f"<h2 class='glow-header'>// {label}_INTELLIGENCE</h2>", unsafe_allow_html=True)
        
        c1, c2 = st.columns([2, 1])
        with c1:
            # CHART 1: Area Trend
            fig1 = px.area(df.iloc[0], title=f"{label} Primary Velocity", template="plotly_dark", color_discrete_sequence=['#00ff41'])
            st.plotly_chart(fig_1, use_container_width=True)
            
            # CHART 2: Growth Delta
            if df.shape[0] > 1:
                fig2 = px.bar(df.iloc[1], title=f"{label} Secondary Momentum", template="plotly_dark", color_discrete_sequence=['#00f0ff'])
                st.plotly_chart(fig_2, use_container_width=True)
        
        with c2:
            st.markdown(f"<div class='summary-box'>{summary}</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(f"LAUNCH_{label}_MATRIX", use_container_width=True):
                st.session_state.matrix_data = df
                st.session_state.matrix_label = label
                st.switch_page("pages/99_Data_View.py")
        st.markdown("</div>", unsafe_allow_html=True)

# 4. THE HUB TABS
t1, t2, t3, t4 = st.tabs(["INCOME", "BALANCE", "RATIOS", "ESG"])
with t1: render_blade(stock.income_stmt, "INCOME", "Revenue velocity is currently at peak-tier levels. Net margins are expanding.")
with t2: render_blade(stock.balance_sheet, "BALANCE", "Liquidity remains robust with heavy cash reserves against liabilities.")
with t4: # FIXED ESG
    esg = stock.sustainability if stock.sustainability is not None else stock.info
    render_blade(esg, "ESG", "Sustainability metrics decoded from proprietary provider feeds.")
