import streamlit as st
import yfinance as yf
import plotly.express as px

# 1. STYLE INJECTION
st.markdown("""
<style>
    .bento-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 255, 65, 0.2);
        padding: 20px; border-radius: 12px;
        backdrop-filter: blur(10px); margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# 2. DATA LOAD
ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)
info = stock.info

st.markdown(f"<h1 style='color:#00ff41;'>// TERMINAL_MAINFRAME: {ticker}</h1>", unsafe_allow_html=True)

# 3. DYNAMIC TAB GENERATOR (5000+ Potential Data Points)
# We group the hundreds of keys in info into logical "Super-Tabs"
data_categories = {
    "VALUATION": ["trailingPE", "forwardPE", "priceToBook", "enterpriseToEbitda", "pegRatio"],
    "PROFITABILITY": ["profitMargins", "operatingMargins", "returnOnEquity", "returnOnAssets"],
    "CASH_FLOW": ["operatingCashflow", "freeCashflow", "totalCash", "totalDebt"],
    "FORECASTS": ["targetMedianPrice", "targetMeanPrice", "numberOfAnalystOpinions"],
    "GOVERNANCE": ["auditRisk", "boardRisk", "compensationRisk", "shareHolderRightsRisk"]
}

# Create Super-Tabs
super_tabs = st.tabs(list(data_categories.keys()) + ["ALL_METRICS_STREAM"])

for i, (category, keys) in enumerate(data_categories.items()):
    with super_tabs[i]:
        st.markdown(f"### // {category}_DYNAMICS")
        # Create a Bento Grid for these keys
        cols = st.columns(3)
        for idx, key in enumerate(keys):
            with cols[idx % 3]:
                st.markdown(f"<div class='bento-card'>", unsafe_allow_html=True)
                st.metric(key.upper(), info.get(key, 'N/A'))
                # Optional: Add a mini-chart for each metric if historical exists
                st.markdown("</div>", unsafe_allow_html=True)

# 4. THE "INFINITE" STREAM TAB
with super_tabs[-1]:
    st.markdown("### // RAW_SIGNAL_STREAM")
    # This loop generates a tab for EVERY single key in the dictionary
    all_keys = list(info.keys())
    # To prevent browser crash, we show them in an expandable grid
    for start in range(0, len(all_keys), 20):
        with st.expander(f"SIGNAL_BLOCK_{start//20 + 1}"):
            cols = st.columns(4)
            for j, k in enumerate(all_keys[start:start+20]):
                cols[j % 4].write(f"**{k}**: {info.get(k)}")
