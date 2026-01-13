import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# --- THE CACHE FIX ---
# We use cache_resource because Ticker objects are NOT serializable
@st.cache_resource(ttl=3600)
def fetch_terminal_data(symbol):
    try:
        return yf.Ticker(symbol)
    except Exception as e:
        st.error(f"CONNECTION_FAILURE: {str(e)}")
        return None

ticker_symbol = st.session_state.get('ticker', 'NVDA')
stock = fetch_terminal_data(ticker_symbol)

# --- THE DATA DECRYPTION ENGINE ---
def clean_df(df):
    """Flattens 2026 Multi-Index tables so they actually work"""
    if df is None or df.empty:
        return None
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(-1)
    return df

# --- THE "MORE DATA" GRID ENGINE ---
def render_infinite_grid(df, title):
    df = clean_df(df)
    if df is not None:
        st.markdown(f"### // {title}_MATRIX")
        metrics = df.index.tolist()
        
        # We generate A TON of charts in a grid
        for i in range(0, len(metrics), 3):
            cols = st.columns(3)
            for j, metric in enumerate(metrics[i:i+3]):
                with cols[j]:
                    with st.container(border=True):
                        st.markdown(f"<span style='color:#888; font-size:10px;'>{metric}</span>", unsafe_allow_html=True)
                        # Plotting every individual line item as a 'Fly' Area Chart
                        fig = px.area(df.loc[metric], template="plotly_dark", color_discrete_sequence=['#00ff41'])
                        fig.update_layout(height=150, margin=dict(l=0,r=0,t=0,b=0), xaxis_visible=False, yaxis_visible=False)
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    else:
        st.warning(f"SIGNAL_OFFLINE: {title}")

# --- THE MAJESTIC HUB ---
st.markdown(f"<h1>// SOVEREIGN_CORE: {ticker_symbol}</h1>", unsafe_allow_html=True)

tab_names = ["INCOME", "BALANCE", "CASHFLOW", "RATIOS", "ESG", "HOLDERS", "OPTIONS", "NEWS"]
tabs = st.tabs(tab_names)

with tabs[0]: render_infinite_grid(stock.income_stmt, "INCOME")
with tabs[1]: render_infinite_grid(stock.balance_sheet, "BALANCE")
with tabs[2]: render_infinite_grid(stock.cashflow, "CASHFLOW")

with tabs[3]: # RATIOS (The 'Hundreds of numbers' request)
    inf = stock.info
    # Pulling EVERY single key in the dictionary
    all_keys = sorted(inf.keys())
    for chunk in range(0, len(all_keys), 20):
        with st.expander(f"DATA_PACK_{chunk//20 + 1}"):
            cols = st.columns(4)
            for k_idx, key in enumerate(all_keys[chunk:chunk+20]):
                cols[k_idx % 4].metric(key[:15], f"{inf.get(key, 'N/A')}")
