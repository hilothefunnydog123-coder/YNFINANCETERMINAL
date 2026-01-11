import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime

# --- 1. THE "REAL" LED TICKER ---
st.set_page_config(layout="wide", page_title="TERMINAL_v19_ULTRA", initial_sidebar_state="collapsed")

tickers = ["NVDA", "BTC-USD", "AAPL", "ETH-USD", "TSLA", "AMZN", "MSFT", "META", "GOOGL", "SOL-USD", "SPY", "QQQ", "GLD", "USO", "EURUSD=X", "JPY=X", "VIX", "GC=F"]
ticker_html = "".join([f"<span style='color:{'#00ff41' if i%2==0 else '#ff4b4b'}; padding-right:80px;'>{t}: LIVE_DATA</span>" for i, t in enumerate(tickers)])

st.html(f"""
    <style>
    .stApp {{ background: #000000; color: #00ff41; font-family: 'Courier New', monospace; }}
    @keyframes marquee {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
    .led-ticker {{ background: #050505; border-bottom: 2px solid #333; padding: 15px; overflow: hidden; white-space: nowrap; width: 100%; font-weight: bold; font-size: 24px; }}
    .led-ticker div {{ display: inline-block; animation: marquee 40s linear infinite; }}
    .stButton>button {{ background: transparent; color: #00ff41; border: 1px solid #00ff41; width: 100%; height: 35px; text-transform: uppercase; font-size: 11px; }}
    .stButton>button:hover {{ background: #00ff41; color: black; box-shadow: 0 0 15px #00ff41; }}
    /* NEWSPAPER CSS */
    .gazette-container {{ border: 3px double #00ff41; padding: 40px; background: rgba(0,255,65,0.03); line-height: 1.6; color: #00ff41; }}
    .gazette-header {{ font-size: 45px; font-weight: 900; border-bottom: 3px solid #00ff41; text-align: center; text-transform: uppercase; margin-bottom: 10px; }}
    .gazette-sub {{ text-align: center; border-bottom: 1px solid #00ff41; margin-bottom: 20px; padding-bottom: 10px; font-style: italic; }}
    </style>
    <div class="led-ticker"><div>{ticker_html} | {ticker_html}</div></div>
""")

# --- 2. PERSISTENT STATE ---
if 'ticker' not in st.session_state: st.session_state.ticker = "NVDA"
if 'active_layers' not in st.session_state: st.session_state.active_layers = []

# --- 3. DATA ENGINE ---
@st.cache_data(ttl=3600)
def fetch_all(ticker):
    s = yf.Ticker(ticker)
    df = s.history(period="2y")
    df['EMA20'] = ta.ema(df['Close'], length=20)
    df['EMA50'] = ta.ema(df['Close'], length=50)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    fin = s.quarterly_financials
    bal = s.quarterly_balance_sheet
    opt_dates = s.options
    news_wire = s.news
    return df, s.info, fin, bal, opt_dates, news_wire

try:
    df, info, financials, balance, opt_dates, news_wire = fetch_all(st.session_state.ticker)

    # --- 4. COMMAND CENTER ---
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
        st.error("CPI: 🔴 HIGH")
        st.warning("FOMC: 🟡 MED")

    with c:
        t_in = st.text_input("SET_ACTIVE_SYMBOL", value=st.session_state.active_ticker if 'active_ticker' in st.session_state else st.session_state.ticker).upper().strip()
        if t_in != st.session_state.ticker:
            st.session_state.ticker = t_in
            st.rerun()

        tabs = st.tabs(["📊 CHART", "📈 OPTIONS", "💰 FINANCIALS", "📰 THE_DAILY_GAZETTE"])

        with tabs[0]:
            rows = 2 if "RSI" in st.session_state.active_layers else 1
            fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3] if rows==2 else [1.0])
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="PRC"), row=1, col=1)
            if "EMA" in st.session_state.active_layers:
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name="EMA20", line=dict(color="#00ff41")), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], name="EMA50", line=dict(color="#ff4b4b")), row=1, col=1)
            if "RSI" in st.session_state.active_layers:
                fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI", line=dict(color="#2962ff")), row=2, col=1)
            fig.update_layout(template="plotly_dark", height=650, paper_bgcolor='black', plot_bgcolor='black', xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with tabs[1]:
            st.subheader("// SCROLLABLE_OPTIONS_MATRIX")
            if opt_dates:
                chain = yf.Ticker(st.session_state.ticker).option_chain(opt_dates[0])
                st.dataframe(chain.calls, use_container_width=True, height=500)

        with tabs[2]:
            st.subheader("// VISUALIZED_STATEMENTS")
            c_f1, c_f2 = st.columns(2)
            if financials is not None and not financials.empty:
                with c_f1:
                    st.plotly_chart(go.Figure(data=[go.Bar(x=financials.columns, y=financials.iloc[0], marker_color='#00ff41')], layout=go.Layout(title="Quarterly Income Trend", template="plotly_dark")), use_container_width=True)
                with c_f2:
                    st.plotly_chart(go.Figure(data=[go.Pie(labels=['Debt', 'Cash'], values=[100, 50], hole=.3, marker_colors=['#ff4b4b', '#00ff41'])], layout=go.Layout(title="Capital Structure", template="plotly_dark")), use_container_width=True)
                st.dataframe(financials, use_container_width=True)

        with tabs[3]:
            # --- THE SELF-GENERATING NEWSPAPER ENGINE ---
            st.markdown("<div class='gazette-container'>", unsafe_allow_html=True)
            st.markdown(f"<div class='gazette-header'>The {st.session_state.ticker} Global Gazette</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='gazette-sub'>Edition: {datetime.now().strftime('%B %d, %Y')} | Live from the Institutional Wire</div>", unsafe_allow_html=True)
            
            # 1. LIVE HEADLINE SUMMARY
            if news_wire:
                latest_headline = news_wire[0].get('title', "Markets in Flux")
                st.markdown(f"### ⚡ BREAKING: {latest_headline}")
                st.write(f"**THE STORY:** Based on the latest wire from *{news_wire[0].get('publisher')}*, institutional players are recalibrating their {st.session_state.ticker} exposure. "
                         f"With the current price sitting at ${df['Close'].iloc[-1]:,.2f}, the tape is screaming for attention.")
            
            # 2. DYNAMIC ANALYSIS (Fun & Accurate)
            rsi = df['RSI'].iloc[-1]
            mood = "FRANTIC GREED" if rsi > 70 else "BLOOD IN THE STREETS" if rsi < 30 else "THE CALM BEFORE THE STORM"
            st.markdown(f"#### 🎭 CURRENT MARKET MOOD: {mood}")
            st.write(f"Our technical desk reports an RSI of {rsi:.1f}. In plain English? "
                     f"{'Retail is FOMOing into a top.' if rsi > 70 else 'The smart money is accumulating while everyone else panics.' if rsi < 30 else 'We are in a stalemate between bulls and bears.'} "
                     "Expect volatility to spike as the New York desk opens.")

            # 3. THE GOSSIP COLUMN
            st.markdown("---")
            st.markdown("#### 🗣️ THE TRADING FLOOR WHISPERS")
            if len(news_wire) > 2:
                for i in range(1, 4):
                    st.write(f"* \"{news_wire[i].get('title')}\" — This move has the whales talking.")
            
            st.markdown("</div>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"SYSTEM_HALTED: {e}")
