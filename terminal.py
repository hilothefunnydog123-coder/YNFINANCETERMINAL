import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime
import google.generativeai as genai 

# --- 0. MASTER KEY LOCK (FUEL INJECTED) ---
GEMINI_API_KEY = "AIzaSyAkGNUAYZXnPD83MFq2SAFqzq_fmNWCIqI"

# --- 1. MAJESTIC NEON UI OVERHAUL ---
st.set_page_config(layout="wide", page_title="SOVEREIGN_V33_STABLE", initial_sidebar_state="collapsed")

tickers = ["NVDA", "BTC-USD", "AAPL", "ETH-USD", "TSLA", "AMZN", "MSFT", "META", "GOOGL", "SOL-USD", "SPY", "QQQ", "GLD", "VIX", "GC=F", "USO", "PLTR", "AMD"]
ticker_html = "".join([f"<span style='color:{'#00ff41' if i%2==0 else '#ff00ff'}; padding-right:100px;'>{t}: LIVE_WIRE</span>" for i, t in enumerate(tickers)])

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
    .stApp {{ background: radial-gradient(circle at top, #050a0f 0%, #000000 100%); color: #00ff41; font-family: 'Courier New', monospace; }}
    @keyframes marquee {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
    .led-ticker {{ background: rgba(0,0,0,0.95); border-bottom: 2px solid #00ff41; box-shadow: 0 0 25px rgba(0,255,65,0.4); padding: 22px; overflow: hidden; white-space: nowrap; width: 100%; font-weight: bold; font-size: 28px; font-family: 'Orbitron', sans-serif; }}
    .led-ticker div {{ display: inline-block; animation: marquee 45s linear infinite; }}
    [data-testid="stMetric"] {{ background: rgba(0, 255, 65, 0.05); border-left: 5px solid #00ff41; border-radius: 4px; padding: 15px !important; box-shadow: 10px 10px 20px rgba(0,0,0,0.8); }}
    .stButton>button {{ background: linear-gradient(90deg, #001a00 0%, #004d00 100%); color: #00ff41; border: 1px solid #00ff41; border-radius: 0px; font-family: 'Orbitron'; font-size: 11px; box-shadow: 0 0 10px #00ff41; transition: 0.2s; }}
    .stButton>button:hover {{ background: #00ff41; color: #000; box-shadow: 0 0 40px #00ff41; transform: scale(1.05); }}
    .gazette-body {{ border: 8px double #00ff41; padding: 60px; background: #000; color: #00ff41; margin-top: 30px; box-shadow: 0 0 60px rgba(0,255,65,0.15); }}
    .gazette-title {{ font-family: 'Orbitron', sans-serif; font-size: 90px; font-weight: 900; border-bottom: 10px solid #00ff41; text-align: center; text-transform: uppercase; letter-spacing: -6px; line-height: 0.85; padding-bottom: 15px; text-shadow: 0 0 20px #00ff41; }}
    .gazette-sub {{ border-bottom: 4px solid #00ff41; text-align: center; padding: 18px; font-weight: bold; margin-bottom: 45px; display: flex; justify-content: space-between; font-size: 20px; }}
    .column-wrapper {{ column-count: 2; column-gap: 70px; text-align: justify; line-height: 1.9; font-size: 17px; }}
    .dropcap {{ float: left; font-size: 95px; line-height: 75px; padding-top: 5px; padding-right: 15px; font-weight: bold; color: #00ff41; text-shadow: 4px 4px #000; }}
    </style>
    <div class="led-ticker"><div>{ticker_html} | {ticker_html}</div></div>
""", unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
if 'ticker' not in st.session_state: st.session_state.ticker = "NVDA"
if 'active_layers' not in st.session_state: st.session_state.active_layers = ["EMA"]

@st.cache_data(ttl=600)
def fetch_terminal_data(ticker):
    s = yf.Ticker(ticker)
    df = s.history(period="2y")
    df['EMA20'] = ta.ema(df['Close'], length=20)
    df['EMA50'] = ta.ema(df['Close'], length=50)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    news = [n for n in s.news if 'title' in n] if s.news else []
    return df, s.info, s.quarterly_financials, s.options, news

try:
    df, info, financials, opt_dates, live_news = fetch_terminal_data(st.session_state.ticker)
    l, c, r = st.columns([1, 4.8, 1.2])

    with l:
        st.markdown("### // HUD_ACTIVE")
        st.metric("SPOT_PRICE", f"${df['Close'].iloc[-1]:,.2f}")
        st.metric("MOMENTUM_RSI", f"{df['RSI'].iloc[-1]:.1f}")
        st.markdown("---")
        st.write("🤖 GHOSTWRITER: ACTIVE")
        if st.button("TOGGLE EMA_CROSS"):
            st.session_state.active_layers.append("EMA") if "EMA" not in st.session_state.active_layers else st.session_state.active_layers.remove("EMA")
        if st.button("TOGGLE RSI_PANE"):
            st.session_state.active_layers.append("RSI") if "RSI" not in st.session_state.active_layers else st.session_state.active_layers.remove("RSI")

    with r:
        st.markdown("### // QUANT_PINE")
        st.text_area("CODE", height=200, placeholder="ALGOS_LOCKED...", label_visibility="collapsed")
        st.button("EXECUTE_LOGIC")
        st.error("CPI: 🔴 EXTREME")

    with c:
        t_in = st.text_input("SYMBOL", value=st.session_state.ticker, label_visibility="collapsed").upper().strip()
        if t_in != st.session_state.ticker:
            st.session_state.ticker = t_in
            st.rerun()

        tabs = st.tabs(["📊 ANALYSIS", "📈 GEX_PROFILE", "📉 OPTIONS", "💰 FINANCIALS", "📰 THE_SOVEREIGN_GAZETTE"])

        with tabs[0]:
            rows = 2 if "RSI" in st.session_state.active_layers else 1
            fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3] if rows==2 else [1.0])
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']), row=1, col=1)
            if "EMA" in st.session_state.active_layers:
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name="EMA20", line=dict(color="#00ff41")))
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], name="EMA50", line=dict(color="#ff00ff")))
            fig.update_layout(template="plotly_dark", height=750, paper_bgcolor='black', plot_bgcolor='black', xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with tabs[1]:
            if opt_dates:
                chain = yf.Ticker(st.session_state.ticker).option_chain(opt_dates[0])
                gex_fig = go.Figure()
                gex_fig.add_trace(go.Bar(x=chain.calls['strike'], y=chain.calls['openInterest'], name="Call OI", marker_color='#00ff41'))
                gex_fig.add_trace(go.Bar(x=chain.puts['strike'], y=-chain.puts['openInterest'], name="Put OI", marker_color='#ff00ff'))
                gex_fig.update_layout(barmode='relative', template="plotly_dark", title="Gamma Exposure Profile")
                st.plotly_chart(gex_fig, use_container_width=True)

        with tabs[4]:
            # --- UPDATED STABLE MODEL IDENTIFIER ---
            if GEMINI_API_KEY:
                genai.configure(api_key=GEMINI_API_KEY)
                # Using the more universal model identifier
                model = genai.GenerativeModel('gemini-1.5-flash') 
                
                headlines = "\n".join([f"- {n['title']}" for n in live_news[:5]]) if live_news else "No news available."
                prompt = (f"Act as a snarky, humorous institutional Wall Street writer for 'The Sovereign Gazette'. "
                          f"Write a 200-word newspaper front page report about {st.session_state.ticker}. "
                          f"Ticker Data: Price ${df['Close'].iloc[-1]:.2f}, RSI {df['RSI'].iloc[-1]:.1f}. "
                          f"Include these real headlines from the wire: {headlines}. "
                          f"Use snarky financial slang, mention 'retail bagholders', and keep the majesty high.")
                
                try:
                    response = model.generate_content(prompt)
                    ai_story = response.text
                except Exception as e:
                    ai_story = f"SYSTEM_ERROR: The Ghostwriter was detained by the SEC. ({e})"
            else:
                ai_story = "ERROR: API KEY NOT FOUND."

            st.markdown(f"""
                <div class="gazette-body">
                    <div class="gazette-title">The Sovereign {st.session_state.ticker} Gazette</div>
                    <div class="gazette-sub">
                        <span>INDEX_PRICE: ${df['Close'].iloc[-1]:.2f}</span>
                        <span>{datetime.now().strftime('%B %d, %Y')}</span>
                        <span>SENTIMENT: GEMINI_SENTIENT</span>
                    </div>
                    <div class="column-wrapper">
                        <p><span class="dropcap">{ai_story[0] if ai_story else 'T'}</span>{ai_story[1:] if ai_story else 'The wires are cold.'}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"SYSTEM_HALTED: {e}")
