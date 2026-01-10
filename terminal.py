import streamlit as st
import yfinance as yf
import pandas_ta as ta
import vectorbt as vbt
import plotly.graph_objects as go

# 1. THE LOOK: Bloomberg Dark Mode
st.set_page_config(layout="wide", page_title="BB-LIGHT TERMINAL")
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #00ff41; }
    [data-testid="stSidebar"] { background-color: #111; border-right: 1px solid #333; }
    h1, h2, h3 { color: #00ff41 !important; font-family: 'Courier New', monospace; }
    </style>
    """, unsafe_allow_all_html=True)

st.title("📟 QUANT-TERMINAL // CLOUD_v1")

# 2. SIDEBAR COMMANDS
with st.sidebar:
    st.header("EXECUTION CTRL")
    ticker = st.text_input("SYMBOL", value="BTC-USD").upper()
    fast_ma = st.slider("FAST WINDOW", 5, 50, 20)
    slow_ma = st.slider("SLOW WINDOW", 20, 200, 50)
    st.markdown("---")
    st.info("Status: CLOUD_READY_STABLE")

# 3. FAST DATA ENGINE
@st.cache_data
def load_data(symbol):
    df = yf.download(symbol, period="5y")
    df['RSI'] = ta.rsi(df['Close'], length=14)
    return df

try:
    data = load_data(ticker)
    
    # 4. DASHBOARD METRICS
    c1, c2, c3 = st.columns(3)
    c1.metric("PRICE", f"${data['Close'].iloc[-1]:,.2f}")
    c2.metric("RSI (14)", f"{data['RSI'].iloc[-1]:.2f}")
    c3.metric("52W HIGH", f"${data['High'].max():,.2f}")

    # 5. THE BACKTEST (VectorBT)
    # This is the "Cheat Code" math that runs instantly
    close = data['Close']
    fast_m = vbt.MA.run(close, fast_ma)
    slow_m = vbt.MA.run(close, slow_ma)
    entries = fast_m.ma_crossed_above(slow_m)
    exits = fast_m.ma_crossed_below(slow_m)
    
    pf = vbt.Portfolio.from_signals(close, entries, exits, init_cash=10000)

    # 6. VISUALIZATION
    st.subheader("STRATEGY EQUITY CURVE")
    st.plotly_chart(pf.plot(), use_container_width=True)
    
    st.subheader("INSTITUTIONAL PERFORMANCE STATS")
    st.table(pf.stats())

except Exception as e:
    st.error(f"Waiting for Valid Ticker... (Error: {e})")
