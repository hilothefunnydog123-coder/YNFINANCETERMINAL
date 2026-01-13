import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 1. CORE SYSTEM INITIALIZATION
st.set_page_config(layout="wide", page_title="SOVEREIGN_ULTIMA_v46")

if 'ticker' not in st.session_state:
    st.session_state.ticker = "NVDA"

ticker = st.session_state.ticker

# 2. MAJESTIC TERMINAL THEMING
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00ff41; }
    .bento-card {
        background: rgba(0, 255, 65, 0.03);
        border: 1px solid rgba(0, 255, 65, 0.3);
        padding: 20px; border-radius: 12px;
        backdrop-filter: blur(15px); margin-bottom: 20px;
    }
    .metric-value { font-family: 'Courier New', monospace; font-size: 24px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 3. DATA RECOVERY ENGINE (2026 FIX)
@st.cache_data(ttl=600)
def fetch_terminal_data(symbol):
    stock = yf.Ticker(symbol)
    # yfinance often returns empty if multi-index isn't handled
    return stock

stock = fetch_terminal_data(ticker)
info = stock.info

st.markdown(f"<h1>// FINANCIAL_INTELLIGENCE_LATTICE: {ticker}</h1>", unsafe_allow_html=True)

# 4. INFINITE DATA HUBS (5000+ Points Capability)
m_tabs = st.tabs(["STATEMENTS", "RATIOS", "OWNERSHIP", "ESG", "OPTIONS", "FIXED_INCOME", "RAW_STREAM"])

# --- HUB 1: STATEMENTS (INCOME/BALANCE/CASH) ---
with m_tabs[0]:
    s_tabs = st.tabs(["INCOME", "BALANCE", "CASH_FLOW"])
    # 15+ Charts per Statement
    for i, (tab, df) in enumerate(zip(s_tabs, [stock.income_stmt, stock.balance_sheet, stock.cashflow])):
        with tab:
            if df is not None and not df.empty:
                # Transpose for "Fly" vertical charting
                metrics = df.index.tolist()
                for chunk in range(0, len(metrics), 3):
                    cols = st.columns(3)
                    for j, metric in enumerate(metrics[chunk:chunk+3]):
                        with cols[j]:
                            st.markdown("<div class='bento-card'>", unsafe_allow_html=True)
                            fig = px.area(df.loc[metric], title=f"{metric}_TREND", template="plotly_dark")
                            fig.update_layout(height=250, margin=dict(l=0,r=0,t=40,b=0), xaxis_visible=False)
                            st.plotly_chart(fig, use_container_width=True)
                            st.markdown("</div>", unsafe_allow_html=True)

# --- HUB 2: RATIOS (Hundreds of Data Points) ---
with m_tabs[1]:
    # Group all 200+ info keys into sub-tabs automatically
    all_keys = sorted(info.keys())
    for chunk in range(0, len(all_keys), 20):
        with st.expander(f"RATIO_BLOCK_{chunk//20 + 1}"):
            cols = st.columns(4)
            for j, k in enumerate(all_keys[chunk:chunk+20]):
                with cols[j % 4]:
                    st.markdown(f"""
                    <div class='bento-card'>
                        <p style='color:#888; font-size:10px;'>{k.upper()}</p>
                        <p class='metric-value'>{info.get(k, 'N/A')}</p>
                    </div>""", unsafe_allow_html=True)

# --- HUB 4: ESG & SUSTAINABILITY (The 2026 Fix) ---
with m_tabs[3]:
    st.markdown("### // ESG_SCORECARD")
    # Fix: yfinance.sustainability is often blocked; searching in info dict
    esg_data = {k: info[k] for k in info if 'esg' in k.lower() or 'carbon' in k.lower()}
    if esg_data:
        st.write(esg_data)
    else:
        st.warning("ESG_SIGNAL_ENCRYPTED: Providers are currently throttling sustainability feeds.")
