import streamlit as st
import yfinance as yf
import pandas_ta as ta
import vectorbt as vbt
import plotly.graph_objects as go
import pandas as pd

# --- 1. THE TERMINAL SKIN (2026 UI) ---
st.set_page_config(layout="wide", page_title="PRO-QUANT v2.3")

# Modern st.html for Matrix/Bloomberg styling
st.html("""
    <style>
    .stApp { background-color: #000000; color: #00ff41; font-family: 'Courier New', monospace; }
    [data-testid="stSidebar"] { background-color: #050505; border-right: 2px solid #00ff41; }
    [data-testid="stMetric"] { 
        border: 1px solid #00ff41; 
        background: rgba(0, 255, 65, 0.05); 
        padding: 15px; 
    }
    h1, h2, h3 { color: #00ff41 !important; text-transform: uppercase; letter-spacing: 2px; }
    .stDataFrame { border: 1px solid #00ff41; }
    </style>
    """)

st.title("📟 TERMINAL_OS // QUANT_SUITE_v2.3")

# --- 2. COMMAND CENTER ---
with st.sidebar:
    st.header("CMD_CORE")
    ticker = st.text_input("SYMBOL", value="NVDA").upper().strip()
    st.markdown("---")
    fast_ma = st.slider("FAST_MA", 5, 50, 20)
    slow_ma = st.slider("SLOW_MA", 20, 200, 50)
    st.write("STATUS: [SYSTEM_READY]")

# --- 3. DATA ENGINE (Fixed for 2025/2026 yfinance) ---
@st.cache_data
def load_market_data(symbol):
    # auto_adjust and multi_level_index=False prevent column indexing errors
    df = yf.download(symbol, period="2y", auto_adjust=True, multi_level_index=False)
    if not df.empty and len(df) > 20:
        df['RSI'] = ta.rsi(df['Close'], length=14)
    return df

try:
    data = load_market_data(ticker)
    
    if data.empty:
        st.warning(f"// NO_DATA_FOUND: {ticker}")
    else:
        # HUD Calculations
        curr_p = float(data['Close'].iloc[-1])
        curr_r = float(data['RSI'].iloc[-1])
        hi_52w = float(data['High'].max())

        # 4. TOP HUD
        c1, c2, c3 = st.columns(3)
        c1.metric("LATEST_PRC", f"${curr_p:,.2f}")
        c2.metric("RSI_LEVEL", f"{curr_r:.2f}")
        c3.metric("PEAK_VALUE", f"${hi_52w:,.2f}")

        # 5. MAIN TERMINAL CHART
        fig = go.Figure(data=[go.Candlestick(
            x=data.index, 
            open=data['Open'], high=data['High'], 
            low=data['Low'], close=data['Close']
        )])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=450,
                          paper_bgcolor='black', plot_bgcolor='black')
        st.plotly_chart(fig, use_container_width=True)

        # 6. VECTORBT BACKTEST (The 'anywidget' Bypass)
        st.subheader("// STRATEGY_BACKTEST_LOG")
        
        close_series = data['Close']
        fast_m = vbt.MA.run(close_series, fast_ma)
        slow_m = vbt.MA.run(close_series, slow_ma)
        
        entries = fast_m.ma_crossed_above(slow_m)
        exits = fast_m.ma_crossed_below(slow_m)
        
        pf = vbt.Portfolio.from_signals(close_series, entries, exits, init_cash=10000)

        c_stats, c_plot = st.columns([1, 2])
        with c_stats:
            # Force the stats to a standard dataframe for Streamlit
            st.dataframe(pf.stats().to_frame(name="VALUE"), height=400)
            
        with c_plot:
            # THE FIX: Access the underlying Plotly figure (.fig) directly
            vbt_fig = pf.plot().fig 
            vbt_fig.update_layout(template="plotly_dark", paper_bgcolor='black', plot_bgcolor='black')
            st.plotly_chart(vbt_fig, use_container_width=True)

except Exception as e:
    st.error(f"// SYSTEM_HALTED: {e}")
