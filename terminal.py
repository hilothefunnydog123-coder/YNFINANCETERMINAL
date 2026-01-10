import streamlit as st
import yfinance as yf
import pandas_ta as ta
import vectorbt as vbt
import plotly.graph_objects as go
import pandas as pd

# --- THE FIX: Disable VectorBT Widgets Globally ---
vbt.settings.plotting['use_widgets'] = False

# --- 1. THE TERMINAL SKIN ---
st.set_page_config(layout="wide", page_title="TERMINAL_v2.4_FINAL")

st.html("""
    <style>
    .stApp { background-color: #000000; color: #00ff41; font-family: 'Courier New', monospace; }
    [data-testid="stSidebar"] { background-color: #050505; border-right: 2px solid #00ff41; }
    [data-testid="stMetric"] { 
        border: 1px solid #00ff41; 
        background: rgba(0, 255, 65, 0.08); 
        padding: 15px; 
    }
    h1, h2, h3 { color: #00ff41 !important; text-transform: uppercase; letter-spacing: 1px; }
    .stDataFrame { border: 1px solid #00ff41; }
    </style>
    """)

st.title("📟 TERMINAL_OS // FINAL_STABLE_v2.4")

# --- 2. SIDEBAR COMMANDS ---
with st.sidebar:
    st.header("CMD_INPUT")
    ticker = st.text_input("SYMBOL", value="NVDA").upper().strip()
    st.markdown("---")
    fast_ma = st.slider("FAST_MA", 5, 50, 20)
    slow_ma = st.slider("SLOW_MA", 20, 200, 50)
    st.write("CORE: [LOCKED]")

# --- 3. DATA ENGINE ---
@st.cache_data
def load_market_data(symbol):
    # Using specific 2026 flags to bypass yfinance multi-index bugs
    df = yf.download(symbol, period="2y", auto_adjust=True, multi_level_index=False)
    if not df.empty and len(df) > 20:
        df['RSI'] = ta.rsi(df['Close'], length=14)
    return df

try:
    df = load_market_data(ticker)
    
    if df.empty:
        st.warning(f"// SYMBOL_NOT_FOUND: {ticker}")
    else:
        # HUD Data
        p_last = float(df['Close'].iloc[-1])
        r_last = float(df['RSI'].iloc[-1])
        p_high = float(df['High'].max())

        # 4. HUD DISPLAY
        c1, c2, c3 = st.columns(3)
        c1.metric("LATEST_PRC", f"${p_last:,.2f}")
        c2.metric("RSI_INDEX", f"{r_last:.2f}")
        c3.metric("2Y_PEAK", f"${p_high:,.2f}")

        # 5. MAIN CANDLESTICK CHART
        fig = go.Figure(data=[go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], 
            low=df['Low'], close=df['Close'], name="Price"
        )])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=450,
                          paper_bgcolor='black', plot_bgcolor='black')
        st.plotly_chart(fig, use_container_width=True)

        # 6. VECTORBT BACKTEST (Widget-Free Version)
        st.subheader("// STRATEGY_PERFORMANCE_LOG")
        
        close = df['Close']
        fast_ind = vbt.MA.run(close, fast_ma)
        slow_ind = vbt.MA.run(close, slow_ma)
        
        entries = fast_ind.ma_crossed_above(slow_ind)
        exits = fast_ind.ma_crossed_below(slow_ind)
        
        pf = vbt.Portfolio.from_signals(close, entries, exits, init_cash=10000)
        
        col_s, col_p = st.columns([1, 2])
        with col_s:
            st.write("STAT_ANALYSIS")
            st.dataframe(pf.stats().to_frame(name="VALUE"), height=400)
            
        with col_p:
            st.write("EQUITY_VISUAL")
            # Since use_widgets=False, this returns a standard Figure object
            pf_fig = pf.plot()
            pf_fig.update_layout(template="plotly_dark", paper_bgcolor='black', plot_bgcolor='black')
            st.plotly_chart(pf_fig, use_container_width=True)

except Exception as e:
    st.error(f"// SYSTEM_HALTED: {e}")
