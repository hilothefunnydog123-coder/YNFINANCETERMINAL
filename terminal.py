import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime

# --- 1. THE "MATRIX" LED TICKER ---
st.set_page_config(layout="wide", page_title="TERMINAL_ULTRA_V16.2", initial_sidebar_state="collapsed")

# 20+ Asset Cycle for Institutional Density
cycle = ["NVDA", "BTC-USD", "AAPL", "ETH-USD", "TSLA", "AMZN", "MSFT", "META", "GOOGL", "SOL-USD", "SPY", "QQQ", "GLD", "VIX", "GC=F", "USO", "PLTR", "AMD"]
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

# --- 2. THE "SAFE-PULSE" ENGINE (Prevents Crashes) ---
if 'ticker' not in st.session_state: st.session_state.ticker = "NVDA"

@st.cache_data(ttl=600)
def fetch_pulse_data(ticker):
    s = yf.Ticker(ticker)
    df = s.history(period="2y")
    df['EMA20'] = ta.ema(df['Close'], length=20)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    
    # --- Safe Financial Check ---
    fin = s.quarterly_financials
    revenue_data = None
    if fin is not None and not fin.empty:
        # Check for various common revenue labels to avoid KeyErrors
        for label in ['Total Revenue', 'Revenue', 'TotalRevenue', 'Operating Revenue']:
            if label in fin.index:
                revenue_data = fin.loc[label]
                break
                
    # --- Safe News Check (Fixes 'title' Error) ---
    try:
        raw_news = s.news
        # Filter out news objects that are missing the 'title' key
        clean_news = [n for n in raw_news if 'title' in n and 'link' in n]
    except:
        clean_news = []
        
    return df, s.info, clean_news, fin, revenue_data

try:
    df, info, news, financials, rev_series = fetch_pulse_data(st.session_state.ticker)

    # --- 3. COMMAND CENTER ---
    l, c, r = st.columns([1, 4.5, 1.2])

    with l:
        st.markdown("### // HUD_CORE")
        st.metric("PRICE", f"${df['Close'].iloc[-1]:,.2f}")
        st.metric("RSI", f"{df['RSI'].iloc[-1]:.1f}")

    with c:
        t_in = st.text_input("SET_ACTIVE_TICKER", value=st.session_state.ticker).upper().strip()
        if t_in != st.session_state.ticker:
            st.session_state.ticker = t_in
            st.rerun()

        tabs = st.tabs(["📊 CHART", "📈 OPTIONS", "💰 FINANCIALS", "📰 THE_PULSE_GAZETTE"])

        with tabs[0]:
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            fig.update_layout(template="plotly_dark", height=650, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with tabs[2]:
            st.subheader("// QUARTERLY_REVENUE_VIZ")
            if rev_series is not None:
                rev_fig = go.Figure(data=[go.Bar(x=rev_series.index, y=rev_series.values, marker_color='#00ff41')])
                rev_fig.update_layout(template="plotly_dark", height=350, title="Quarterly Revenue Trend")
                st.plotly_chart(rev_fig, use_container_width=True)
            else:
                st.info("DATA_UNAVAILABLE: No Revenue keys found in quarterly financials.")
            st.dataframe(financials, use_container_width=True)

        with tabs[3]:
            # --- THE DYNAMIC PULSE NEWSPAPER (Error-Proof) ---
            st.markdown(f"<div class='gazette-frame'><div class='headline-wrap'>{st.session_state.ticker}: THE MARKET PULSE</div>", unsafe_allow_html=True)
            st.write(f"*UPDATED: {datetime.now().strftime('%H:%M:%S')} | LIVE NEWSWIRE*")
            st.write("---")
            
            if news:
                for item in news[:5]: # Top 5 accurate headlines
                    st.markdown(f"### 🗞️ {item['title']}")
                    st.write(f"**SOURCE:** {item.get('publisher', 'N/A')} | [READ_FULL_WIRE]({item['link']})")
                    st.write("---")
            else:
                st.info("SCANNING NEWSWIRE... NO RECENT HEADLINES DETECTED.")
            st.markdown("</div>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"SYSTEM_HALTED: {e}")
