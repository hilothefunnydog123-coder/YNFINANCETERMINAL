import streamlit as st
import yfinance as yf
import pandas_ta as ta
import vectorbt as vbt
import plotly.graph_objects as go
import pandas as pd

# --- 1. GLOBAL UI & LED TICKER ---
vbt.settings.plotting['use_widgets'] = False

ticker_data = [{"s": "NVDA", "p": "124.50", "c": "+2.4%", "clr": "#00ff41"}, {"s": "BTC-USD", "p": "64,210", "c": "+1.2%", "clr": "#00ff41"}]
ticker_string = "  |  ".join([f"<span style='color:{x['clr']}'>{x['s']}: {x['p']} ({x['c']})</span>" for x in ticker_data])

st.set_page_config(layout="wide", page_title="TERMINAL_v7.5_STABLE")
st.html(f"""
    <style>
    .stApp {{ background: #000000; color: #00ff41; font-family: 'Courier New', monospace; }}
    @keyframes marquee {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
    .led-ticker {{ background: #050505; border-bottom: 2px solid #333; padding: 10px; overflow: hidden; white-space: nowrap; width: 100%; font-weight: bold; font-size: 18px; }}
    .led-ticker div {{ display: inline-block; animation: marquee 30s linear infinite; }}
    .stButton>button {{ background: transparent; color: #00ff41; border: 1px solid #00ff41; font-size: 11px; width: 100%; height: 35px; }}
    .stButton>button:hover {{ background: #00ff41; color: black; box-shadow: 0 0 15px #00ff41; }}
    </style>
    <div class="led-ticker"><div>{ticker_string} | {ticker_string}</div></div>
""")

# --- 2. PERSISTENT SYSTEM STATE ---
if 'active_layers' not in st.session_state: st.session_state.active_layers = []
if 'ticker' not in st.session_state: st.session_state.ticker = "NVDA"

# --- 3. FIXED DATA ENGINE ---
@st.cache_data(ttl=60)
def load_quant_data(ticker):
    s = yf.Ticker(ticker)
    # Removed 'multi_level_index' to fix the crash
    df = s.history(period="2y", auto_adjust=True)
    
    # Pre-calculate Indicators
    df['EMA20'] = ta.ema(df['Close'], length=20)
    df['EMA50'] = ta.ema(df['Close'], length=50)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    return df, s.info, s.options

try:
    df, info, opt_dates = load_quant_data(st.session_state.ticker)

    # --- 4. THE 3-WING COMMAND CENTER ---
    left_ctrl, center_main, right_ctrl = st.columns([1, 4, 1.2])

    with left_ctrl:
        st.markdown("### // CHART_LAYERS")
        # Buttons now toggle layers in session_state
        if st.button("TOGGLE EMA_CROSS"):
            st.session_state.active_layers.append("EMA") if "EMA" not in st.session_state.active_layers else st.session_state.active_layers.remove("EMA")
        if st.button("TOGGLE RSI_BAND"):
            st.session_state.active_layers.append("RSI") if "RSI" not in st.session_state.active_layers else st.session_state.active_layers.remove("RSI")
        if st.button("CLEAR_ALL"): st.session_state.active_layers = []
        
        st.markdown("---")
        st.metric("LATEST_PRICE", f"${df['Close'].iloc[-1]:,.2f}")
        st.metric("VOLATILITY", f"{df['Close'].pct_change().std()*100:.2f}%")

    with right_ctrl:
        st.markdown("### // PINE_SCRIPT_HUB")
        pine_input = st.text_area("PASTE_CODE", height=250, placeholder="//@version=5\nindicator('EMA')...")
        
        if st.button("INTERPRET_LOGIC"):
            # Maps Pine keywords to chart layers
            if "ta.ema" in pine_input.lower(): st.session_state.active_layers.append("EMA")
            if "ta.rsi" in pine_input.lower(): st.session_state.active_layers.append("RSI")
            st.toast("Pine Logic Synced to Chart")

    with center_main:
        t_input = st.text_input("SET_ACTIVE_TICKER", value=st.session_state.ticker).upper()
        if t_input != st.session_state.ticker:
            st.session_state.ticker = t_input
            st.rerun()

        tab1, tab2, tab3 = st.tabs(["📊 LIVE_CHART", "📉 OPTIONS_CHAIN", "💰 FUNDAMENTALS"])
        
        with tab1:
            # Candlestick Base
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price")])
            
            # DYNAMIC OVERLAYS: Adding tracers based on button state
            if "EMA" in st.session_state.active_layers:
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name="EMA20", line=dict(color="#00ff41", width=1.5)))
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], name="EMA50", line=dict(color="#ff4b4b", width=1.5)))
            
            fig.update_layout(template="plotly_dark", height=600, paper_bgcolor='black', plot_bgcolor='black', xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
            st.write(f"SYSTEM_LAYERS_ACTIVE: {st.session_state.active_layers}")

        with tab2:
            st.subheader("// DEEP_OPTIONS_CHAIN")
            # Concat multiple dates for a massive scrollable view
            try:
                chains = [yf.Ticker(st.session_state.ticker).option_chain(d).calls for d in opt_dates[:5]]
                st.dataframe(pd.concat(chains), height=600, use_container_width=True)
            except: st.write("No Derivatives Found")

except Exception as e:
    st.error(f"SYSTEM_CRASH: {e}")
