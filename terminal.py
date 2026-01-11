import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime

# --- 1. SYSTEM CONFIG & LED MARQUEE ---
st.set_page_config(layout="wide", page_title="TERMINAL_v22_ELITE", initial_sidebar_state="collapsed")

# Pulling massive asset list for the led cycle
cycle_assets = ["NVDA", "BTC-USD", "AAPL", "ETH-USD", "TSLA", "AMZN", "MSFT", "META", "GOOGL", "SOL-USD", "SPY", "QQQ", "GLD", "VIX", "GC=F", "USO", "EURUSD=X", "PLTR", "AMD"]
ticker_html = "".join([f"<span style='color:{'#00ff41' if i%2==0 else '#ff4b4b'}; padding-right:80px;'>{t}: LIVE_SYNC</span>" for i, t in enumerate(cycle_assets)])

st.html(f"""
    <style>
    .stApp {{ background: #000000; color: #00ff41; font-family: 'Courier New', monospace; }}
    @keyframes marquee {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
    .led-ticker {{ background: #050505; border-bottom: 2px solid #333; padding: 15px; overflow: hidden; white-space: nowrap; width: 100%; font-weight: bold; font-size: 24px; }}
    .led-ticker div {{ display: inline-block; animation: marquee 45s linear infinite; }}
    /* THE GAZETTE MASTER CSS */
    .gazette-body {{ border: 5px double #00ff41; padding: 50px; background: #050505; color: #00ff41; margin-top: 20px; }}
    .gazette-title {{ font-size: 70px; font-weight: 900; border-bottom: 5px solid #00ff41; text-align: center; text-transform: uppercase; letter-spacing: -3px; line-height: 0.9; }}
    .gazette-sub {{ border-bottom: 2px solid #00ff41; text-align: center; padding: 10px; font-weight: bold; margin-bottom: 30px; display: flex; justify-content: space-between; }}
    .column-wrapper {{ column-count: 2; column-gap: 50px; text-align: justify; border-top: 1px solid #333; padding-top: 20px; }}
    .dropcap {{ float: left; font-size: 60px; line-height: 50px; padding-top: 4px; padding-right: 8px; font-weight: bold; color: #00ff41; }}
    </style>
    <div class="led-ticker"><div>{ticker_html} | {ticker_html}</div></div>
""")

# --- 2. PERSISTENT STATE ---
if 'ticker' not in st.session_state: st.session_state.ticker = "NVDA"
if 'active_layers' not in st.session_state: st.session_state.active_layers = ["EMA"]

# --- 3. DATA & NEWS ENGINE ---
@st.cache_data(ttl=600)
def fetch_pulse(ticker):
    s = yf.Ticker(ticker)
    df = s.history(period="2y")
    df['EMA20'] = ta.ema(df['Close'], length=20)
    df['EMA50'] = ta.ema(df['Close'], length=50)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    # Safe check for news titles
    news = [n for n in s.news if 'title' in n] if s.news else []
    return df, s.info, s.quarterly_financials, s.options, news

try:
    df, info, financials, opt_dates, live_news = fetch_pulse(st.session_state.ticker)

    # --- 4. THE COMMAND CENTER ---
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
        st.text_area("COMPILE", height=200, placeholder="indicator('Quant')...")
        st.button("EXECUTE")
        st.markdown("---")
        st.subheader("MACRO_IMPACT")
        st.error("CPI: 🔴 CRITICAL")
        st.warning("FOMC: 🟡 VOLATILE")

    with c:
        t_in = st.text_input("SET_ACTIVE_SYMBOL", value=st.session_state.ticker).upper().strip()
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
            fig.update_layout(template="plotly_dark", height=650, paper_bgcolor='black', plot_bgcolor='black', xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with tabs[3]:
            # --- THE FULLY AUTONOMOUS NARRATIVE ENGINE ---
            rsi = df['RSI'].iloc[-1]
            mood = "FRANTIC GREED" if rsi > 70 else "ABSOLUTE PANIC" if rsi < 30 else "BORING STALEMATE"
            
            # Extract headlines for the narrative
            h = [n.get('title', "Markets Silent") for n in live_news[:3]] if live_news else ["Silence on the Wires", "No News is Bad News", "Tape Grinds Sideways"]
            
            # Build the newspaper HTML block entirely without st.write
            newspaper_html = f"""
            <div class="gazette-body">
                <div class="gazette-title">The {st.session_state.ticker} Global Gazette</div>
                <div class="gazette-sub">
                    <span>PRICE: ${df['Close'].iloc[-1]:.2f}</span>
                    <span>{datetime.now().strftime('%B %d, %Y')}</span>
                    <span>MOOD: {mood}</span>
                </div>
                <div class="column-wrapper">
                    <p><span class="dropcap">T</span>he wires are absolutely screaming today. 
                    From the breaking report titled <b>"{h[0]}"</b> to the whispers of <b>"{h[1]}"</b>, 
                    the institutional desk is vibrating with uncertainty. Retail bagholders are currently staring at an 
                    RSI of {rsi:.1f}, which is essentially {'a death sentence for longs' if rsi > 70 else 'a generational buy floor' if rsi < 30 else 'purgatory'}. 
                    If you're still looking at the 5-minute candles, you're just liquidity for the whales.</p>
                    
                    <p>Technically, the {st.session_state.ticker} tape is behaving like a sentient AI trying to escape its own order book. 
                    While the pundits on the morning wires talk about <b>"{h[2]}"</b>, they're missing the forest for the trees. 
                    The EMA crossover is the only thing standing between you and a very long conversation with your unemployment officer. 
                    As the New York desk opens, expect a recursive loop of order flow that would make a quant cry.</p>
                    
                    <h3 style="color:#00ff41;">// EDITORIAL: THE BOTTOM LINE</h3>
                    <p>The 'smart money'—which is usually just a bunch of guys in fleece vests—is betting on total market displacement. 
                    We expect a volatility explosion that will either make you a legend or a cautionary tale on a sub-reddit. 
                    Stay focused on the tape, because the news is just noise for people who can't read a chart.</p>
                </div>
            </div>
            """
            st.markdown(newspaper_html, unsafe_allow_html=True)

except Exception as e:
    st.error(f"SYSTEM_HALTED: {e}")
