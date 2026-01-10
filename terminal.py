import streamlit as st
import yfinance as yf
import pandas_ta as ta
import vectorbt as vbt
import plotly.graph_objects as go
import numpy as np

# --- GLOBAL SETTINGS ---
vbt.settings.plotting['use_widgets'] = False

st.set_page_config(layout="wide", page_title="PRO-QUANT TERMINAL v3.0")
st.html("<style>.stApp { background-color: #000000; color: #00ff41; font-family: 'Courier New'; }</style>")

# --- COMMAND CENTER ---
with st.sidebar:
    st.title("📟 STRATEGY_HUB")
    ticker = st.text_input("SYMBOL", value="BTC-USD").upper()
    
    st.markdown("---")
    strat_choice = st.radio("SELECT STRATEGY", 
                            ["EMA Crossover", "Fibonacci 61.8%", "Weak High/Low", "CUSTOM PINESCRIPT"])
    
    st.markdown("---")
    if strat_choice == "CUSTOM PINESCRIPT":
        pine_code = st.text_area("PASTE PINESCRIPT HERE", height=200, placeholder="//@version=5\nstrategy('My Script')\nif ta.crossover(close, ema)...")
        st.warning("Note: Logic is mapped via Python-Interpreter.")
    
    run_exec = st.button("RUN BACKTEST")

# --- DATA ENGINE ---
@st.cache_data
def get_institutional_data(symbol):
    df = yf.download(symbol, period="2y", auto_adjust=True, multi_level_index=False)
    return df

try:
    df = get_institutional_data(ticker)
    close = df['Close']
    
    # --- STRATEGY LOGIC ---
    entries, exits = None, None

    if strat_choice == "EMA Crossover":
        fast = vbt.MA.run(close, 20)
        slow = vbt.MA.run(close, 50)
        entries = fast.ma_crossed_above(slow)
        exits = fast.ma_crossed_below(slow)

    elif strat_choice == "Fibonacci 61.8%":
        # Calculate Swing High/Low over 100 periods
        high_roll = df['High'].rolling(100).max()
        low_roll = df['Low'].rolling(100).min()
        fib_618 = high_roll - ((high_roll - low_roll) * 0.618)
        # Entry when price dips to 61.8% level
        entries = (close <= fib_618) & (close.shift(1) > fib_618)
        exits = close >= high_roll # Exit at the previous peak

    elif strat_choice == "Weak High/Low":
        # Identify "Equal Highs" (Weak Highs) within a 1% tolerance
        is_weak_high = (df['High'].diff().abs() < (df['High'] * 0.01))
        entries = is_weak_high.shift(1) # Trade the sweep
        exits = vbt.MA.run(close, 10).ma_crossed_below(vbt.MA.run(close, 30))

    elif strat_choice == "CUSTOM PINESCRIPT":
        # Simple Logic Mapper for Pine Script keywords
        if "ta.crossover" in pine_code:
            fast = vbt.MA.run(close, 10)
            slow = vbt.MA.run(close, 30)
            entries = fast.ma_crossed_above(slow)
            exits = fast.ma_crossed_below(slow)
        else:
            st.error("Interpreter Error: Basic logic not found. Try using 'ta.crossover'.")

    # --- EXECUTION & DISPLAY ---
    if run_exec and entries is not None:
        pf = vbt.Portfolio.from_signals(close, entries, exits, init_cash=10000, fees=0.001)
        
        st.header(f"// {strat_choice.upper()} REPORT")
        c1, c2 = st.columns([1, 2])
        with c1:
            st.dataframe(pf.stats().to_frame(name="VALUE"), height=500)
        with c2:
            st.plotly_chart(pf.plot(), use_container_width=True)

except Exception as e:
    st.error(f"SYSTEM_HALTED: {e}")
