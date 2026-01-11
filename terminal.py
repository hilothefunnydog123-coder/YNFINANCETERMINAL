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

# --- 1. MAJESTIC NEON UI & DYNAMIC TICKER ---
st.set_page_config(layout="wide", page_title="SOVEREIGN_V36_LOCK", initial_sidebar_state="collapsed")

# Initialize ticker in session state immediately
if 'ticker' not in st.session_state: st.session_state.ticker = "NVDA"
if 'active_layers' not in st.session_state: st.session_state.active_layers = ["EMA"]

# High-density asset list
tickers_list = ["NVDA", "BTC-USD", "AAPL", "ETH-USD", "TSLA", "AMZN", "MSFT", "META", "GOOGL", "SOL-USD", "SPY", "QQQ", "GLD", "VIX", "GC=F", "USO", "PLTR", "AMD"]

# Dynamic Marquee Logic: Injects real-time prices into the top bar
@st.cache_data(ttl=60)
def get_marquee_html(tickers):
    html_parts = []
    for t in tickers:
        try:
            # Quick fetch for marquee only
            p = yf.Ticker(t).fast_info['lastPrice']
            color = "#00ff41" if t == st.session_state.ticker else "#00f0ff"
            html_parts.append(f"<span style='color:{color}; padding-right:100px;'>{t}: ${p:,.2f}</span>")
        except:
            html_parts.append(f"<span style='color:#ff00ff; padding-right:100px;'>{t}: SYNCING...</span>")
    return "".join(html_parts)

