import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime

# --- 1. THE "REAL" LED TICKER (Full Colorful Cycle) ---
st.set_page_config(layout="wide", page_title="TERMINAL_v18_ULTRA", initial_sidebar_state="collapsed")

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
    .news-card {{ border: 2px solid #333; padding: 15px; margin-bottom: 10px; background: rgba(0,255,65,0.02); }}
    </style>
    <div class="led-ticker"><div>{ticker_html} | {ticker_html}</div></div>
""")

# --- 2. PERSISTENT STATE ---
if 'ticker' not in st.session_state: st.session_state.ticker = "NVDA"
if 'active_layers' not in st.session_state: st.session_state.active_layers = []

# --- 3. DATA ENGINE ---
@st.cache_data(ttl=600)
def fetch_all(ticker):
    s = yf.Ticker(ticker)
    df = s.history(period="2y")
    df['EMA20'] = ta.ema(df['Close'], length=20)
    df['EMA50'] = ta.ema(df['Close'], length=50)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    
    # Financials Safe-Fetch
    fin = s.quarterly_financials
    bal = s.quarterly_balance_sheet
    
    # Options Chain
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
        # Buttons toggle layer state
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
        t_in = st.text_input("SET_ACTIVE_SYMBOL", value=st.session_state.ticker).upper().strip()
        if t_in != st.session_state.ticker:
            st.session_state.ticker = t_in
            st.rerun()

        tabs = st.tabs(["📊 CHART", "📈 OPTIONS", "💰 FINANCIALS", "📰 LIVE_GAZETTE"])

        with tabs[0]:
            rows = 2 if "RSI" in st.session_state.active_layers else 1
            fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3] if rows==2 else [1.0])
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="PRC"), row=1, col=1)
            
            # EMA Layer logic
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
                # Fetching the first available expiry date
                chain = yf.Ticker(st.session_state.ticker).option_chain(opt_dates[0])
                st.dataframe(chain.calls, use_container_width=True, height=500)
            else:
                st.warning("NO OPTIONS DATA FOUND FOR SYMBOL")

        with tabs[2]:
            st.subheader("// VISUALIZED_STATEMENTS")
            c_f1, c_f2 = st.columns(2)
            with c_f1:
                # Revenue Chart
                if 'Total Revenue' in financials.index:
                    st.plotly_chart(go.Figure(data=[go.Bar(x=financials.columns, y=financials.loc['Total Revenue'], marker_color='#00ff41')], 
                                    layout=go.Layout(title="Quarterly Revenue", template="plotly_dark")), use_container_width=True)
            with c_f2:
                # Debt Chart
                if balance is not None and 'Total Debt' in balance.index:
                    st.plotly_chart(go.Figure(data=[go.Bar(x=balance.columns, y=balance.loc['Total Debt'], marker_color='#ff4b4b')], 
                                    layout=go.Layout(title="Total Debt Load", template="plotly_dark")), use_container_width=True)
            st.dataframe(financials, use_container_width=True)

        with tabs[3]:
            st.subheader("// LIVE_INTELLIGENCE_WIRE")
            if news_wire:
                for n in news_wire[:8]: # Display 8 most recent
                    st.markdown(f"""
                        <div class='news-card'>
                            <h4 style='color:#00ff41;'>⚡ {n.get('title', 'N/A')}</h4>
                            <p style='font-size:12px;'>Source: {n.get('publisher', 'N/A')} | <a href="{n.get('link')}" target="_blank">Read Wire</a></p>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("SCANNING NEWSWIRE... NO HEADLINES IN CURRENT EPOCH.")

except Exception as e:
    st.error(f"SYSTEM_HALTED: {e}")
