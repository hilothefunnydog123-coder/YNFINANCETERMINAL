import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime

# --- 1. SYSTEM CONFIG & HIDDEN INTERFACE ---
st.set_page_config(layout="wide", page_title="TERMINAL_v23_ULTRA", initial_sidebar_state="collapsed")

# 30+ Asset Cycle for the high-density ticker tape
tickers = ["NVDA", "BTC-USD", "AAPL", "ETH-USD", "TSLA", "AMZN", "MSFT", "META", "GOOGL", "SOL-USD", "SPY", "QQQ", "GLD", "VIX", "GC=F", "USO", "EURUSD=X", "PLTR", "AMD"]
ticker_html = "".join([f"<span style='color:{'#00ff41' if i%2==0 else '#ff4b4b'}; padding-right:80px;'>{t}: LIVE_WIRE</span>" for i, t in enumerate(tickers)])

st.markdown(f"""
    <style>
    .stApp {{ background: #000000; color: #00ff41; font-family: 'Courier New', monospace; }}
    @keyframes marquee {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
    .led-ticker {{ background: #050505; border-bottom: 2px solid #333; padding: 15px; overflow: hidden; white-space: nowrap; width: 100%; font-weight: bold; font-size: 24px; }}
    .led-ticker div {{ display: inline-block; animation: marquee 45s linear infinite; }}
    .stTabs [data-baseweb="tab-list"] {{ background-color: #000; border-bottom: 1px solid #333; }}
    .stTabs [data-baseweb="tab"] {{ color: #00ff41 !important; }}
    /* Newspaper Master CSS */
    .gazette-body {{ border: 5px double #00ff41; padding: 50px; background: #050505; color: #00ff41; margin-top: 20px; }}
    .gazette-title {{ font-size: 70px; font-weight: 900; border-bottom: 5px solid #00ff41; text-align: center; text-transform: uppercase; letter-spacing: -3px; }}
    .gazette-sub {{ border-bottom: 2px solid #00ff41; text-align: center; padding: 10px; font-weight: bold; margin-bottom: 30px; display: flex; justify-content: space-between; }}
    .column-wrapper {{ column-count: 2; column-gap: 50px; text-align: justify; }}
    </style>
    <div class="led-ticker"><div>{ticker_html} | {ticker_html}</div></div>
""", unsafe_allow_html=True)

# --- 2. PERSISTENT STATE ---
if 'ticker' not in st.session_state: st.session_state.ticker = "NVDA"
if 'active_layers' not in st.session_state: st.session_state.active_layers = ["EMA"]

# --- 3. DATA & NEWS ENGINE (Fixed Empty Tabs) ---
@st.cache_data(ttl=600)
def fetch_terminal_data(ticker):
    s = yf.Ticker(ticker)
    df = s.history(period="2y")
    df['EMA20'] = ta.ema(df['Close'], length=20)
    df['EMA50'] = ta.ema(df['Close'], length=50)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    # Explicitly fetching for tabs
    fin = s.quarterly_financials
    bal = s.quarterly_balance_sheet
    opts = s.options
    news = [n for n in s.news if 'title' in n] if s.news else []
    return df, s.info, fin, bal, opts, news

