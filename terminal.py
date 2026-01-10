import streamlit as st
import yfinance as yf
import pandas_ta as ta
import vectorbt as vbt
import plotly.graph_objects as go
import pandas as pd
import time

# --- SYSTEM CONFIG ---
vbt.settings.plotting['use_widgets'] = False

st.set_page_config(layout="wide", page_title="PRO-QUANT TERMINAL v3.0", page_icon="📟")

# --- MAGICAL CSS INJECTION ---
st.html("""
    <style>
    /* Dark Terminal Theme */
    .stApp {
        background: radial-gradient(circle, #0a0a0a 0%, #000000 100%);
        color: #00ff41;
        font-family: 'Courier New', monospace;
    }
    /* Glowing Sidebar */
    [data-testid="stSidebar"] {
        background-color: rgba(5, 5, 5, 0.9);
        border-right: 2px solid #00ff41;
        box-shadow: 5px 0px 15px rgba(0, 255, 65, 0.1);
    }
    /* Glassmorphism Metric Cards */
    [data-testid="stMetric"] {
        background: rgba(0, 255, 65, 0.03);
        border: 1px solid #00ff41;
        border-radius: 10px;
        padding: 20px;
        backdrop-filter: blur(5px);
    }
    /* Terminal Header */
    .terminal-header {
        border-bottom: 2px solid #00ff41;
        padding-bottom: 10px;
        margin-bottom: 20px;
        text-shadow: 0 0 10px #00ff41;
    }
    /* Custom Button */
    .stButton>button {
        background: transparent !important;
        color: #00ff41 !important;
        border: 2px solid #00ff41 !important;
        font-weight: bold;
        transition: 0.3s;
        width: 100%;
    }
    .stButton>button:hover {
        background: #00ff41 !important;
        color: black !important;
        box-shadow: 0 0 20px #00ff41;
    }
    </style>
    """)

# --- SIDEBAR: COMMAND CENTER ---
with st.sidebar:
    st.markdown("<h1 style='font-size: 20px;'>📟 SYSTEM_COMMAND</h1>", unsafe_allow_html=True)
    ticker = st.text_input("SET_SYMBOL", value="BTC-USD").upper().strip()
    
    st.markdown("---")
    strat_choice = st.radio("SELECT_STRATEGY", 
                            ["EMA CROSSOVER", "FIBONACCI 61.8%", "WEAK HIGH/LOW", "CUSTOM PINESCRIPT"])
    
    st.markdown("---")
    if strat_choice == "CUSTOM PINESCRIPT":
        pine_code = st.text_area("PASTE_CODE", height=150, placeholder="//@version=5\nstrategy('My Script')\nif ta.crossover...")
    
    lookback = st.selectbox("LOOKBACK_PERIOD", ["1Y", "2Y", "5Y"], index=0)
    run_exec = st.button("EXECUTE_QUANT_PROTOCOL")

# --- DATA ENGINE ---
@st.cache_data
def load_market_data(symbol, period):
    df = yf.download(symbol, period=period.lower(), auto_adjust=True, multi_level_index=False)
    if not df.empty:
        df['RSI'] = ta.rsi(df['Close'], length=14)
    return df

# --- MAIN TERMINAL INTERFACE ---
st.markdown("<div class='terminal-header'><h1>QUANT_TERMINAL // STRATEGY_HUB v3.0</h1></div>", unsafe_allow_html=True)

if not run_exec:
    # STANDBY SCREEN
    st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJqZ3R6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZ")
    st.markdown("### [ SYSTEM_READY ]: WAITING FOR COMMAND...")
    st.info("Select a strategy in the sidebar and click EXECUTE to start the backtest engine.")

else:
    # EXECUTION PHASE
    try:
        data = load_market_data(ticker, lookback)
        
        if data.empty:
            st.error(f"// ACCESS_DENIED: DATA NOT FOUND FOR {ticker}")
        else:
            with st.status("🛠️ PROCESSING DATA ARRAYS...", expanded=True) as status:
                st.write("Fetching institutional price data...")
                close = data['Close']
                
                st.write(f"Applying strategy: {strat_choice}...")
                entries, exits = None, None

                # Strategy 1: EMA
                if strat_choice == "EMA CROSSOVER":
                    fast = vbt.MA.run(close, 20)
                    slow = vbt.MA.run(close, 50)
                    entries = fast.ma_crossed_above(slow)
                    exits = fast.ma_crossed_below(slow)

                # Strategy 2: Fib Retracement
                elif strat_choice == "FIBONACCI 61.8%":
                    high_roll = data['High'].rolling(100).max()
                    low_roll = data['Low'].rolling(100).min()
                    fib_level = high_roll - ((high_roll - low_roll) * 0.618)
                    entries = (close <= fib_level) & (close.shift(1) > fib_level)
                    exits = close >= high_roll

                # Strategy 3: Weak High/Low (Market Structure)
                elif strat_choice == "WEAK HIGH/LOW":
                    # Identifies almost identical highs within 0.5% tolerance
                    is_weak_high = (data['High'].diff().abs() < (data['High'] * 0.005))
                    entries = is_weak_high.shift(1)
                    exits = vbt.MA.run(close, 10).ma_crossed_below(vbt.MA.run(close, 30))

                # Strategy 4: PineScript Interpreter
                elif strat_choice == "CUSTOM PINESCRIPT":
                    if "ta.crossover" in pine_code.lower():
                        fast = vbt.MA.run(close, 10)
                        slow = vbt.MA.run(close, 30)
                        entries = fast.ma_crossed_above(slow)
                        exits = fast.ma_crossed_below(slow)
                    else:
                        st.error("INTERPRETER ERROR: UNSUPPORTED PINE LOGIC.")

                st.write("Calculating Portfolio Vectorization...")
                pf = vbt.Portfolio.from_signals(close, entries, exits, init_cash=10000, fees=0.001)
                status.update(label="✅ EXECUTION SUCCESS", state="complete")

            # --- DISPLAY HUD ---
            c1, c2, c3 = st.columns(3)
            c1.metric("LATEST_PRICE", f"${float(close.iloc[-1]):,.2f}")
            c2.metric("SHARPE_RATIO", f"{float(pf.sharpe_ratio()):.2f}")
            c3.metric("WIN_RATE", f"{float(pf.trades.win_rate())*100:.1f}%")

            # --- PLOTTING ---
            st.markdown("---")
            st.subheader(f"// PERFORMANCE_LOG: {ticker}")
            
            # Magical Equity Curve
            vbt_fig = pf.plot()
            vbt_fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', 
                                  plot_bgcolor='rgba(0,0,0,0)', font_color='#00ff41')
            st.plotly_chart(vbt_fig, use_container_width=True)

            # Trade Stats Table
            st.markdown("### // STATISTICAL_BREAKDOWN")
            st.dataframe(pf.stats().to_frame(name="VALUE").style.highlight_max(axis=0, color='#111'))

    except Exception as e:
        st.error(f"// SYSTEM_HALTED: {e}")
