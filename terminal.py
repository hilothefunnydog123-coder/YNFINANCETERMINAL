import streamlit as st
import yfinance as yf
import pandas_ta as ta
import vectorbt as vbt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# --- GLOBAL QUANT SETTINGS ---
vbt.settings.plotting['use_widgets'] = False
vbt.settings.array_wrapper['freq'] = 'D'

st.set_page_config(layout="wide", page_title="PRO-QUANT TERMINAL v3.2")

# --- CUSTOM CSS: THE "MAGIC" SKIN ---
st.html("""
    <style>
    .stApp { background: #000000; color: #00ff41; font-family: 'Courier New', monospace; }
    [data-testid="stSidebar"] { background-color: #050505; border-right: 2px solid #00ff41; }
    [data-testid="stMetric"] { 
        border: 1px solid #00ff41; background: rgba(0, 255, 65, 0.05); 
        padding: 15px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,255,65,0.2);
    }
    h1, h2, h3 { color: #00ff41 !important; text-transform: uppercase; text-shadow: 0 0 5px #00ff41; }
    .stButton>button { 
        background: transparent; color: #00ff41; border: 1px solid #00ff41; width: 100%;
    }
    .stButton>button:hover { background: #00ff41; color: black; }
    </style>
""")

# --- SIDEBAR: STRATEGY ENGINE ---
with st.sidebar:
    st.title("📟 COMMAND_CENTER")
    ticker = st.text_input("SYMBOL", value="BTC-USD").upper().strip()
    
    st.markdown("---")
    strat_mode = st.selectbox("EXECUTION_MODE", 
                              ["EMA Crossover", "Fibonacci 61.8%", "Weak High/Low", "CUSTOM PINE BRIDGE"])
    
    if strat_mode == "CUSTOM PINE BRIDGE":
        pine_input = st.text_area("PASTE PINESCRIPT", height=200, placeholder="//@version=5...")
    
    run_btn = st.button("RUN_QUANT_PROTOCOL")

# --- DATA & LOGIC ---
@st.cache_data
def get_clean_data(symbol):
    df = yf.download(symbol, period="2y", auto_adjust=True, multi_level_index=False)
    if not df.empty:
        df['RSI'] = ta.rsi(df['Close'], length=14)
    return df

try:
    data = get_clean_data(ticker)
    if data.empty:
        st.error("SYMBOL_NOT_FOUND")
    else:
        # 1. STRATEGY CALCULATION
        close = data['Close']
        entries, exits = None, None

        if strat_mode == "EMA Crossover":
            f_ma = vbt.MA.run(close, 20)
            s_ma = vbt.MA.run(close, 50)
            entries = f_ma.ma_crossed_above(s_ma)
            exits = f_ma.ma_crossed_below(s_ma)

        elif strat_mode == "Fibonacci 61.8%":
            h, l = data['High'].rolling(100).max(), data['Low'].rolling(100).min()
            fib = h - ((h - l) * 0.618)
            entries = (close <= fib) & (close.shift(1) > fib)
            exits = (close >= h)

        elif strat_mode == "Weak High/Low":
            is_weak = (data['High'].diff().abs() < (data['High'] * 0.005))
            entries = is_weak.shift(1)
            exits = vbt.MA.run(close, 10).ma_crossed_below(vbt.MA.run(close, 30))

        # 2. HUD DATA
        c1, c2, c3 = st.columns(3)
        c1.metric("LATEST_PRICE", f"${float(close.iloc[-1]):,.2f}")
        c2.metric("2Y_VOLATILITY", f"{float(data['Close'].pct_change().std() * 100):.2f}%")
        c3.metric("RSI_14", f"{float(data['RSI'].iloc[-1]):.1f}")

        # 3. INSTITUTIONAL CHART
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.03, subplot_titles=('PRICE_ACTION', 'VOLUME'), 
                           row_width=[0.2, 0.7])

        fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], 
                                     low=data['Low'], close=data['Close'], name="PRC"), row=1, col=1)
        fig.add_trace(go.Bar(x=data.index, y=data['Volume'], name="VOL", marker_color='#00ff41'), row=2, col=1)

        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=600,
                          paper_bgcolor='black', plot_bgcolor='black', font_color='#00ff41')
        st.plotly_chart(fig, use_container_width=True)

        # 4. BACKTEST EXECUTION
        if run_btn and entries is not None:
            pf = vbt.Portfolio.from_signals(close, entries, exits, init_cash=10000, fees=0.001)
            
            st.subheader(f"// EXECUTION_REPORT: {strat_mode.upper()}")
            col_a, col_b = st.columns([1, 2])
            with col_a:
                st.dataframe(pf.stats().to_frame(name="VALUE"), height=400)
            with col_b:
                pf_fig = pf.plot()
                pf_fig.update_layout(template="plotly_dark", paper_bgcolor='black', plot_bgcolor='black')
                st.plotly_chart(pf_fig, use_container_width=True)

except Exception as e:
    st.error(f"SYSTEM_HALTED: {e}")
