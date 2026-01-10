import streamlit as st
import yfinance as yf
import pandas_ta as ta
import vectorbt as vbt
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. THE TERMINAL SKIN (2026 CSS Injection) ---
st.set_page_config(layout="wide", page_title="TERMINAL_v2.0_QUANT")

st.html("""
    <style>
    /* Global Matrix/Bloomberg Vibes */
    .stApp { background-color: #000000; color: #00ff41; }
    [data-testid="stSidebar"] { 
        background-color: #050505; 
        border-right: 2px solid #00ff41; 
    }
    /* Metric Card Glowing Effect */
    [data-testid="stMetric"] {
        border: 1px solid #00ff41;
        padding: 20px;
        border-radius: 5px;
        background: rgba(0, 255, 65, 0.05);
        box-shadow: 0 0 10px rgba(0, 255, 65, 0.2);
    }
    /* Typography */
    h1, h2, h3, p { font-family: 'Courier New', monospace !important; }
    .stButton>button {
        background-color: #00ff41 !important;
        color: black !important;
        font-weight: bold;
        border-radius: 0px;
        width: 100%;
    }
    </style>
    """)

# --- 2. THE COMMAND LINE (Sidebar) ---
with st.sidebar:
    st.title("📟 CMD_PROMPT")
    ticker = st.text_input("ENTER_SYMBOL", value="BTC-USD").upper()
    
    st.markdown("---")
    st.subheader("PARAM_STRATEGY")
    fast = st.slider("FAST_MA", 5, 50, 20)
    slow = st.slider("SLOW_MA", 20, 200, 50)
    
    st.markdown("---")
    st.write("SYSTEM_STATUS: [ONLINE]")

# --- 3. DATA ENGINE (The "Cheat Code" Speed) ---
@st.cache_data
def load_market_data(symbol):
    df = yf.download(symbol, period="5y", interval="1d")
    # Technical Overlay
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df['EMA_20'] = ta.ema(df['Close'], length=20)
    return df

try:
    data = load_market_data(ticker)
    
    # --- 4. TOP HUD (Metrics) ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("PRICE", f"${data['Close'].iloc[-1]:,.2f}")
    col2.metric("RSI", f"{data['RSI'].iloc[-1]:.1f}")
    col3.metric("52W_HIGH", f"${data['High'].max():,.2f}")
    col4.metric("VOL_CHG", f"{((data['Volume'].iloc[-1]/data['Volume'].mean())-1)*100:.1f}%")

    # --- 5. THE TERMINAL CHART ---
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="PRC"))
    fig.add_trace(go.Scatter(x=data.index, y=data['EMA_20'], line=dict(color='#00ff41', width=1.5), name="EMA20"))
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_rangeslider_visible=False,
        height=500,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- 6. VECTORBT BACKTEST (The "Insane" Part) ---
    st.markdown("### // STRATEGY_BACKTEST_REPORT")
    
    # Vectorized logic: Fast Crosses Slow
    fast_ma = vbt.MA.run(data['Close'], fast)
    slow_ma = vbt.MA.run(data['Close'], slow)
    entries = fast_ma.ma_crossed_above(slow_ma)
    exits = fast_ma.ma_crossed_below(slow_ma)
    
    pf = vbt.Portfolio.from_signals(data['Close'], entries, exits, init_cash=10000)

    # Show it
    c_bt1, c_bt2 = st.columns([1, 2])
    with c_bt1:
        st.write("STATISTICAL_LOG")
        st.dataframe(pf.stats().to_frame(), height=400)
    with c_bt2:
        st.write("EQUITY_CURVE_VISUAL")
        st.plotly_chart(pf.plot(), use_container_width=True)

except Exception as e:
    st.error(f"FATAL_ERROR: {e}")
