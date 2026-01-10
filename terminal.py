import streamlit as st
import yfinance as yf
import pandas_ta as ta
import vectorbt as vbt
import plotly.graph_objects as go
import pandas as pd

# --- 1. PAGE SETUP & BLOOMBERG CSS ---
st.set_page_config(layout="wide", page_title="ULTRA_TERMINAL_V5")

st.markdown("""
    <style>
    .stApp { background: #000000; color: #00ff41; font-family: 'Courier New', monospace; }
    [data-testid="stSidebar"] { background-color: #050505; border-right: 2px solid #00ff41; }
    
    /* Ticker Tape Animation */
    @keyframes marquee { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    .ticker-tape { 
        background: #111; border-bottom: 2px solid #00ff41; padding: 5px; 
        overflow: hidden; white-space: nowrap; width: 100%;
    }
    .ticker-tape span { display: inline-block; animation: marquee 20s linear infinite; }

    /* Button Grid Styling */
    .stButton>button { 
        background: transparent; color: #00ff41; border: 1px solid #333; 
        font-size: 10px; width: 100%; height: 30px;
    }
    .stButton>button:hover { border-color: #00ff41; box-shadow: 0 0 10px #00ff41; }
    </style>
""", unsafe_allow_html=True)

# --- 2. TICKER TAPE ---
st.markdown('<div class="ticker-tape"><span>NVDA: $124.50 (+2.4%) | AAPL: $214.20 (-0.4%) | BTC-USD: $64,210 (+1.2%) | TSLA: $210.10 (+5.1%)</span></div>', unsafe_allow_html=True)

# --- 3. SESSION STATE ENGINE (Fixes the "Nothing Works" bug) ---
if 'active_ticker' not in st.session_state:
    st.session_state.active_ticker = "NVDA"

# --- 4. THE COMMAND CENTER LAYOUT ---
left_btn, center_main, right_btn = st.columns([1, 5, 1])

# LEFT SIDE BUTTONS (5 indicators)
with left_btn:
    st.markdown("### // IND_CTRL")
    for i in range(5):
        if st.button(f"STRAT_LOG_{i}"): st.toast(f"Activating Matrix {i}")
    st.markdown("---")
    st.selectbox("TIMEFRAME", ["1m", "5m", "1h", "1d"])

# RIGHT SIDE BUTTONS (5 execution)
with right_btn:
    st.markdown("### // EXEC_CTRL")
    for i in range(5):
        if st.button(f"ORDER_TYP_{i}"): st.toast(f"Executing Order {i}")
    st.markdown("---")
    st.metric("NET_SIG", "94.2%", "+1.2%")

# --- 5. CENTER MAIN (Deep Data) ---
with center_main:
    ticker = st.text_input("SET_TICKER", value=st.session_state.active_ticker).upper()
    st.session_state.active_ticker = ticker
    
    tab1, tab2, tab3 = st.tabs(["📊 ANALYSIS", "📉 OPTIONS_CHAIN", "💰 DIVIDENDS"])
    
    # LOAD DATA
    stock = yf.Ticker(ticker)
    df = stock.history(period="2y")
    
    with tab1:
        # Complex Chart with Indicators
        df['EMA20'] = ta.ema(df['Close'], length=20)
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name="EMA20", line=dict(color="#00ff41")))
        fig.update_layout(template="plotly_dark", height=600, paper_bgcolor='black', plot_bgcolor='black')
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("// SCROLLABLE_OPTIONS_MATRIX")
        # Fetching multiple expiries to make it "scroll forever"
        try:
            expiries = stock.options[:3] 
            chains = [stock.option_chain(x).calls for x in expiries]
            mega_chain = pd.concat(chains)
            st.dataframe(mega_chain, height=600, use_container_width=True)
        except:
            st.write("NO OPTIONS DATA FOUND")

    with tab3:
        st.subheader("// DIVIDEND_YIELD_HISTORY")
        divs = stock.dividends
        if not divs.empty:
            st.bar_chart(divs)
        else:
            st.write("NO DIVIDENDS RECORDED")
