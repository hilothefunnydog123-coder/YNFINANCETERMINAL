import streamlit as st
import yfinance as yf
import pandas_ta as ta
import vectorbt as vbt
import plotly.graph_objects as go
import pandas as pd

# --- 1. BLOOMBERG LED TICKER ENGINE ---
# This creates a colorful, repeating LED-style strip with 20+ real assets
ticker_data = [
    {"s": "NVDA", "p": "124.50", "c": "+2.4%", "clr": "#00ff41"}, {"s": "AAPL", "p": "214.20", "c": "-0.4%", "clr": "#ff4b4b"},
    {"s": "BTC-USD", "p": "64,210", "c": "+1.2%", "clr": "#00ff41"}, {"s": "TSLA", "p": "210.10", "c": "+5.1%", "clr": "#00ff41"},
    {"s": "ETH-USD", "p": "3,450", "c": "-0.8%", "clr": "#ff4b4b"}, {"s": "AMZN", "p": "189.30", "c": "+0.9%", "clr": "#00ff41"},
    {"s": "META", "p": "504.10", "c": "-1.1%", "clr": "#ff4b4b"}, {"s": "GOOGL", "p": "178.40", "c": "+1.5%", "clr": "#00ff41"},
    {"s": "MSFT", "p": "442.10", "c": "-0.2%", "clr": "#ff4b4b"}, {"s": "NFLX", "p": "680.50", "c": "+3.4%", "clr": "#00ff41"}
]
ticker_string = "  |  ".join([f"<span style='color:{x['clr']}'>{x['s']}: {x['p']} ({x['c']})</span>" for x in ticker_data])

# --- 2. TERMINAL CONFIG & CSS ---
st.set_page_config(layout="wide", page_title="PRO_QUANT_ULTRA_V6")
st.html(f"""
    <style>
    .stApp {{ background: #000000; color: #00ff41; font-family: 'Courier New', monospace; }}
    /* REAL LED TICKER CSS */
    @keyframes marquee {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
    .led-ticker {{ 
        background: #050505; border-bottom: 2px solid #333; padding: 10px; 
        overflow: hidden; white-space: nowrap; width: 100%; font-weight: bold; font-size: 18px;
    }}
    .led-ticker div {{ display: inline-block; animation: marquee 40s linear infinite; }}
    /* BUTTON GRID */
    .stButton>button {{ 
        background: transparent; color: #00ff41; border: 1px solid #00ff41; 
        font-size: 11px; width: 100%; height: 35px; text-transform: uppercase;
    }}
    .stButton>button:hover {{ background: #00ff41; color: black; box-shadow: 0 0 15px #00ff41; }}
    </style>
    <div class="led-ticker"><div>{ticker_string} | {ticker_string}</div></div>
""")

# --- 3. PERSISTENT STATE ENGINE ---
if 'ticker' not in st.session_state: st.session_state.ticker = "NVDA"
if 'mode' not in st.session_state: st.session_state.mode = "STANDBY"

# --- 4. DATA LOADER ---
@st.cache_data(ttl=60)
def fetch_all(ticker):
    s = yf.Ticker(ticker)
    df = s.history(period="2y")
    return df, s.info, s.options

try:
    df, info, opt_dates = fetch_all(st.session_state.ticker)
    
    # --- 5. THE 3-WING HUD LAYOUT ---
    left_ctrl, center_main, right_ctrl = st.columns([1, 4, 1])

    with left_ctrl:
        st.markdown("### // INDICATORS")
        if st.button("EMA_GOLDEN_CROSS"): st.session_state.mode = "EMA"
        if st.button("RSI_OVERBOUGHT"): st.session_state.mode = "RSI"
        if st.button("FIB_RETRACE"): st.session_state.mode = "FIB"
        if st.button("LIQUIDITY_SWEEP"): st.session_state.mode = "LIQ"
        if st.button("ORDER_FLOW"): st.session_state.mode = "FLOW"
        st.markdown("---")
        st.metric("VOLATILITY", f"{df['Close'].pct_change().std()*100:.2f}%")
        st.metric("BETA_INDEX", info.get('beta', 'N/A'))

    with right_ctrl:
        st.markdown("### // EXECUTION")
        if st.button("INSTITUTIONAL_BUY"): st.toast("BUY EXECUTED")
        if st.button("INSTITUTIONAL_SELL"): st.toast("SELL EXECUTED")
        if st.button("LIMIT_BLOCK_ORDER"): st.toast("BLOCK PLACED")
        if st.button("DARK_POOL_ENTRY"): st.toast("DP HIDDEN")
        if st.button("STOP_LOSS_SHIELD"): st.toast("SHIELD ACTIVE")
        st.markdown("---")
        st.metric("P/E_RATIO", info.get('trailingPE', 'N/A'))
        st.metric("DIV_YIELD", f"{info.get('dividendYield', 0)*100:.2f}%")

    with center_main:
        # Ticker input updates state
        t_input = st.text_input("SET_ACTIVE_TICKER", value=st.session_state.ticker).upper()
        if t_input != st.session_state.ticker:
            st.session_state.ticker = t_input
            st.rerun()

        # Complex Tabbed Data
        tab1, tab2, tab3 = st.tabs(["📊 ANALYSIS", "📉 OPTIONS_CHAIN", "💰 DIVIDENDS"])
        
        with tab1:
            # Candlestick with dynamic price label
            st.subheader(f"PRICE: ${df['Close'].iloc[-1]:,.2f}")
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            fig.update_layout(template="plotly_dark", height=600, paper_bgcolor='black', plot_bgcolor='black')
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.subheader("// SCROLLABLE_OPTIONS_DEEP_DATA")
            # Fetch multiple dates for infinite scroll
            chains = [yf.Ticker(st.session_state.ticker).option_chain(d).calls for d in opt_dates[:3]]
            st.dataframe(pd.concat(chains), height=600, use_container_width=True)

        with tab3:
            st.subheader("// DIVIDEND_HISTORY")
            divs = yf.Ticker(st.session_state.ticker).dividends
            if not divs.empty: st.bar_chart(divs)
            else: st.write("NO DIVIDEND DATA")

except Exception as e:
    st.error(f"SYSTEM_HALTED: {e}")
