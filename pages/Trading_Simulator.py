import streamlit as st
import pandas as pd
import yfinance as yf
import streamlit.components.v1 as components

# 1. INITIALIZE VIRTUAL LEDGER (Session State)
if 'balance' not in st.session_state:
    st.session_state.balance = 100000.0
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {} 
if 'trade_history' not in st.session_state:
    st.session_state.trade_history = []

st.set_page_config(layout="wide", page_title="YN_PAPER_TRADER")

# 2. TRADINGVIEW WIDGET ENGINE (The "No-Module" Solution)
def render_tv_chart(symbol):
    render_code = f"""
    <div class="tradingview-widget-container" style="height:500px;width:100%;">
      <div id="tradingview_chart"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true,
        "symbol": "{symbol}",
        "interval": "D",
        "timezone": "Etc/UTC",
        "theme": "dark",
        "style": "1",
        "locale": "en",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "hide_side_toolbar": false,
        "allow_symbol_change": true,
        "container_id": "tradingview_chart"
      }});
      </script>
    </div>
    """
    components.html(render_code, height=500)

# 3. DASHBOARD UI
ticker = st.session_state.get('ticker', 'NVDA')
st.title(f"⚡ YN EXECUTION DESK: {ticker}")

col1, col2 = st.columns([2, 1])

with col1:
    render_tv_chart(ticker)

with col2:
    st.markdown("### // ORDER_EXECUTION")
    try:
        # Fetching price with a fallback for rate limits
        stock = yf.Ticker(ticker)
        current_price = stock.fast_info['last_price']
    except:
        current_price = 0.0
        st.error("PRICE_FEED_OFFLINE")

    st.metric("LIVE_PRICE", f"${current_price:.2f}")
    
    qty = st.number_input("Quantity", min_value=1, step=1)
    total_cost = qty * current_price
    
    c_buy, c_sell = st.columns(2)
    
    if c_buy.button("MARKET_BUY", use_container_width=True):
        if st.session_state.balance >= total_cost:
            st.session_state.balance -= total_cost
            # Logic for Average Cost Basis
            pos = st.session_state.portfolio.get(ticker, {'qty': 0, 'avg_price': 0.0})
            new_qty = pos['qty'] + qty
            new_avg = ((pos['avg_price'] * pos['qty']) + total_cost) / new_qty
            st.session_state.portfolio[ticker] = {'qty': new_qty, 'avg_price': new_avg}
            st.toast(f"FILLED: Bought {qty} {ticker}")
        else:
            st.error("INSUFFICIENT_FUNDS")

    if c_sell.button("MARKET_SELL", use_container_width=True):
        pos = st.session_state.portfolio.get(ticker, {'qty': 0})
        if pos['qty'] >= qty:
            st.session_state.balance += total_cost
            pos['qty'] -= qty
            if pos['qty'] == 0:
                del st.session_state.portfolio[ticker]
            st.toast(f"FILLED: Sold {qty} {ticker}")
        else:
            st.error("INSUFFICIENT_SHARES")

# 4. PORTFOLIO & LEADERBOARD
st.markdown("---")
st.subheader("💼 ACTIVE_POSITIONS")

if st.session_state.portfolio:
    p_list = []
    total_market_value = 0
    for t, data in st.session_state.portfolio.items():
        # Quick price check
        p = yf.Ticker(t).fast_info['last_price']
        mkt_val = p * data['qty']
        total_market_value += mkt_val
        pnl = (p - data['avg_price']) * data['qty']
        p_list.append({
            "Ticker": t, "Qty": data['qty'], 
            "Avg Cost": f"${data['avg_price']:.2f}", 
            "P&L": f"${pnl:.2f}",
            "Value": f"${mkt_val:.2f}"
        })
    st.table(pd.DataFrame(p_list))
    
    # Leaderboard Calculation
    total_equity = st.session_state.balance + total_market_value
    perf = ((total_equity / 100000.0) - 1) * 100
    st.metric("TOTAL_ACCOUNT_EQUITY", f"${total_equity:,.2f}", f"{perf:.2f}% vs S&P 500")
else:
    st.info("Portfolio empty. Use the Execution Panel to place trades.")
