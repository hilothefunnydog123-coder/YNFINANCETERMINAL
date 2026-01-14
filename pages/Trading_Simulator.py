import streamlit as st
import pandas as pd
import yfinance as yf
import streamlit.components.v1 as components

# 1. INITIALIZE SETTINGS (Persists through session)
if 'preset_qty' not in st.session_state:
    st.session_state.preset_qty = 10  # Initial default
if 'balance' not in st.session_state:
    st.session_state.balance = 100000.0
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}

st.set_page_config(layout="wide", page_title="YN_EXECUTION_DESK")

# 2. VIBRANT CUSTOM CSS
st.markdown("""
<style>
    /* Make buttons huge and vibrant */
    div.stButton > button {
        width: 100%;
        height: 60px;
        font-size: 20px !important;
        font-weight: bold !important;
        border-radius: 12px !important;
    }
    /* Buy Button: Neon Green */
    .st-key-buy_btn button {
        background-color: #00ff41 !important;
        color: black !important;
        border: 2px solid #00ff41 !important;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.4);
    }
    /* Sell Button: Neon Red */
    .st-key-sell_btn button {
        background-color: #ff4b4b !important;
        color: white !important;
        border: 2px solid #ff4b4b !important;
        box-shadow: 0 0 15px rgba(255, 75, 75, 0.4);
    }
    .setting-box {
        background: rgba(255,255,255,0.05);
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #444;
    }
</style>
""", unsafe_allow_html=True)

# 3. GLOBAL PRESETS (Save once, use forever)
with st.sidebar:
    st.markdown("### ⚙️ EXECUTION_PRESETS")
    new_qty = st.number_input("Default Trade Quantity", min_value=1, value=st.session_state.preset_qty)
    if new_qty != st.session_state.preset_qty:
        st.session_state.preset_qty = new_qty
        st.success(f"Preset updated to {new_qty} shares!")

# 4. THE LARGE CHART (Full Width)
ticker = st.session_state.get('ticker', 'NVDA')
st.markdown(f"## 📈 {ticker} INTERACTIVE_CHART")

# TradingView Widget with autosize enabled
# 2. Set height variable for consistency
CHART_HEIGHT = 650 

# 3. The Fixed Widget Call
components.html(f"""
    <div class="tradingview-widget-container" style="height:{CHART_HEIGHT}px; width:100%;">
        <div id="tradingview_full"></div>
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({{
            "autosize": true,  /* Uses 100% of parent div height */
            "symbol": "{ticker}",
            "interval": "D",
            "timezone": "Etc/UTC",
            "theme": "dark",
            "style": "1",
            "locale": "en",
            "enable_publishing": false,
            "allow_symbol_change": true,
            "container_id": "tradingview_full"
        }});
        </script>
    </div>
""", height=CHART_HEIGHT + 10) # Streamlit height must be explicitly set

# 5. POPOUT EXECUTION PANEL
st.markdown("---")
col_info, col_buy, col_sell = st.columns([1, 1, 1])

try:
    price = yf.Ticker(ticker).fast_info['last_price']
except:
    price = 0.0

with col_info:
    st.markdown(f"**CURRENT_PRICE**")
    st.markdown(f"## ${price:.2f}")
    st.caption(f"Executing with preset: **{st.session_state.preset_qty} shares**")

with col_buy:
    if st.button(f"MARKET_BUY ({st.session_state.preset_qty})", key="buy_btn"):
        total = price * st.session_state.preset_qty
        if st.session_state.balance >= total:
            st.session_state.balance -= total
            # Update internal portfolio logic...
            st.balloons()
            st.toast("BUY_ORDER_FILLED")

with col_sell:
    if st.button(f"MARKET_SELL ({st.session_state.preset_qty})", key="sell_btn"):
        # Update internal portfolio logic...
        st.toast("SELL_ORDER_FILLED")
