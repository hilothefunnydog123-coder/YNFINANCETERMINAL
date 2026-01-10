import streamlit as st
import yfinance as yf
import pandas_ta as ta
import vectorbt as vbt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# --- BLOOMBERG UI OVERHAUL ---
st.set_page_config(layout="wide", page_title="TERMINAL_ULTRA_V5")

st.markdown("""
    <style>
    /* Full Dark Mode Theme */
    .stApp { background: #000000; color: #00ff41; font-family: 'Courier New', monospace; }
    
    /* Ticker Tape Animation */
    @keyframes marquee { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    .ticker-tape { 
        white-space: nowrap; overflow: hidden; background: #111; border-bottom: 2px solid #00ff41;
        padding: 5px; font-weight: bold; font-size: 14px; position: fixed; top: 0; left: 0; width: 100%; z-index: 1000;
    }
    .ticker-tape span { display: inline-block; padding-left: 100%; animation: marquee 30s linear infinite; }

    /* Button Styling */
    .stButton>button { 
        background: transparent; color: #00ff41; border: 1px solid #333; 
        font-size: 10px !important; height: 30px; width: 100%; transition: 0.3s;
    }
    .stButton>button:hover { border-color: #00ff41; box-shadow: 0 0 10px #00ff41; color: #fff; }
    
    /* Scrollable Options Table */
    .scroll-table { height: 800px; overflow-y: auto; border: 1px solid #333; }
    </style>
""", unsafe_allow_html=True)

# 1. LIVE TICKER TAPE
st.markdown('<div class="ticker-tape"><span>NVDA: $124.50 (+2.4%) | AAPL: $214.20 (-0.4%) | BTC-USD: $64,210 (+1.2%) | ETH-USD: $3,450 (-0.8%) | TSLA: $210.10 (+5.1%)</span></div>', unsafe_allow_html=True)
st.write("") # Spacer

# 2. THE 3-PANEL COMMAND CENTER
left_wing, center_main, right_wing = st.columns([1, 4, 1])

# --- LEFT WING: INDICATOR CONTROLS ---
with left_wing:
    st.markdown("### // IND_CTRL")
    for i in range(1, 11):
        if st.button(f"SIGNAL_{i:02d}", key=f"l{i}"):
            st.toast(f"Loading Signal Matrix {i}...")
    st.markdown("---")
    st.subheader("PARAM_ADJ")
    st.slider("SENSITIVITY", 0.1, 1.0, 0.5)

# --- CENTER MAIN: THE MEGADATA HUB ---
with center_main:
    ticker = st.text_input("SET_TICKER", value="AAPL").upper().strip()
    tab1, tab2, tab3, tab4 = st.tabs(["📊 CHART", "📉 OPTIONS_CHAIN", "💸 DIVIDENDS", "📑 MACRO_DATA"])
    
    # Auto-Load Engine
    stock = yf.Ticker(ticker)
    df = stock.history(period="5y")
    
    with tab1:
        # Complex Multi-Subplot Chart
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.5, 0.2, 0.3])
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']), row=1, col=1)
        fig.add_trace(go.Bar(x=df.index, y=df['Volume']), row=2, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=ta.rsi(df['Close'])), row=3, col=1)
        fig.update_layout(template="plotly_dark", height=800, margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("// FULL_OPTIONS_MATRIX")
        expiries = stock.options
        all_calls = []
        for d in expiries[:5]: # Fetching first 5 expiries for speed
            all_calls.append(stock.option_chain(d).calls)
        calls_df = pd.concat(all_calls)
        st.markdown('<div class="scroll-table">', unsafe_allow_html=True)
        st.dataframe(calls_df, height=700)
        st.markdown('</div>', unsafe_allow_html=True)

# --- RIGHT WING: EXECUTION & SOCIAL ---
with right_wing:
    st.markdown("### // EXEC_CTRL")
    for i in range(1, 11):
        if st.button(f"ORDER_TYPE_{i:02d}", key=f"r{i}"):
            st.toast(f"Executing Macro Order {i}...")
    st.markdown("---")
    st.metric("NET_SIG", "94.2%", "+1.2%")
    st.metric("WHALE_VOL", "2.1B", "-0.4%")
