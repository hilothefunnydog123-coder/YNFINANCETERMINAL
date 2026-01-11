import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime

# --- 1. GLOBAL UI & LED TICKER (Full Cycle) ---
st.set_page_config(layout="wide", page_title="TERMINAL_ULTRA_V12", initial_sidebar_state="collapsed")

# Pulling 30 tickers for a heavy, professional scroll
full_tickers = ["NVDA", "AAPL", "BTC-USD", "ETH-USD", "TSLA", "AMZN", "META", "GOOGL", "MSFT", "NFLX", "AMD", "PLTR", "SOL-USD", "SPY", "QQQ", "GLD", "USO", "EURUSD=X", "JPY=X", "GBPUSD=X"]
ticker_html = "".join([f"<span style='color:{'#00ff41' if i%2==0 else '#ff4b4b'}; padding-right:50px;'>{t}: LIVE_DATA</span>" for i, t in enumerate(full_tickers)])

st.html(f"""
    <style>
    .stApp {{ background: #000000; color: #00ff41; font-family: 'Courier New', monospace; }}
    @keyframes marquee {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
    .led-ticker {{ background: #050505; border-bottom: 2px solid #333; padding: 12px; overflow: hidden; white-space: nowrap; width: 100%; font-weight: bold; font-size: 20px; }}
    .led-ticker div {{ display: inline-block; animation: marquee 35s linear infinite; }}
    .newspaper-box {{ border: 2px solid #00ff41; padding: 30px; background: rgba(0, 255, 65, 0.03); line-height: 1.6; }}
    </style>
    <div class="led-ticker"><div>{ticker_html} | {ticker_html}</div></div>
""")

# --- 2. PERSISTENT STATE ---
if 'active_layers' not in st.session_state: st.session_state.active_layers = []
if 'ticker' not in st.session_state: st.session_state.ticker = "NVDA"

# --- 3. THE "DEEP DATA" ENGINE ---
@st.cache_data(ttl=3600)
def load_elite_data(ticker):
    s = yf.Ticker(ticker)
    df = s.history(period="2y")
    # Technicals
    df['EMA20'] = ta.ema(df['Close'], length=20)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    # Financials & Options
    return df, s.info, s.quarterly_financials, s.quarterly_balance_sheet, s.options

try:
    df, info, financials, balance, opt_dates = load_elite_data(st.session_state.ticker)

    # --- 4. 3-WING INTERFACE ---
    l, c, r = st.columns([1, 4.5, 1.2])

    with l:
        st.markdown("### // SYSTEM_HUD")
        st.metric("PRICE", f"${df['Close'].iloc[-1]:,.2f}")
        st.metric("RSI_14", f"{df['RSI'].iloc[-1]:.1f}")
        st.markdown("---")
        for layer in ["EMA_LAYER", "RSI_PANE", "VOLUME_PROFILE"]:
            if st.button(f"TOGGLE_{layer}"):
                st.session_state.active_layers.append(layer) if layer not in st.session_state.active_layers else st.session_state.active_layers.remove(layer)

    with r:
        st.markdown("### // PINE_HUB")
        pine_in = st.text_area("COMPILE_CODE", height=200, placeholder="//@version=5\nindicator('Algo')...")
        st.button("SYNC_LOGIC")
        st.markdown("---")
        st.subheader("MACRO_ALERTS")
        st.error("CPI: 🔴 HIGH IMPACT")
        st.warning("FOMC: 🟡 MED IMPACT")

    with c:
        t_in = st.text_input("SET_TICKER", value=st.session_state.ticker).upper().strip()
        if t_in != st.session_state.ticker:
            st.session_state.ticker = t_in
            st.rerun()

        tabs = st.tabs(["📊 ANALYSIS", "📉 OPTIONS_GREEKS", "💰 FINANCIALS_VIZ", "📰 DAILY_GAZETTE"])

        with tabs[0]:
            rows = 2 if "RSI_PANE" in st.session_state.active_layers else 1
            fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3] if rows==2 else [1.0])
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="PRC"), row=1, col=1)
            if "EMA_LAYER" in st.session_state.active_layers:
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name="EMA20", line=dict(color="#00ff41")), row=1, col=1)
            if "RSI_PANE" in st.session_state.active_layers:
                fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI", line=dict(color="#2962ff")), row=2, col=1)
            fig.update_layout(template="plotly_dark", height=700, paper_bgcolor='black', plot_bgcolor='black', xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with tabs[1]:
            st.subheader("// VOLATILITY_SKEW")
            # Fetch Call/Put Skew
            try:
                chain = yf.Ticker(st.session_state.ticker).option_chain(opt_dates[0])
                calls, puts = chain.calls, chain.puts
                skew_fig = go.Figure()
                skew_fig.add_trace(go.Scatter(x=calls['strike'], y=calls['impliedVolatility'], name="CALL_IV", line=dict(color="#00ff41")))
                skew_fig.add_trace(go.Scatter(x=puts['strike'], y=puts['impliedVolatility'], name="PUT_IV", line=dict(color="#ff4b4b")))
                skew_fig.update_layout(template="plotly_dark", title="Implied Volatility Curve")
                st.plotly_chart(skew_fig, use_container_width=True)
                st.dataframe(calls, height=400, use_container_width=True)
            except: st.error("DEEP_DATA_NOT_FOUND")

        with tabs[2]:
            st.subheader("// VISUALIZED_STATEMENTS")
            st.markdown("#### QUARTERLY_REVENUE_TREND")
            # Charting Revenue from Financials DataFrame
            rev_fig = go.Figure(data=[go.Bar(x=financials.columns, y=financials.loc['Total Revenue'], marker_color='#00ff41')])
            rev_fig.update_layout(template="plotly_dark", height=350)
            st.plotly_chart(rev_fig, use_container_width=True)
            st.dataframe(financials, use_container_width=True)

        with tabs[3]:
            # THE MAGICAL NEWSPAPER
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            st.markdown(f"<div class='newspaper-box'><h1>📰 THE {st.session_state.ticker} GAZETTE</h1>", unsafe_allow_html=True)
            st.markdown(f"**EDITION: {now}** | *Written by the Ghost of Wall Street*")
            st.write("---")
            # Logic-driven writing based on technicals
            tone = "EXTENDED" if df['RSI'].iloc[-1] > 70 else "COILED" if df['RSI'].iloc[-1] < 30 else "NEUTRAL"
            st.write(f"The tape doesn't lie. As of {now}, **{st.session_state.ticker}** is looking dangerously **{tone}**.")
            st.write(f"With a current price of ${df['Close'].iloc[-1]:,.2f}, institutional volume is signaling a massive liquidity sweep. Retailers are chasing the green candles while the smart money is stacking orders at the value area.")
            st.markdown("</div>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"SYSTEM_HALTED: {e}")
