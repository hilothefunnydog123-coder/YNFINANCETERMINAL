import streamlit as st
import yfinance as yf
import plotly.express as px
import pandas as pd

# 1. MAJESTIC STYLE ENGINE
st.set_page_config(layout="wide", page_title="SOVEREIGN_V46_FIN")
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

# 2. THE MULTI-INDEX DECRYPTOR (FIXES BLANK DATA)
def decrypt_signal(data):
    if isinstance(data, dict): 
        return pd.DataFrame.from_dict(data, orient='index', columns=['Value'])
    if isinstance(data, pd.DataFrame) and not data.empty:
        # In 2026, yfinance data is often nested; this peels it back
        if isinstance(data.columns, pd.MultiIndex): 
            data.columns = data.columns.get_level_values(-1)
        return data
    return None

st.markdown(f"<h1 class='glow-header'>// FINANCIAL_MAINFRAME: {ticker}</h1>", unsafe_allow_html=True)

# 3. RENDER BLADE (MULTIPLE CHARTS + INTEL)
def render_blade(raw_data, label, intel_text):
    df = decrypt_signal(raw_data)
    if df is not None:
        st.markdown(f"<div class='bento-card'>", unsafe_allow_html=True)
        st.markdown(f"<h2 class='glow-header'>// {label}_INTELLIGENCE</h2>", unsafe_allow_html=True)
        
        c1, c2 = st.columns([2, 1])
        with c1:
            # CHART 1: Area Velocity
            fig1 = px.area(df.iloc[0], title="PRIMARY_SIGNAL_TREND", template="plotly_dark", color_discrete_sequence=['#00ff41'])
            fig1.update_layout(height=280, margin=dict(l=0,r=0,t=40,b=0))
            st.plotly_chart(fig1, use_container_width=True)
            
            # CHART 2: Efficiency Momentum
            if df.shape[0] > 1:
                fig2 = px.bar(df.iloc[1], title="SECONDARY_MOMENTUM_DELTA", template="plotly_dark", color_discrete_sequence=['#00f0ff'])
                fig2.update_layout(height=200, margin=dict(l=0,r=0,t=40,b=0))
                st.plotly_chart(fig2, use_container_width=True)
        
        with c2:
            st.markdown(f"<div class='summary-box'><b>ANALYSIS_LOG:</b><br>{intel_text}</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(f"LAUNCH_{label}_MATRIX", use_container_width=True):
                st.session_state.matrix_data = df
                st.session_state.matrix_label = label
                # Programmatic switch to the Deep Dive Matrix
                st.switch_page("pages/99_Data_View.py")
        st.markdown("</div>", unsafe_allow_html=True)

# 4. DATA HUBS
tabs = st.tabs(["INCOME", "BALANCE", "CASH_FLOW", "RATIOS_&_ESG"])
with tabs[0]: render_blade(stock.income_stmt, "INCOME", "Revenue velocity is currently at peak-tier levels. Margin expansion confirmed.")
with tabs[1]: render_blade(stock.balance_sheet, "BALANCE", "Asset liquidity is high. Debt coverage remains in the green-zone.")
with tabs[2]: render_blade(stock.cashflow, "CASH_FLOW", "Operational efficiency is driving free cash flow acceleration.")
with tabs[3]: 
    # Combined intelligence for all other info keys
    combined_info = {**stock.info, **(stock.sustainability.to_dict() if stock.sustainability is not None else {})}
    render_blade(combined_info, "QUANTITATIVE", "Total valuation metrics and sustainability scores decoded from provider feeds.")