ticker_content = get_marquee_html(tickers_list)

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
    .stApp {{ background: radial-gradient(circle at top, #050a0f 0%, #000000 100%); color: #00ff41; font-family: 'Courier New', monospace; }}
    @keyframes marquee {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
    .led-ticker {{ background: rgba(0,0,0,0.95); border-bottom: 2px solid #00ff41; box-shadow: 0 0 25px rgba(0,255,65,0.4); padding: 22px; overflow: hidden; white-space: nowrap; width: 100%; font-weight: bold; font-size: 28px; font-family: 'Orbitron', sans-serif; }}
    .led-ticker div {{ display: inline-block; animation: marquee 45s linear infinite; }}
    [data-testid="stMetric"] {{ background: rgba(0, 255, 65, 0.05); border-left: 5px solid #00ff41; border-radius: 4px; padding: 15px !important; box-shadow: 10px 10px 20px rgba(0,0,0,0.8); }}
    .stButton>button {{ background: linear-gradient(90deg, #001a00 0%, #004d00 100%); color: #00ff41; border: 1px solid #00ff41; border-radius: 0px; font-family: 'Orbitron'; font-size: 11px; }}
    .gazette-body {{ border: 8px double #00ff41; padding: 60px; background: #000; color: #00ff41; margin-top: 30px; box-shadow: 0 0 60px rgba(0,255,65,0.15); }}
    .gazette-title {{ font-family: 'Orbitron', sans-serif; font-size: 90px; font-weight: 900; border-bottom: 10px solid #00ff41; text-align: center; text-transform: uppercase; letter-spacing: -6px; line-height: 0.85; padding-bottom: 15px; }}
    .column-wrapper {{ column-count: 2; column-gap: 70px; text-align: justify; line-height: 1.9; }}
    .dropcap {{ float: left; font-size: 95px; line-height: 75px; padding-top: 5px; padding-right: 15px; font-weight: bold; color: #00ff41; text-shadow: 4px 4px #000; }}
    </style>
    <div class="led-ticker"><div>{ticker_content} | {ticker_content}</div></div>
""", unsafe_allow_html=True)

# --- 2. DATA ENGINE (FIXED SYNC) ---
@st.cache_data(ttl=600)
def fetch_master_data(ticker):
    s = yf.Ticker(ticker)
    # Price History
    df = s.history(period="2y")
    df['EMA20'] = ta.ema(df['Close'], length=20)
    df['EMA50'] = ta.ema(df['Close'], length=50)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    # Financials & Balance Sheet
    fin = s.quarterly_financials
    bal = s.quarterly_balance_sheet
    # Derivatives & Wire
    opts = s.options
    news = [n for n in s.news if 'title' in n] if s.news else []
    return df, s.info, fin, bal, opts, news

try:
    df, info, financials, balance, opt_dates, live_news = fetch_master_data(st.session_state.ticker)
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
        st.text_area("CODE", height=200, label_visibility="collapsed")
        st.button("EXECUTE_LOGIC")
        st.error("CPI: 🔴 EXTREME")

    with c:
        t_in = st.text_input("SET_ACTIVE_SYMBOL", value=st.session_state.ticker, label_visibility="collapsed").upper().strip()
        if t_in != st.session_state.ticker:
            st.session_state.ticker = t_in
            st.rerun()

        tabs = st.tabs(["📊 ANALYSIS", "📈 GEX_PROFILE", "📉 OPTIONS", "💰 FINANCIALS", "📰 THE_SOVEREIGN_GAZETTE"])

        with tabs[0]:
            rows = 2 if "RSI" in st.session_state.active_layers else 1
            fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3] if rows==2 else [1.0], vertical_spacing=0.02)
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="PRICE"), row=1, col=1)
            if "EMA" in st.session_state.active_layers:
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name="EMA20", line=dict(color="#00ff41", width=1.5)), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], name="EMA50", line=dict(color="#ff00ff", width=1.5)), row=1, col=1)
            if "RSI" in st.session_state.active_layers:
                fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI", line=dict(color="#00f0ff", width=2)), row=2, col=1)
            fig.update_layout(template="plotly_dark", height=750, paper_bgcolor='black', plot_bgcolor='black', xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with tabs[1]:
            st.subheader("// GAMMA_EXPOSURE_PROFILE")
            if opt_dates:
                chain = yf.Ticker(st.session_state.ticker).option_chain(opt_dates[0])
                gex_fig = go.Figure()
                gex_fig.add_trace(go.Bar(x=chain.calls['strike'], y=chain.calls['openInterest'], name="Calls", marker_color='#00ff41'))
                gex_fig.add_trace(go.Bar(x=chain.puts['strike'], y=-chain.puts['openInterest'], name="Puts", marker_color='#ff00ff'))
                gex_fig.update_layout(barmode='relative', template="plotly_dark")
                st.plotly_chart(gex_fig, use_container_width=True)
                [Image of an options gamma exposure chart showing call and put walls]

        with tabs[2]:
            st.subheader("// LIVE_OPTION_CHAIN")
            if opt_dates:
                chain = yf.Ticker(st.session_state.ticker).option_chain(opt_dates[0])
                st.dataframe(chain.calls.style.set_properties(**{'background-color': '#050a0f', 'color': '#00ff41'}), use_container_width=True, height=600)
                [Image of NVDA option chain showing strike price and implied volatility]
            else: st.info("NO_DERIVATIVES")

        with tabs[3]:
            st.subheader("// QUARTERLY_REVENUE_MATRIX")
            if financials is not None and not financials.empty:
                rev_label = next((l for l in ['Total Revenue', 'Operating Revenue', 'Revenue'] if l in financials.index), financials.index[0])
                fin_fig = go.Figure(data=[go.Bar(x=financials.columns, y=financials.loc[rev_label], marker_color='#00ff41')])
                fin_fig.update_layout(template="plotly_dark", paper_bgcolor='black')
                st.plotly_chart(fin_fig, use_container_width=True)
                st.dataframe(financials, use_container_width=True)
                [Image of quarterly revenue bar chart for a technology company]
            else: st.info("DATA_OFFLINE")

        with tabs[4]:
            # --- THE AUTONOMOUS GHOSTWRITER (LOCKED DISCOVERY) ---
            ai_story = ""
            if GEMINI_API_KEY:
                try:
                    genai.configure(api_key=GEMINI_API_KEY)
                    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    target_model = available_models[0] if available_models else "gemini-1.5-flash"
                    model_engine = genai.GenerativeModel(target_model)
                    headlines_str = "\n".join([f"- {n['title']}" for n in live_news[:5]]) if live_news else "Tape silent."
                    prompt = (f"Write a snarky, humorous 200-word front page for {st.session_state.ticker}. "
                              f"Current Price: ${df['Close'].iloc[-1]:.2f}, RSI: {df['RSI'].iloc[-1]:.1f}. "
                              f"Headlines: {headlines_str}. Use institutional slang and mention bagholders.")
                    response = model_engine.generate_content(prompt)
                    ai_story = response.text
                except Exception as e:
                    ai_story = f"SYSTEM_ERROR: The Ghostwriter is under SEC investigation. Error: {e}"
            
            st.markdown(f"""
                <div class="gazette-body">
                    <div class="gazette-title">The Sovereign {st.session_state.ticker} Gazette</div>
                    <div class="column-wrapper">
                        <p><span class="dropcap">{ai_story[0] if ai_story else 'T'}</span>{ai_story[1:] if ai_story else 'Silent wires.'}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"SYSTEM_HALTED: {e}")
