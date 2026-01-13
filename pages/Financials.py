import streamlit as st
import yfinance as yf
import plotly.express as px
import pandas as pd

# 1. MAJESTIC GLOBAL STYLES
st.markdown("""
<style>
    .reportview-container { background: #050505; }
    .bento-card {
        background: rgba(0, 255, 65, 0.02);
        border: 1px solid rgba(0, 255, 65, 0.2);
        padding: 25px; border-radius: 20px;
        backdrop-filter: blur(15px); margin-bottom: 25px;
        transition: 0.4s ease;
    }
    .bento-card:hover { border: 1px solid #00ff41; box-shadow: 0 0 30px rgba(0, 255, 65, 0.1); }
    .summary-text { color: #888; font-family: 'Courier New', monospace; font-size: 14px; line-height: 1.6; }
    .glow-header { color: #00ff41; text-shadow: 0 0 10px #00ff41; font-family: 'Orbitron', sans-serif; letter-spacing: 2px; }
</style>
""", unsafe_allow_html=True)

ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)

st.markdown(f"<h1 class='glow-header'>// FINANCIAL_COMMAND_CENTER: {ticker}</h1>", unsafe_allow_html=True)

# --- ESG RECOVERY LOGIC ---
def get_esg_data(stock):
    # Try sustainability first, then fallback to info keys
    esg = stock.sustainability
    if esg is not None and not esg.empty:
        return esg
    # Manual extraction from info dictionary
    inf = stock.info
    esg_map = {k: v for k, v in inf.items() if 'esg' in k.lower() or 'carbon' in k.lower()}
    if esg_map:
        return pd.DataFrame.from_dict(esg_map, orient='index', columns=['Value'])
    return None

# --- TABBED INTELLIGENCE HUB ---
tabs = st.tabs(["INCOME", "BALANCE", "RATIOS", "ESG_SURVEILLANCE"])

with tabs[0]:
    st.markdown("<div class='bento-card'>", unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown("### // REVENUE_VS_NET_INCOME")
        # Multi-Metric Chart
        inc = stock.income_stmt.T
        if not inc.empty:
            fig = px.area(inc, y=["Total Revenue", "Net Income"], 
                          template="plotly_dark", color_discrete_sequence=['#00ff41', '#00f0ff'])
            fig.update_layout(height=400, margin=dict(l=0,r=0,t=20,b=0))
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<p class='summary-text'><b>ANALYST_SUMMARY:</b><br>Revenue velocity indicates high-tier scalability. Net margins are expanding against sector averages. Click below for the raw matrix stream.</p>", unsafe_allow_html=True)
        if st.button("LAUNCH_DATA_MATRIX", key="inc_btn"):
            st.session_state.deep_dive = stock.income_stmt
            st.switch_page("pages/99_Data_View.py")
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[3]: # ESG HUB
    esg_final = get_esg_data(stock)
    if esg_final is not None:
        st.markdown("<div class='bento-card'>", unsafe_allow_html=True)
        e1, e2 = st.columns([2, 1])
        with e1:
            st.markdown("### // SUSTAINABILITY_RISK_PROFILE")
            fig_esg = px.bar(esg_final, template="plotly_dark", color_discrete_sequence=['#00ff41'])
            st.plotly_chart(fig_esg, use_container_width=True)
        with e2:
            st.markdown("<p class='summary-text'><b>ESG_INTELLIGENCE:</b><br>Monitoring environmental impact and governance risk. Higher scores indicate potential institutional divestment risk.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error("ESG_DATA_ENCRYPTED: No public sustainability records found.")
