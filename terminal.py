import streamlit as st
import yfinance as yf
import pandas_ta as ta
import vectorbt as vbt
import plotly.graph_objects as go
import pandas as pd

# --- 1. GLOBAL SETTINGS & LED TICKER ---
vbt.settings.plotting['use_widgets'] = False
vbt.settings.array_wrapper['freq'] = 'D'

ticker_data = [{"s": "NVDA", "p": "124.50", "c": "+2.4%", "clr": "#00ff41"}, {"s": "BTC-USD", "p": "64,210", "c": "+1.2%", "clr": "#00ff41"}, {"s": "TSLA", "p": "210.10", "c": "+5.1%", "clr": "#00ff41"}]
ticker_string = "  |  ".join([f"<span style='color:{x['clr']}'>{x['s']}: {x['p']} ({x['c']})</span>" for x in ticker_data])

st.set_page_config(layout="wide", page_title="PRO_QUANT_V7")
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

# --- 2. SESSION STATE (The "Memory" of the Terminal) ---
if 'active_indicators' not in st.session_state: st.session_state.active_indicators = []
if 'ticker' not in st.session_state: st.session_state.ticker = "BTC-USD"

# --- 3. DATA ENGINE ---
@st.cache_data(ttl=60)
def fetch_terminal_data(ticker):
    s = yf.Ticker(ticker)
    df = s.history(period="2y", auto_adjust=True, multi_level_index=False)
    # Pre-calculate common indicators
    df['EMA20'] = ta.ema(df['Close'], length=20)
    df['EMA50'] = ta.ema(df['Close'], length=50)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    return df, s.info, s.options

# --- 4. COMMAND CENTER LAYOUT ---
left_ctrl, center_main, right_ctrl = st.columns([1, 4, 1.2])

try:
    df, info, opt_dates = fetch_terminal_data(st.session_state.ticker)

    # LEFT WING: INDICATOR OVERLAYS
    with left_ctrl:
        st.markdown("### // CHART_LAYERS")
        if st.button("TOGGLE EMA_CROSS"): 
            st.session_state.active_indicators.append("EMA_CROSS") if "EMA_CROSS" not in st.session_state.active_indicators else st.session_state.active_indicators.remove("EMA_CROSS")
        if st.button("TOGGLE RSI_BAND"):
            st.session_state.active_indicators.append("RSI") if "RSI" not in st.session_state.active_indicators else st.session_state.active_indicators.remove("RSI")
        if st.button("RESET_ALL_LAYERS"): st.session_state.active_indicators = []
        
        st.markdown("---")
        st.metric("VOLATILITY", f"{df['Close'].pct_change().std()*100:.2f}%")
        st.metric("BETA", info.get('beta', 'N/A'))

    # RIGHT WING: PINE SCRIPT INTERPRETER
    with right_ctrl:
        st.markdown("### // PINE_STRAT_UPLOAD")
        pine_code = st.text_area("PASTE PINESCRIPT HERE", height=300, placeholder="//@version=5\nstrategy('My Script')\nif ta.crossover...")
        
        if st.button("EXECUTE_PINE_LOGIC"):
            # Simple keyword interpreter for indicators
            if "ta.ema" in pine_code.lower():
                st.session_state.active_indicators.append("PINE_EMA")
            if "ta.rsi" in pine_code.lower():
                st.session_state.active_indicators.append("RSI")
            st.success("Logic Interpreted. Overlaying data...")

    # CENTER MAIN: THE INTERACTIVE TERMINAL
    with center_main:
        t_input = st.text_input("SET_ACTIVE_TICKER", value=st.session_state.ticker).upper()
        if t_input != st.session_state.ticker:
            st.session_state.ticker = t_input
            st.rerun()

        tab1, tab2, tab3 = st.tabs(["📊 CHART & SIGNALS", "📉 OPTIONS_MATRIX", "💰 FUNDAMENTALS"])
        
        with tab1:
            st.subheader(f"TERMINAL_VIEW: {st.session_state.ticker} | ${df['Close'].iloc[-1]:,.2f}")
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price")])
            
            # FUNCTIONAL OVERLAYS: Adding data based on active buttons
            if "EMA_CROSS" in st.session_state.active_indicators:
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name="EMA20", line=dict(color="#00ff41", width=1)))
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], name="EMA50", line=dict(color="#ff4b4b", width=1)))
            
            if "PINE_EMA" in st.session_state.active_indicators:
                 fig.add_trace(go.Scatter(x=df.index, y=df['Close'].rolling(window=10).mean(), name="PINE_EMA_10", line=dict(color="#2962ff", dash='dot')))

            fig.update_layout(template="plotly_dark", height=600, paper_bgcolor='black', plot_bgcolor='black', xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
            st.write(f"ACTIVE_LAYERS: {st.session_state.active_indicators}")

        with tab2:
            # Massive scrollable options chain
            chains = [yf.Ticker(st.session_state.ticker).option_chain(d).calls for d in opt_dates[:5]]
            st.dataframe(pd.concat(chains), height=600, use_container_width=True)

except Exception as e:
    st.error(f"SYSTEM_HALTED: {e}")
