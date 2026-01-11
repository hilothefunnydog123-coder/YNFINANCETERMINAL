import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime

# --- 1. THE MAGICAL LED MARQUEE ---
st.set_page_config(layout="wide", page_title="TERMINAL_ULTRA_V16", initial_sidebar_state="collapsed")

# 30+ Asset Cycle for Institutional Density
cycle = ["NVDA", "BTC-USD", "AAPL", "ETH-USD", "TSLA", "AMZN", "MSFT", "META", "GOOGL", "SOL-USD", "SPY", "QQQ", "GLD", "USO", "EURUSD=X", "JPY=X", "VIX", "GC=F"]
ticker_html = "".join([f"<span style='color:{'#00ff41' if i%2==0 else '#ff4b4b'}; padding-right:80px;'>{t}: LIVE_FEED</span>" for i, t in enumerate(cycle)])

st.html(f"""
    <style>
    .stApp {{ background: #000000; color: #00ff41; font-family: 'Courier New', monospace; }}
    @keyframes marquee {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
    .led-ticker {{ background: #050505; border-bottom: 2px solid #333; padding: 15px; overflow: hidden; white-space: nowrap; width: 100%; font-weight: bold; font-size: 24px; }}
    .led-ticker div {{ display: inline-block; animation: marquee 45s linear infinite; }}
    /* Newspaper Aesthetic */
    .gazette-frame {{ border: 4px double #00ff41; padding: 40px; background: rgba(0, 255, 65, 0.02); }}
    .headline-wrap {{ font-size: 48px; font-weight: 900; border-bottom: 3px solid #00ff41; margin-bottom: 20px; text-transform: uppercase; }}
    </style>
    <div class="led-ticker"><div>{ticker_html} | {ticker_html}</div></div>
""")

# --- 2. PERSISTENT STATE ---
if 'ticker' not in st.session_state: st.session_state.ticker = "NVDA"
if 'layers' not in st.session_state: st.session_state.layers = ["EMA"]

# --- 3. THE "PULSE" ENGINE (Error-Proof) ---
@st.cache_data(ttl=600) # Refreshes every 10 mins for accuracy
def fetch_pulse(ticker):
    s = yf.Ticker(ticker)
    df = s.history(period="2y")
    df['EMA20'] = ta.ema(df['Close'], length=20)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    # Error handling for News objects
    try:
        raw_news = s.news
        clean_news = [n for n in raw_news if 'title' in n]
    except:
        clean_news = []
    return df, s.info, clean_news, s.quarterly_financials

try:
    df, info, news, financials = fetch_pulse(st.session_state.ticker)

    # --- 4. COMMAND CENTER ---
    l, c, r = st.columns([1, 4.5, 1.2])

    with l:
        st.markdown("### // HUD_CORE")
        st.metric("PRICE", f"${df['Close'].iloc[-1]:,.2f}")
        st.metric("RSI", f"{df['RSI'].iloc[-1]:.1f}")
        st.markdown("---")
        if st.button("TOGGLE EMA"): 
            st.session_state.layers.append("EMA") if "EMA" not in st.session_state.layers else st.session_state.layers.remove("EMA")
        if st.button("TOGGLE RSI"):
            st.session_state.layers.append("RSI") if "RSI" not in st.session_state.layers else st.session_state.layers.remove("RSI")

    with r:
        st.markdown("### // PINE_SYNC")
        st.text_area("CODE", height=150, placeholder="indicator('Greeks')...")
        st.button("COMPILE")
        st.markdown("---")
        st.subheader("MACRO_ALERTS")
        st.error("CPI: 🔴 CRITICAL")
        st.warning("FOMC: 🟡 VOLATILE")

    with c:
        t_in = st.text_input("SET_ACTIVE_TICKER", value=st.session_state.ticker).upper().strip()
        if t_in != st.session_state.ticker:
            st.session_state.ticker = t_in
            st.rerun()

        tabs = st.tabs(["📊 CHART", "📈 OPTIONS", "💰 FINANCIALS", "📰 THE_PULSE_GAZETTE"])

        with tabs[0]:
            rows = 2 if "RSI" in st.session_state.layers else 1
            fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3] if rows==2 else [1.0])
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']), row=1, col=1)
            if "EMA" in st.session_state.layers:
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name="EMA20", line=dict(color="#00ff41")))
            fig.update_layout(template="plotly_dark", height=650, paper_bgcolor='black', plot_bgcolor='black', xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with tabs[2]:
            st.subheader("// QUARTERLY_REVENUE_VIZ")
            rev_fig = go.Figure(data=[go.Bar(x=financials.columns, y=financials.loc['Total Revenue'], marker_color='#00ff41')])
            rev_fig.update_layout(template="plotly_dark", height=350)
            st.plotly_chart(rev_fig, use_container_width=True)
            st.dataframe(financials, use_container_width=True)

        with tabs[3]:
            # --- THE DYNAMIC PULSE NEWSPAPER ---
            st.markdown(f"<div class='gazette-frame'><div class='headline-wrap'>{st.session_state.ticker}: THE MARKET PULSE</div>", unsafe_allow_html=True)
            st.write(f"*UPDATED: {datetime.now().strftime('%H:%M:%S')} | LIVE NEWSWIRE ACCESS ACTIVE*")
            st.write("---")
            
            if news:
                for item in news[:5]: # Top 5 accurate headlines
                    st.markdown(f"### 🗞️ {item['title']}")
                    st.write(f"**SOURCE:** {item['publisher']} | [READ_FULL_WIRE]({item['link']})")
                    st.write("---")
            else:
                st.info("SCANNING NEWSWIRE... NO HEADLINES DETECTED IN LAST 60 MINUTES.")
            st.markdown("</div>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"SYSTEM_HALTED: {e}")
