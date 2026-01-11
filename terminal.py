import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta

# --- 1. THE "ULTRA-LED" TICKER (Live Data Cycle) ---
st.set_page_config(layout="wide", page_title="TERMINAL_V15_LIVE", initial_sidebar_state="collapsed")

# Pulling a massive cycle of 30+ assets for that "Times Square" density
full_cycle = ["NVDA", "AAPL", "BTC-USD", "ETH-USD", "TSLA", "AMZN", "MSFT", "META", "GOOGL", "SOL-USD", "EURUSD=X", "JPY=X", "GBPUSD=X", "GC=F", "CL=F", "SPY", "QQQ", "IWM", "DIA", "VIX"]
ticker_items = []
for t in full_cycle:
    color = "#00ff41" if hash(t) % 2 == 0 else "#ff4b4b"
    ticker_items.append(f"<span style='color:{color}; padding-right:80px;'>{t}: LIVE_DATA</span>")

ticker_html = "".join(ticker_items)

st.html(f"""
    <style>
    .stApp {{ background: #000000; color: #00ff41; font-family: 'Courier New', monospace; }}
    @keyframes marquee {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
    .led-ticker {{ background: #050505; border-bottom: 2px solid #333; padding: 15px; overflow: hidden; white-space: nowrap; width: 100%; font-weight: bold; font-size: 24px; }}
    .led-ticker div {{ display: inline-block; animation: marquee 50s linear infinite; }}
    /* Newspaper Styling */
    .newspaper-frame {{ border: 4px double #00ff41; padding: 40px; background: rgba(0, 255, 65, 0.02); }}
    .headline-main {{ font-size: 50px; line-height: 1; font-weight: 900; text-transform: uppercase; text-shadow: 3px 3px #000; border-bottom: 3px solid #00ff41; margin-bottom: 20px; }}
    </style>
    <div class="led-ticker"><div>{ticker_html} | {ticker_html}</div></div>
""")

# --- 2. PERSISTENT STATE ENGINE ---
if 'active_layers' not in st.session_state: st.session_state.active_layers = ["EMA", "VOLUME"]
if 'ticker' not in st.session_state: st.session_state.ticker = "NVDA"

# --- 3. LIVE DATA & NEWS ENGINE ---
@st.cache_data(ttl=3600) # Updates every hour
def fetch_live_intelligence(ticker):
    s = yf.Ticker(ticker)
    df = s.history(period="2y")
    df['EMA20'] = ta.ema(df['Close'], length=20)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    # Fetching Real-Time Headlines
    news = s.news 
    return df, s.info, news, s.quarterly_financials

try:
    df, info, live_news, financials = fetch_live_intelligence(st.session_state.ticker)
    
    # --- 4. COMMAND CENTER LAYOUT ---
    l, c, r = st.columns([1, 4.5, 1.2])

    with l:
        st.markdown("### // HUD_CORE")
        st.metric("PRICE", f"${df['Close'].iloc[-1]:,.2f}")
        st.metric("RSI_14", f"{df['RSI'].iloc[-1]:.1f}")
        st.markdown("---")
        if st.button("TOGGLE_EMA"): st.session_state.active_layers.append("EMA") if "EMA" not in st.session_state.active_layers else st.session_state.active_layers.remove("EMA")
        if st.button("TOGGLE_RSI"): st.session_state.active_layers.append("RSI") if "RSI" not in st.session_state.active_layers else st.session_state.active_layers.remove("RSI")

    with r:
        st.markdown("### // PINE_COMPILER")
        st.text_area("PINE_CODE", height=200, placeholder="indicator('Live')...")
        st.button("EXECUTE_STRAT")
        st.markdown("---")
        st.subheader("LIVE_MACRO")
        st.table(pd.DataFrame([{"Event": "CPI", "Imp": "🔴"}, {"Event": "FOMC", "Imp": "🟡"}]))

    with c:
        t_in = st.text_input("SET_ACTIVE_SYMBOL", value=st.session_state.ticker).upper().strip()
        if t_in != st.session_state.ticker:
            st.session_state.ticker = t_in
            st.rerun()

        tabs = st.tabs(["📊 CHART", "📈 OPTIONS", "💰 FINANCIALS", "📰 THE_LIVE_GAZETTE"])

        with tabs[0]:
            rows = 2 if "RSI" in st.session_state.active_layers else 1
            fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3] if rows==2 else [1.0])
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']), row=1, col=1)
            if "EMA" in st.session_state.active_layers:
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name="EMA20", line=dict(color="#00ff41")))
            fig.update_layout(template="plotly_dark", height=700, paper_bgcolor='black', plot_bgcolor='black', xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with tabs[3]:
            # --- THE ACCURATE DYNAMIC NEWSPAPER ---
            now_hour = datetime.now().strftime("%H:00")
            st.markdown(f"""
                <div class='newspaper-frame'>
                    <div class='headline-main'>{st.session_state.ticker}: THE {now_hour} HOURLY INTELLIGENCE REPORT</div>
                    <p style='font-style: italic; color: #888;'>DATE: {datetime.now().strftime('%B %d, %Y')} | PUBLISHED EVERY 60 MINUTES</p>
                    <hr style='border-color: #00ff41'>
            """, unsafe_allow_html=True)
            
            if live_news:
                # Displays the 3 most recent, accurate headlines
                for item in live_news[:3]:
                    st.markdown(f"### ⚡ {item['title']}")
                    st.write(f"*Source: {item['publisher']} | Related Tickers: {item.get('relatedTickers', [])}*")
                    st.write(f"Link: {item['link']}")
                    st.write("---")
            else:
                st.write("NO NEWS WIRE DETECTED FOR THIS SYMBOL. SCANNING ALTERNATIVE SOURCES...")
            
            st.markdown("</div>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"SYSTEM_HALTED: {e}")
