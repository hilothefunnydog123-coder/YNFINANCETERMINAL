import streamlit as st
import yfinance as yf
import plotly.express as px
import pandas as pd

# 1. STYLE ENGINE
st.markdown("""
<style>
    .bento-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 255, 65, 0.3);
        padding: 15px; border-radius: 12px;
        backdrop-filter: blur(10px); margin-bottom: 15px;
        transition: 0.3s;
    }
    .bento-card:hover { border: 1px solid #00ff41; box-shadow: 0 0 20px rgba(0,255,65,0.2); }
</style>
""", unsafe_allow_html=True)

# 2. DATA LOAD
ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)
inf = stock.info

st.markdown(f"<h1 style='color:#00ff41;'>// FINANCIAL_MAINFRAME_v46: {ticker}</h1>", unsafe_allow_html=True)

# 3. THE "INFINITE" TAB ENGINE
# We create 10 Master Categories
master_tabs = st.tabs(["INCOME", "BALANCE", "CASHFLOW", "VALUATION", "GROWTH", "MARGINS", "LIQUIDITY", "EFFICIENCY", "ANALYSTS", "OWNERSHIP"])

# --- TAB 1: INCOME DEEP DIVE (15+ Charts) ---
with master_tabs[0]:
    st.markdown("### // INCOME_DYNAMICS_GRID")
    data = stock.income_stmt
    if not data.empty:
        # We loop through every line item in the Income Statement
        items = data.index.tolist()
        # Group metrics into blocks of 15 charts each
        for chunk in range(0, len(items), 15):
            with st.expander(f"SIGNAL_BLOCK_{chunk//15 + 1}: {items[chunk]}...", expanded=(chunk==0)):
                cols = st.columns(3)
                for i, metric in enumerate(items[chunk:chunk+15]):
                    with cols[i % 3]:
                        st.markdown(f"<div class='bento-card'>", unsafe_allow_html=True)
                        # Plotly Area Chart for every single line item
                        fig = px.area(data.loc[metric], title=metric, template="plotly_dark", color_discrete_sequence=['#00ff41'])
                        fig.update_layout(height=180, margin=dict(l=0,r=0,t=30,b=0), xaxis_title=None, yaxis_title=None)
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                        st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 2: VALUATION ENGINE (100+ Metrics) ---
with master_tabs[3]:
    st.markdown("### // VALUATION_LATTICE")
    # Dynamically pull every 'Price' or 'Ratio' related key from the 200+ info keys
    val_keys = [k for k in inf.keys() if any(x in k.lower() for x in ['price', 'ratio', 'pe', 'value', 'ebitda'])]
    
    # Render in a high-density grid
    for chunk in range(0, len(val_keys), 24):
        with st.expander(f"VALUATION_BLOCK_{chunk//24 + 1}"):
            cols = st.columns(4)
            for i, k in enumerate(val_keys[chunk:chunk+24]):
                with cols[i % 4]:
                    st.markdown(f"""
                    <div class='bento-card'>
                        <p style='color:#888; font-size:10px; margin:0;'>{k.upper()}</p>
                        <p style='color:#00ff41; font-size:18px; font-weight:bold;'>{inf.get(k, 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
