import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_tradingview_chart import streamlit_tradingview_chart # Ensure pip install streamlit-tradingview-chart

# 1. INITIALIZE VIRTUAL LEDGER
if 'balance' not in st.session_state:
    st.session_state.balance = 100000.0  # Default starting amount
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}  # Format: {'TICKER': {'qty': 10, 'avg_price': 150.0}}
if 'trade_history' not in st.session_state:
    st.session_state.trade_history = []

st.set_page_config(layout="wide", page_title="YN_PAPER_TRADER")

# 2. CUSTOM THEME (Vibrant Terminal Style)
st.markdown("""
<style>
    .trade-card { background: #1e1e1e; padding: 20px; border-radius: 15px; border: 1px solid #333; }
    .stat-val { font-size: 24px; font-weight: bold; color: #00ff41; font-family: monospace; }
    .buy-btn { background-color: #00ff41 !important; color: black !important; font-weight: bold; }
    .sell-btn { background-color: #ff4b4b !important; color: white !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 3. SIDEBAR: SETUP & WALLET
with st.sidebar:
    st.header("⚙️ TRADING_SETUP")
    start_amt = st.number_input("Starting Capital", min_value=1000, value=100000, step=1000)
    if st.button("RESET_ACCOUNT"):
        st.session_state.balance = float(start_amt)
        st.session_state.portfolio = {}
        st.session_state.trade_history = []
        st.rerun()

    st.markdown("---")
    st.metric("CASH_BALANCE", f"${st.session_state.balance:,.2f}")

# 4. MAIN INTERFACE
ticker = st.session_state.get('ticker', 'NVDA')
c1, c2 = st.columns([2, 1])

with c1:
    st.markdown(f"### 📈 {ticker} LIVE_CHART")
    # Using the TradingView Advanced Real-Time Chart Widget
    streamlit_tradingview_chart(
        chart_type="candlestick",
        symbol=ticker,
        interval="D",
        theme="dark",
        save_image=False,
    )

with c2:
    st.markdown("### ⚡ EXECUTION_PANEL")
    stock_data = yf.Ticker(ticker).fast_info
    current_price = stock_data['last_price']
    
    st.markdown(f"<div class='trade-card'>Price: <span class='stat-val'>${current_price:.2f}</span></div>", unsafe_allow_html=True)
    
    qty = st.number_input("Quantity", min_value=1, value=1)
    total_cost = qty * current_price
    
    col_buy, col_sell = st.columns(2)
    
    # BUY LOGIC
    if col_buy.button("MARKET_BUY", use_container_width=True):
        if st.session_state.balance >= total_cost:
            st.session_state.balance -= total_cost
            # Update Portfolio
            if ticker in st.session_state.portfolio:
                prev_qty = st.session_state.portfolio[ticker]['qty']
                prev_avg = st.session_state.portfolio[ticker]['avg_price']
                new_qty = prev_qty + qty
                new_avg = ((prev_avg * prev_qty) + (current_price * qty)) / new_qty
                st.session_state.portfolio[ticker] = {'qty': new_qty, 'avg_price': new_avg}
            else:
                st.session_state.portfolio[ticker] = {'qty': qty, 'avg_price': current_price}
            
            st.toast(f"Bought {qty} {ticker} at ${current_price:.2f}")
        else:
            st.error("INSUFFICIENT_FUNDS")

    # SELL LOGIC
    if col_sell.button("MARKET_SELL", use_container_width=True):
        if ticker in st.session_state.portfolio and st.session_state.portfolio[ticker]['qty'] >= qty:
            st.session_state.balance += total_cost
            st.session_state.portfolio[ticker]['qty'] -= qty
            if st.session_state.portfolio[ticker]['qty'] == 0:
                del st.session_state.portfolio[ticker]
            st.toast(f"Sold {qty} {ticker} at ${current_price:.2f}")
        else:
            st.error("INSUFFICIENT_SHARES")

# 5. PORTFOLIO MONITOR
st.markdown("---")
st.markdown("### 💼 LIVE_POSITIONS")
if st.session_state.portfolio:
    p_data = []
    for t, pos in st.session_state.portfolio.items():
        curr_p = yf.Ticker(t).fast_info['last_price']
        pnl = (curr_p - pos['avg_price']) * pos['qty']
        p_data.append({
            "Ticker": t,
            "Qty": pos['qty'],
            "Avg Price": f"${pos['avg_price']:.2f}",
            "Current Price": f"${curr_p:.2f}",
            "P&L": f"${pnl:,.2f}",
            "Return %": f"{((curr_p/pos['avg_price'])-1)*100:.2f}%"
        })
    st.table(pd.DataFrame(p_data))
else:
    st.info("No active positions. Execute a trade to begin.")
