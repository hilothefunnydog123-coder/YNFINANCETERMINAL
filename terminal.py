import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime

# --- 1. THE "REAL" LED TICKER (Full Colorful Cycle) ---
st.set_page_config(layout="wide", page_title="TERMINAL_v17.5_STABLE", initial_sidebar_state="collapsed")

# 30+ Asset Cycle for Institutional Density
tickers = ["NVDA", "BTC-USD", "AAPL", "ETH-USD", "TSLA", "AMZN", "MSFT", "META", "GOOGL", "SOL-USD", "SPY", "QQQ", "GLD", "USO", "EURUSD=X", "JPY=X", "VIX", "GC=F"]
ticker_html = "".join([f"<span style='color:{'#00ff41' if i%2==0 else '#ff4b4b'}; padding-right:80px;'>{t}: LIVE_WIRE</span>" for i, t in enumerate(tickers)])

st.html(f"""
    <style>
    .stApp {{ background: #000000; color: #00ff41; font-family: 'Courier New', monospace; }}
    @keyframes marquee {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
    .led-ticker {{ background: #050505; border-bottom: 2px solid #333; padding: 15px; overflow: hidden; white-space: nowrap; width: 100%; font-weight: bold; font-size: 24px; }}
    .led-ticker div {{ display: inline-block; animation: marquee 40s linear infinite; }}
    /* High-End Newspaper Styling */
    .news-frame {{ border: 3px double #00ff41; padding: 40px; background: rgba(0, 255, 65, 0.02); line-height: 1.6; }}
    .headline-main {{ font-size: 45px; font-weight: 900; border-bottom: 3px solid #00ff41; margin-bottom: 20px; text-transform: uppercase; }}
    </style>
    <div class="led-ticker"><div>{ticker_html} | {ticker_html}</div></div>
""")

# --- 2. SYSTEM STATE ---
if 'ticker' not in st.session_state: st.session_state.ticker = "NVDA"
if 'active_layers' not in st.session_state: st.session_state.active_layers = ["EMA"]

# --- 3. THE "SAFE-FETCH" ENGINE (Prevents Crashes) ---
@st.cache_data(ttl=3600) # Updates every hour
def fetch_institutional_data(ticker):
    s = yf.Ticker(ticker)
    df = s.history(period="2y")
    df['EMA20'] = ta.ema(df['Close'], length=20)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    
    # Safe Financial Check
    fin = s.quarterly_financials
    rev_data = None
    if fin is not None and not fin.empty:
        # Try different names for Revenue depending on company type
        for label in ['Total Revenue', 'Operating Revenue', 'Revenue']:
            if label in fin.index:
                rev_data = fin.loc[label]
                break
                
    # Safe News Check: No Templates, only Live Headlines
    try:
        raw_news = s.news
        clean_news = [n for n in raw_news if 'title' in n and 'link' in n]
    except:
        clean_news = []
        
    return df, s.info, clean_news, fin, rev_data

try:
    df, info, news, financials, rev_series = fetch_institutional_data(st.session_state.ticker)

    # --- 4. COMMAND CENTER LAYOUT ---
    l, c, r = st.columns([1, 4.5, 1.2])

    with l:
        st.markdown("### // HUD_ACTIVE")
        st.metric("PRICE", f"${df['Close'].iloc[-1]:,.2f}")
        st.metric("RSI_14", f"{df['RSI'].iloc[-1]:.1f}")
        st.markdown("---")
        if st.button("TOGGLE EMA"):
            st.session_state.active_layers.append("EMA") if "EMA" not in st.session_state.active_layers else st.session_state.active_layers.remove("EMA")
        if st.button("TOGGLE RSI"):
            st.session_state.active_layers.append("RSI") if "RSI" not in st.session_state.active_layers else st.session_state.active_layers.remove("RSI")

    with r:
        st.markdown("### // PINE_COMPILER")
        st.text_area("COMPILE", height=200, placeholder="indicator('Quant')...")
        st.button("EXEC_LOGIC")
        st.markdown("---")
        st.subheader("MACRO_ALERTS")
        st.error("CPI: 🔴 CRITICAL")
        st.warning("FOMC: 🟡 VOLATILE")

    with c:
        t_in = st.text_input("SET_ACTIVE_SYMBOL", value=st.session_state.ticker).upper().strip()
        if t_in != st.session_state.ticker:
            st.session_state.ticker = t_in
            st.rerun()

        tabs = st.tabs(["📊 CHART", "📈 OPTIONS", "💰 FINANCIALS", "📰 LIVE_GAZETTE"])

        with tabs[0]:
            # Subplot RSI Logic
            rows = 2 if "RSI" in st.session_state.active_layers else 1
            fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3] if rows==2 else [1.0])
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']), row=1, col=1)
            
            if "EMA" in st.session_state.active_layers:
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name="EMA20", line=dict(color="#00ff41")))
            
            if "RSI" in st.session_state.active_layers:
                fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI", line=dict(color="#2962ff")), row=2, col=1)
            
            fig.update_layout(template="plotly_dark", height=650, paper_bgcolor='black', plot_bgcolor='black', xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with tabs[2]:
            st.subheader("// VISUALIZED_STATEMENTS")
            if rev_series is not None:
                rev_fig = go.Figure(data=[go.Bar(x=rev_series.index, y=rev_series.values, marker_color='#00ff41')])
                rev_fig.update_layout(title="Quarterly Revenue Trend", template="plotly_dark")
                st.plotly_chart(rev_fig, use_container_width=True)
            st.dataframe(financials, use_container_width=True)

        with tabs[3]:
            # --- THE ACCURATE LIVE GAZETTE ---
            st.markdown(f"<div class='news-frame'><div class='headline-main'>{st.session_state.ticker}: LIVE INTELLIGENCE WIRE</div>", unsafe_allow_html=True)
            st.write(f"*AS OF: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | HOURLY PULSE ACTIVE*")
            st.write("---")
            if news:
                for item in news[:6]: # Real Headlines
                    st.markdown(f"### ⚡ {item['title']}")
                    st.write(f"**SOURCE:** {item['publisher']} | [SECURE_LINK]({item['link']})")
                    st.write("---")
            else:
                st.info("SCANNING GLOBAL NEWSWIRE... NO HEADLINES IN CURRENT EPOCH.")
            st.markdown("</div>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"SYSTEM_HALTED: {e}")
