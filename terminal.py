import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime

# --- 1. PRO LED TICKER (Full Colorful Cycle) ---
st.set_page_config(layout="wide", page_title="TERMINAL_V14_PRO", initial_sidebar_state="collapsed")

# Expanded list for a "Full Cycle" look
tickers = ["NVDA", "BTC-USD", "AAPL", "ETH-USD", "TSLA", "AMZN", "MSFT", "META", "GOOGL", "SOL-USD", "SPY", "QQQ", "GLD", "USO", "EURUSD=X"]
ticker_html = "".join([f"<span style='color:{'#00ff41' if i%2==0 else '#ff4b4b'}; padding-right:70px;'>{t}: LIVE_FEED</span>" for i, t in enumerate(tickers)])

st.html(f"""
    <style>
    .stApp {{ background: #000000; color: #00ff41; font-family: 'Courier New', monospace; }}
    @keyframes marquee {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
    .led-ticker {{ background: #050505; border-bottom: 2px solid #333; padding: 15px; overflow: hidden; white-space: nowrap; width: 100%; font-weight: bold; font-size: 22px; color: #00ff41; }}
    .led-ticker div {{ display: inline-block; animation: marquee 45s linear infinite; }}
    .newspaper-container {{ border: 3px double #00ff41; padding: 40px; background: rgba(0, 255, 65, 0.02); line-height: 1.8; }}
    .headline {{ font-size: 42px; font-weight: 900; text-transform: uppercase; border-bottom: 2px solid #00ff41; margin-bottom: 20px; text-shadow: 2px 2px #000; }}
    </style>
    <div class="led-ticker"><div>{ticker_html} | {ticker_html}</div></div>
""")

# --- 2. DATA & STATE ENGINE ---
if 'active_layers' not in st.session_state: st.session_state.active_layers = ["EMA"]
if 'ticker' not in st.session_state: st.session_state.ticker = "NVDA"

@st.cache_data(ttl=3600)
def load_all_data(ticker):
    s = yf.Ticker(ticker)
    df = s.history(period="2y")
    df['EMA20'] = ta.ema(df['Close'], length=20)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    return df, s.info, s.quarterly_financials, s.options

try:
    df, info, financials, opt_dates = load_all_data(st.session_state.ticker)
    
    # --- 3. LAYOUT WINGS ---
    l, c, r = st.columns([1, 4.5, 1.2])

    with l:
        st.markdown("### // SYSTEM_HUD")
        st.metric("PRICE", f"${df['Close'].iloc[-1]:,.2f}")
        st.metric("RSI", f"{df['RSI'].iloc[-1]:.1f}")
        st.markdown("---")
        if st.button("TOGGLE EMA"): st.session_state.active_layers.append("EMA") if "EMA" not in st.session_state.active_layers else st.session_state.active_layers.remove("EMA")
        if st.button("TOGGLE RSI"): st.session_state.active_layers.append("RSI") if "RSI" not in st.session_state.active_layers else st.session_state.active_layers.remove("RSI")

    with r:
        st.markdown("### // PINE_COMPILER")
        st.text_area("PINE_CODE", height=200, placeholder="indicator('Greeks')...")
        st.button("SYNC_LOGIC")
        st.markdown("---")
        st.subheader("MACRO_CALENDAR")
        st.table(pd.DataFrame([{"Event": "CPI", "Impact": "🔴"}, {"Event": "FOMC", "Impact": "🟡"}]))

    with c:
        t_in = st.text_input("SET_TICKER", value=st.session_state.ticker).upper().strip()
        if t_in != st.session_state.ticker:
            st.session_state.ticker = t_in
            st.rerun()

        tabs = st.tabs(["📊 ANALYSIS", "📉 OPTIONS", "💰 FINANCIALS", "📰 THE_DAILY_GAZETTE"])

        with tabs[0]:
            rows = 2 if "RSI" in st.session_state.active_layers else 1
            fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3] if rows==2 else [1.0])
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']), row=1, col=1)
            if "EMA" in st.session_state.active_layers:
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name="EMA20", line=dict(color="#00ff41")))
            if "RSI" in st.session_state.active_layers:
                fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI", line=dict(color="#2962ff")), row=2, col=1)
            fig.update_layout(template="plotly_dark", height=700, paper_bgcolor='black', plot_bgcolor='black', xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with tabs[3]:
            # --- DYNAMIC NEWSPAPER LOGIC ---
            rsi_val = df['RSI'].iloc[-1]
            price_change = ((df['Close'].iloc[-1] / df['Close'].iloc[-2]) - 1) * 100
            
            # Mood Selector
            if rsi_val > 70:
                headline = f"BLOOD IN THE WATER: {st.session_state.ticker} PUSHED TO EXTREMES"
                story = f"The greed is palpable. {st.session_state.ticker} is screaming 'overbought' with an RSI of {rsi_val:.1f}. Smart money is exit-ramping while retail is holding the bag."
            elif rsi_val < 30:
                headline = f"CAPITULATION: {st.session_state.ticker} CRUSHED TO VALUE FLOOR"
                story = f"Panic has set in. {st.session_state.ticker} is being dumped into the abyss, but institutional buyers are spotting a generational entry here at the {rsi_val:.1f} level."
            else:
                headline = f"THE COIL: {st.session_state.ticker} CONSOLIDATING FOR A BREAKOUT"
                story = f"Market participants are in a stalemate. {st.session_state.ticker} is trading flatly, building up enough energy to blow the doors off the next session."

            st.markdown(f"""
                <div class='newspaper-container'>
                    <div class='headline'>{headline}</div>
                    <p style='font-size: 14px; color: #888;'>DATE: {datetime.now().strftime('%B %d, %Y')} | WRITTEN BY THE TERMINAL GHOST</p>
                    <p style='font-size: 20px;'><b>Analysis Report:</b> {story}</p>
                    <p>Technically, the price moved <b>{price_change:.2f}%</b> in the last 24 hours. Whether this is a trap or a trend remains to be seen, but the tape doesn't lie.</p>
                </div>
            """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"SYSTEM_HALTED: {e}")
