import streamlit as st
import yfinance as yf
import pandas_ta as ta
import vectorbt as vbt
import plotly.graph_objects as go
import pandas as pd

# 1. THE TERMINAL SKIN
st.set_page_config(layout="wide", page_title="TERMINAL_v2.2_STABLE")

st.html("""
    <style>
    .stApp { background-color: #000000; color: #00ff41; font-family: 'Courier New', monospace; }
    [data-testid="stSidebar"] { background-color: #050505; border-right: 2px solid #00ff41; }
    [data-testid="stMetric"] { border: 1px solid #00ff41; padding: 15px; background: rgba(0, 255, 65, 0.05); }
    h1, h2, h3 { color: #00ff41 !important; text-transform: uppercase; }
    </style>
    """)

st.title("📟 QUANT_OS // STABLE_v2.2")

# 2. SIDEBAR COMMANDS
with st.sidebar:
    st.header("CMD_INPUT")
    ticker = st.text_input("SYMBOL", value="NVDA").upper().strip()
    st.markdown("---")
    fast_ma = st.slider("FAST_MA", 5, 50, 20)
    slow_ma = st.slider("SLOW_MA", 20, 200, 50)

# 3. CRASH-PROOF DATA ENGINE
@st.cache_data
def load_data(symbol):
    # 'auto_adjust=True' and 'multi_level_index=False' fixes the 2025 formatting bugs
    df = yf.download(symbol, period="2y", auto_adjust=True, multi_level_index=False)
    if not df.empty and len(df) > 20:
        df['RSI'] = ta.rsi(df['Close'], length=14)
    return df

try:
    df = load_data(ticker)
    
    # SAFETY CHECK: If yfinance returns nothing, stop here gracefully
    if df.empty:
        st.warning(f"⚠️ NO DATA FOUND FOR '{ticker}'. CHECK SYMBOL OR CONNECTION.")
    else:
        # Get single values safely
        current_price = float(df['Close'].iloc[-1])
        current_rsi = float(df['RSI'].iloc[-1]) if 'RSI' in df.columns else 0.0
        year_high = float(df['High'].max())

        # 4. HUD DISPLAY
        c1, c2, c3 = st.columns(3)
        c1.metric("LATEST_PRICE", f"${current_price:,.2f}")
        c2.metric("RSI_14", f"{current_rsi:.2f}")
        c3.metric("2Y_HIGH", f"${year_high:,.2f}")

        # 5. THE CHART
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=500, paper_bgcolor='black', plot_bgcolor='black')
        st.plotly_chart(fig, use_container_width=True)

        # 6. VECTORBT BACKTEST
        st.subheader("// STRATEGY_BACKTEST")
        close = df['Close']
        fast_m = vbt.MA.run(close, fast_ma)
        slow_m = vbt.MA.run(close, slow_ma)
        entries = fast_m.ma_crossed_above(slow_m)
        exits = fast_m.ma_crossed_below(slow_m)
        
        pf = vbt.Portfolio.from_signals(close, entries, exits, init_cash=10000)
        
        col_stats, col_plot = st.columns([1, 2])
        with col_stats:
            st.dataframe(pf.stats().to_frame(name="VALUE"), height=400)
        with col_plot:
            st.plotly_chart(pf.plot(), use_container_width=True)

except Exception as e:
    st.error(f"SYSTEM_HALTED: {e}")
    st.info("Try checking your Internet or using a common ticker like 'AAPL'.")
