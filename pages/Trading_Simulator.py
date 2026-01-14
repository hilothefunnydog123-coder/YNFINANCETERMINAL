import streamlit as st
import pandas as pd
import yfinance as yf
import streamlit.components.v1 as components
import json
from datetime import datetime

# 1. INITIALIZE SESSION STATE (Persistent User Data)
if 'balance' not in st.session_state:
    st.session_state.balance = 100000.0  # Customizable start
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}  # {ticker: {qty, avg_price}}
if 'markers' not in st.session_state:
    st.session_state.markers = []  # Chart arrows
if 'trade_log' not in st.session_state:
    st.session_state.trade_log = []

# 2. APP CONFIGURATION
st.set_page_config(layout="wide", page_title="YN_TRADING_SIM")
ticker = st.session_state.get('ticker', 'NVDA')

# CUSTOM CSS FOR VIBRANT BOLD UI
st.markdown("""
<style>
    .stMetric { background: rgba(255,255,255,0.05); padding: 15px; border-radius: 15px; }
    div.stButton > button { width: 100%; height: 3em; font-size: 20px; font-weight: bold; }
    .buy-btn button { background-color: #0088ff !important; color: white !important; }
    .sell-btn button { background-color: #ff4b4b !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# 3. SIDEBAR: CUSTOM SETTINGS
with st.sidebar:
    st.header("⚙️ SETTINGS")
    # Custom starting balance
    cust_bal = st.number_input("Starting Capital ($)", min_value=1.0, value=st.session_state.balance)
    if st.button("RESET ACCOUNT"):
        st.session_state.balance = cust_bal
        st.session_state.portfolio = {}
        st.session_state.markers = []
        st.rerun()
    
    # Persistent Trade Quantity
    st.session_state.preset_qty = st.number_input("Custom Order Qty", min_value=1, value=10)
    st.markdown("---")
    st.metric("CASH ON HAND", f"${st.session_state.balance:,.2f}")

# 4. LARGE INTERACTIVE CHART WITH ARROWS
st.title(f"⚡ EXECUTION DESK: {ticker}")

# Convert session markers to JS-readable JSON
marker_json = json.dumps(st.session_state.markers)
CHART_HEIGHT = 650

components.html(f"""
    <div id="tv_chart" style="height:{CHART_HEIGHT}px;"></div>
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <script type="text/javascript">
    new TradingView.widget({{
        "autosize": true,
        "symbol": "{ticker}",
        "interval": "D",
        "theme": "dark",
        "style": "1",
        "container_id": "tv_chart",
        "onChartReady": function() {{
            var markers = {marker_json};
            // Note: In some versions of the widget, markers are added via the API
            // This simulation expects the Lightweight Charts logic
        }}
    }});
    </script>
""", height=CHART_HEIGHT)

# 5. EXECUTION & P&L TRACKING
col_info, col_buy, col_sell = st.columns([1, 1, 1])

try:
    # Use fast_info to avoid rate limits
    curr_price = yf.Ticker(ticker).fast_info['last_price']
except:
    curr_price = 0.0

with col_info:
    st.metric("MARKET PRICE", f"${curr_price:.2f}")

# BUY LOGIC
with col_buy:
    st.markdown('<div class="buy-btn">', unsafe_allow_html=True)
    if st.button(f"BUY {st.session_state.preset_qty} {ticker}"):
        cost = curr_price * st.session_state.preset_qty
        if st.session_state.balance >= cost:
            st.session_state.balance -= cost
            # Update Portfolio
            pos = st.session_state.portfolio.get(ticker, {'qty': 0, 'avg_price': 0})
            new_qty = pos['qty'] + st.session_state.preset_qty
            new_avg = ((pos['avg_price'] * pos['qty']) + cost) / new_qty
            st.session_state.portfolio[ticker] = {'qty': new_qty, 'avg_price': new_avg}
            
            # Add Blue Arrow Marker
            st.session_state.markers.append({
                "time": datetime.now().strftime('%Y-%m-%d'),
                "position": "belowBar", "color": "#0088ff", "shape": "arrowUp", "text": "BUY"
            })
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# SELL LOGIC
with col_sell:
    st.markdown('<div class="sell-btn">', unsafe_allow_html=True)
    if st.button(f"SELL {st.session_state.preset_qty} {ticker}"):
        pos = st.session_state.portfolio.get(ticker, {'qty': 0})
        if pos['qty'] >= st.session_state.preset_qty:
            st.session_state.balance += (curr_price * st.session_state.preset_qty)
            st.session_state.portfolio[ticker]['qty'] -= st.session_state.preset_qty
            
            # Add Red Arrow Marker
            st.session_state.markers.append({
                "time": datetime.now().strftime('%Y-%m-%d'),
                "position": "aboveBar", "color": "#ff4b4b", "shape": "arrowDown", "text": "SELL"
            })
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# 6. P&L PERFORMANCE DASHBOARD
st.markdown("---")
st.subheader("💼 PERFORMANCE_AUDIT")

if st.session_state.portfolio:
    total_unrealized = 0
    p_data = []
    for t, d in st.session_state.portfolio.items():
        if d['qty'] > 0:
            c_p = yf.Ticker(t).fast_info['last_price']
            pnl = (c_p - d['avg_price']) * d['qty']
            total_unrealized += pnl
            p_data.append({
                "Ticker": t, "Qty": d['qty'], "Avg Cost": f"${d['avg_price']:.2f}",
                "Market Value": f"${(c_p * d['qty']):,.2f}", "P&L": f"${pnl:,.2f}"
            })
    
    st.table(pd.DataFrame(p_data))
    st.metric("TOTAL UNREALIZED P&L", f"${total_unrealized:,.2f}", delta=f"{total_unrealized:,.2f}")
else:
    st.info("No open positions. Use the Execution Desk to begin.")