try:
    df, info, financials, balance, opt_dates, live_news = fetch_terminal_data(st.session_state.ticker)

    # --- 4. COMMAND CENTER LAYOUT ---
    l, c, r = st.columns([1, 4.5, 1.2])

    with l:
        st.markdown("### // HUD_ACTIVE")
        st.metric("PRICE", f"${df['Close'].iloc[-1]:,.2f}")
        st.metric("RSI_14", f"{df['RSI'].iloc[-1]:.1f}")
        st.markdown("---")
        if st.button("TOGGLE EMA_CROSS"):
            st.session_state.active_layers.append("EMA") if "EMA" not in st.session_state.active_layers else st.session_state.active_layers.remove("EMA")
        if st.button("TOGGLE RSI"):
            st.session_state.active_layers.append("RSI") if "RSI" not in st.session_state.active_layers else st.session_state.active_layers.remove("RSI")

    with r:
        st.markdown("### // PINE_HUB")
        st.text_area("COMPILE", height=200, placeholder="indicator('Quant')...", label_visibility="collapsed")
        st.button("EXECUTE")
        st.markdown("---")
        st.subheader("MACRO_IMPACT")
        st.error("CPI: 🔴 CRITICAL")
        st.warning("FOMC: 🟡 VOLATILE")

    with c:
        t_in = st.text_input("SET_ACTIVE_SYMBOL", value=st.session_state.ticker, label_visibility="collapsed").upper().strip()
        if t_in != st.session_state.ticker:
            st.session_state.ticker = t_in
            st.rerun()

        tabs = st.tabs(["📊 CHART", "📈 OPTIONS", "💰 FINANCIALS", "📰 THE_SENTIENT_GAZETTE"])

        with tabs[0]:
            rows = 2 if "RSI" in st.session_state.active_layers else 1
            fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3] if rows==2 else [1.0])
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']), row=1, col=1)
            if "EMA" in st.session_state.active_layers:
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name="EMA20", line=dict(color="#00ff41")), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], name="EMA50", line=dict(color="#ff4b4b")), row=1, col=1)
            if "RSI" in st.session_state.active_layers:
                fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI", line=dict(color="#2962ff")), row=2, col=1)
            fig.update_layout(template="plotly_dark", height=650, paper_bgcolor='black', plot_bgcolor='black', xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True)

        with tabs[1]:
            st.subheader("// OPTIONS_DEEP_CHAIN")
            if opt_dates:
                # Fixed: Pulling chain for the first available expiry
                chain = yf.Ticker(st.session_state.ticker).option_chain(opt_dates[0])
                st.dataframe(chain.calls, use_container_width=True, height=600)
            else:
                st.warning("NO DERIVATIVES FOUND FOR THIS SYMBOL")

        with tabs[2]:
            st.subheader("// QUARTERLY_FINANCIALS_VIZ")
            if financials is not None and not financials.empty:
                # Fixed: Visualizing revenue trend
                fin_fig = go.Figure(data=[go.Bar(x=financials.columns, y=financials.iloc[0], marker_color='#00ff41')])
                fin_fig.update_layout(title="Institutional Revenue Matrix", template="plotly_dark", paper_bgcolor='black')
                st.plotly_chart(fin_fig, use_container_width=True)
                st.dataframe(financials, use_container_width=True)
            else:
                st.info("NO FINANCIAL STATEMENTS ON RECORD")

        with tabs[3]:
            # --- THE FULLY AUTONOMOUS NARRATIVE ENGINE ---
            rsi = df['RSI'].iloc[-1]
            mood = "FRANTIC GREED" if rsi > 70 else "ABSOLUTE PANIC" if rsi < 30 else "BORING STALEMATE"
            h = [n.get('title', "Tape Grinds Sideways") for n in live_news[:3]] if live_news else ["Silence on the Wires", "No News is Bad News", "Order Flow Flatlines"]
            
            # Pure HTML Injection for the Newspaper
            newspaper_html = f"""
            <div class="gazette-body">
                <div class="gazette-title">The {st.session_state.ticker} Global Gazette</div>
                <div class="gazette-sub">
                    <span>PRICE: ${df['Close'].iloc[-1]:.2f}</span>
                    <span>{datetime.now().strftime('%B %d, %Y')}</span>
                    <span>SENTIMENT: {mood}</span>
                </div>
                <div class="column-wrapper">
                    <p>The institutional wire is absolutely screaming. From the breaking report titled <b>"{h[0]}"</b> to the whispers of <b>"{h[1]}"</b>, 
                    the desk is vibrating with uncertainty. Retail participants are staring at an 
                    RSI of {rsi:.1f}, which is essentially {'a death sentence for the over-leveraged' if rsi > 70 else 'a generational accumulation floor' if rsi < 30 else 'market purgatory'}. 
                    If you're still chasing 1-minute candles, you're simply providing liquidity for the whales.</p>
                    
                    <p>Technically, the {st.session_state.ticker} tape is behaving like a sentient machine. 
                    While the morning news focuses on <b>"{h[2]}"</b>, the smart money is focused on capital preservation. 
                    The EMA crossover remains the only guardrail against a recursive loop of order flow that would make a quant cry. 
                    As the New York desk opens, expect total market displacement.</p>
                </div>
            </div>
            """
            st.markdown(newspaper_html, unsafe_allow_html=True)

except Exception as e:
    st.error(f"SYSTEM_HALTED: {e}")
