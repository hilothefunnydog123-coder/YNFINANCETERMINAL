import streamlit as st
from openbb import obb
import vectorbt as vbt
import pandas as pd

# Terminal Aesthetics
st.set_page_config(layout="wide", page_title="BB-VBT QUANT TERMINAL")
st.title("🏛️ YNFINANCE INSIDER TERMINAL")

# 1. DATA INPUT (The OpenBB Part)
with st.sidebar:
    ticker = st.text_input("SYMBOL", value="NVDA")
    provider = st.selectbox("DATA PROVIDER", ["yfinance", "fmp", "polygon"])
    fast_ma_val = st.slider("Fast MA", 5, 50, 20)
    slow_ma_val = st.slider("Slow MA", 20, 200, 50)

# Fetching data using the new OpenBB OBBject
@st.cache_data
def fetch_institutional_data(symbol, prov):
    # This replaces the old yfinance.download
    res = obb.equity.price.historical(symbol=symbol, provider=prov)
    df = res.to_dataframe()
    return df

try:
    data = fetch_institutional_data(ticker, provider)
    close_price = data['close']

    # 2. THE QUANT ENGINE (The VectorBT Part)
    # This runs the math on the entire price series at once (no loops)
    fast_ma = vbt.MA.run(close_price, fast_ma_val)
    slow_ma = vbt.MA.run(close_price, slow_ma_val)
    
    entries = fast_ma.ma_crossed_above(slow_ma)
    exits = fast_ma.ma_crossed_below(slow_ma)

    # Simulation with $10k, 0.1% fees (realistic)
    pf = vbt.Portfolio.from_signals(close_price, entries, exits, init_cash=10000, fees=0.001)

    # 3. DISPLAY THE DATA
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📊 Quant Stats")
        st.dataframe(pf.stats(), height=400)

    with col2:
        st.subheader("📈 Cumulative Returns")
        st.plotly_chart(pf.plot(), use_container_width=True)

    # 4. OPENBB FUNDAMENTALS (The "Cheat Code" Data)
    st.markdown("---")
    st.header("🔍 Institutional Insider Trading (via OpenBB)")
    insider = obb.equity.fundamental.insider_trading(symbol=ticker, provider="fmp").to_dataframe()
    st.table(insider.head(10))

except Exception as e:
    st.error(f"Waiting for command... Error: {e}")
