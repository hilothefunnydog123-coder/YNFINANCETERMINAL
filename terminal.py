import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime
import time

# --- 1. GLOBAL UI & REAL-TIME CLOCK ---
st.set_page_config(layout="wide", page_title="TERMINAL_ULTRA_V11")
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

st.markdown(f"""
    <style>
    .stApp {{ background: #000000; color: #00ff41; font-family: 'Courier New', monospace; }}
    @keyframes marquee {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
    .led-ticker {{ background: #050505; border-bottom: 2px solid #333; padding: 10px; overflow: hidden; white-space: nowrap; width: 100%; font-weight: bold; font-size: 18px; }}
    .led-ticker div {{ display: inline-block; animation: marquee 30s linear infinite; }}
    .newspaper-box {{ border: 2px solid #00ff41; padding: 20px; background: rgba(0, 255, 65, 0.05); margin-top: 20px; }}
    .news-headline {{ font-size: 24px; text-shadow: 0 0 10px #00ff41; text-transform: uppercase; }}
    </style>
    <div class="led-ticker"><div>NVDA: $124 (+2%) | BTC: $64K (+1%) | TSLA: $210 (+5%) | TIME: {now} | NVDA: $124 (+2%) | BTC: $64K (+1%)</div></div>
""", unsafe_allow_html=True)

# --- 2. PERSISTENT STATE ENGINE (The Secret to Layering) ---
# We use st.session_state to make sure buttons "remember" what they did
if 'indicators' not in st.session_state: st.session_state.indicators = []
if 'ticker' not in st.session_state: st.session_state.ticker = "NVDA"

# --- 3. DATA ENGINE ---
@st.cache_data(ttl=60)
def load_deep_data(ticker):
    s = yf.Ticker(ticker)
    df = s.history(period="2y", auto_adjust=True)
    df['EMA20'] = ta.ema(df['Close'], length=20)
    df['EMA50'] = ta.ema(df['Close'], length=50)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    return df, s.info, s.quarterly_financials

try:
    df, info, financials = load_deep_data(st.session_state.ticker)

    # --- 4. COMMAND CENTER LAYOUT ---
    l, c, r = st.columns([1, 4, 1.2])

    with l:
        st.markdown("### // CHART_LAYERS")
        # These buttons now TOGGLE items in a list
        if st.button("TOGGLE_EMA_CROSS"):
            st.session_state.indicators.append("EMA") if "EMA" not in st.session_state.indicators else st.session_state.indicators.remove("EMA")
        if st.button("TOGGLE_RSI_PANE"):
            st.session_state.indicators.append("RSI") if "RSI" not in st.session_state.indicators else st.session_state.indicators.remove("RSI")
        if st.button("CLEAR_LAYERS"): st.session_state.indicators = []
        
        st.markdown("---")
        st.metric("LATEST_PRICE", f"${df['Close'].iloc[-1]:,.2f}")
        st.metric("24H_CHG", f"{((df['Close'].iloc[-1]/df['Close'].iloc[-2])-1)*100:.2f}%")

    with r:
        st.markdown("### // PINE_COMPILER")
        pine_input = st.text_area("PASTE_CODE", height=200, placeholder="//@version=5\nindicator('Greeks')...")
        if st.button("EXECUTE_PINE"):
            if "ta.rsi" in pine_input.lower(): st.session_state.indicators.append("RSI")
            st.toast("Logic Synced to Mainframe")

    with c:
        t_in = st.text_input("ACTIVE_TICKER", value=st.session_state.ticker).upper()
        if t_in != st.session_state.ticker:
            st.session_state.ticker = t_in
            st.rerun()

        t1, t2, t3, t4 = st.tabs(["📊 ANALYSIS", "📉 OPTIONS", "💰 FINANCIALS", "📰 DAILY_NEWSPAPER"])

        with t1:
            # Multi-Pane Charting
            rows = 2 if "RSI" in st.session_state.indicators else 1
            fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3] if rows==2 else [1.0])
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="PRC"), row=1, col=1)
            
            if "EMA" in st.session_state.indicators:
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name="EMA20", line=dict(color="#00ff41")), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], name="EMA50", line=dict(color="#ff4b4b")), row=1, col=1)
            
            if "RSI" in st.session_state.indicators:
                fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI", line=dict(color="#2962ff")), row=2, col=1)
                fig.add_hline(y=70, line_dash="dot", line_color="red", row=2, col=1)
                fig.add_hline(y=30, line_dash="dot", line_color="green", row=2, col=1)

            fig.update_layout(template="plotly_dark", height=650, paper_bgcolor='black', plot_bgcolor='black', xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with t4:
            st.markdown(f"### 📰 THE {st.session_state.ticker} GAZETTE")
            st.caption(f"EDITION: {now} | STATUS: LIVE")
            
            # Simulated "New Person Writing" Style
            with st.container(border=True):
                st.markdown(f"""
                <div class='newspaper-box'>
                    <div class='news-headline'>"{st.session_state.ticker} Markets Are Grinding Retail Into Dust Today"</div>
                    <hr style='border-color: #00ff41'>
                    <p style='font-style: italic;'>By The Institutional Ghostwriter</p>
                    <p>It's another one of those mornings where the tape just won't lie. <b>{st.session_state.ticker}</b> is currently trading at ${df['Close'].iloc[-1]:,.2f}, 
                    showing a relative strength of {df['RSI'].iloc[-1]:.2f}. While the average retail trader is staring at their 5-minute charts, 
                    the whales are busy stacking orders at the institutional levels.</p>
                    <p>Technically, the price action is looking <b>{'extended' if df['RSI'].iloc[-1] > 70 else 'coiled'}</b>. If we don't see a sweep of the 
                    prevailing highs soon, expect a liquidity flush that will leave the "moon boys" crying in their Discord servers.</p>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown("#### 📅 GLOBAL MACRO CALENDAR")
            macro_data = [
                {"Event": "US Core CPI", "Impact": "🔴 HIGH", "Forecast": "0.3%", "Actual": "---"},
                {"Event": "Unemployment Claims", "Impact": "🟡 MED", "Forecast": "225K", "Actual": "228K"}
            ]
            st.table(macro_data)

except Exception as e:
    st.error(f"SYSTEM_HALTED: {e}")
