import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime
import google.generativeai as genai 

# --- 0. MASTER KEY LOCK ---
GEMINI_API_KEY = "AIzaSyAkGNUAYZXnPD83MFq2SAFqzq_fmNWCIqI"

# --- 1. MAJESTIC UI & DYNAMIC TICKER ---
st.set_page_config(layout="wide", page_title="SOVEREIGN_V38_STABLE", initial_sidebar_state="collapsed")

if 'ticker' not in st.session_state: st.session_state.ticker = "NVDA"
if 'active_layers' not in st.session_state: st.session_state.active_layers = ["EMA"]

tickers_list = ["NVDA", "BTC-USD", "AAPL", "ETH-USD", "TSLA", "AMZN", "MSFT", "META", "GOOGL", "SOL-USD", "SPY", "QQQ", "GLD", "VIX", "GC=F", "USO"]

@st.cache_data(ttl=60)
def get_marquee_html(tickers):
    html_parts = []
    for t in tickers:
        try:
            p = yf.Ticker(t).fast_info['lastPrice']
            html_parts.append(f"<span style='color:#00ff41; padding-right:100px;'>{t}: ${p:,.2f}</span>")
        except:
            html_parts.append(f"<span style='color:#ff00ff; padding-right:100px;'>{t}: OFFLINE</span>")
    return "".join(html_parts)

ticker_content = get_marquee_html(tickers_list)

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
    .stApp {{ background: radial-gradient(circle at top, #050a0f 0%, #000000 100%); color: #00ff41; font-family: 'Courier New', monospace; }}
    @keyframes marquee {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
    .led-ticker {{ background: rgba(0,0,0,0.95); border-bottom: 2px solid #00ff41; padding: 22px; overflow: hidden; white-space: nowrap; width: 100%; font-weight: bold; font-size: 28px; font-family: 'Orbitron', sans-serif; }}
    .led-ticker div {{ display: inline-block; animation: marquee 45s linear infinite; }}
    .gazette-body {{ border: 8px double #00ff41; padding: 60px; background: #000; color: #00ff41; margin-top: 30px; box-shadow: 0 0 50px rgba(0,255,65,0.2); }}
    .gazette-title {{ font-family: 'Orbitron', sans-serif; font-size: 80px; text-align: center; text-transform: uppercase; border-bottom: 10px solid #00ff41; padding-bottom: 10px; line-height: 0.9; }}
    .gazette-sub {{ border-bottom: 3px solid #00ff41; display: flex; justify-content: space-between; padding: 10px 0; margin-bottom: 30px; font-weight: bold; font-size: 18px; }}
    .column-wrapper {{ column-count: 2; column-gap: 50px; text-align: justify; line-height: 1.8; }}
    .dropcap {{ float: left; font-size: 85px; line-height: 65px; padding-right: 15px; font-weight: bold; color: #00ff41; }}
    </style>
    <div class="led-ticker"><div>{ticker_content} | {ticker_content}</div></div>
""", unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
@st.cache_data(ttl=600)
def fetch_master_data(ticker):
    s = yf.Ticker(ticker)
    df = s.history(period="2y")
    df['EMA20'] = ta.ema(df['Close'], length=20)
    df['EMA50'] = ta.ema(df['Close'], length=50)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    # Filter news objects to ensure titles exist
    news = [n for n in s.news if 'title' in n] if s.news else []
    return df, s.info, s.quarterly_financials, s.options, news

try:
    df, info, financials, opt_dates, live_news = fetch_master_data(st.session_state.ticker)
    l, c, r = st.columns([1, 4.8, 1.2])

    with l:
        st.markdown("### // HUD_ACTIVE")
        st.metric("SPOT_PRICE", f"${df['Close'].iloc[-1]:,.2f}")
        st.metric("MOMENTUM_RSI", f"{df['RSI'].iloc[-1]:.1f}")
        if st.button("TOGGLE EMA_CROSS"):
            st.session_state.active_layers.append("EMA") if "EMA" not in st.session_state.active_layers else st.session_state.active_layers.remove("EMA")
        if st.button("TOGGLE RSI_PANE"):
            st.session_state.active_layers.append("RSI") if "RSI" not in st.session_state.active_layers else st.session_state.active_layers.remove("RSI")

    with r:
        st.markdown("### // QUANT_PINE")
        st.text_area("CODE", height=200, label_visibility="collapsed")
        st.button("EXECUTE_LOGIC")

    with c:
        t_in = st.text_input("SYMBOL", value=st.session_state.ticker, label_visibility="collapsed").upper().strip()
        if t_in != st.session_state.ticker:
            st.session_state.ticker = t_in
            st.rerun()

        tabs = st.tabs(["📊 ANALYSIS", "📈 GEX_PROFILE", "📉 OPTIONS", "💰 FINANCIALS", "📰 THE_SOVEREIGN_GAZETTE"])

        with tabs[0]:
            rows = 2 if "RSI" in st.session_state.active_layers else 1
            fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3] if rows==2 else [1.0], vertical_spacing=0.05)
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']), row=1, col=1)
            if "EMA" in st.session_state.active_layers:
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name="EMA20", line=dict(color="#00ff41")))
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], name="EMA50", line=dict(color="#ff00ff")))
            fig.update_layout(template="plotly_dark", height=750, xaxis_rangeslider_visible=False, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)

        with tabs[1]:
            # Gamma Wall logic
            if opt_dates:
                chain = yf.Ticker(st.session_state.ticker).option_chain(opt_dates[0])
                gex_fig = go.Figure()
                gex_fig.add_trace(go.Bar(x=chain.calls['strike'], y=chain.calls['openInterest'], name="Calls", marker_color='#00ff41'))
                gex_fig.add_trace(go.Bar(x=chain.puts['strike'], y=-chain.puts['openInterest'], name="Puts", marker_color='#ff00ff'))
                gex_fig.update_layout(barmode='relative', template="plotly_dark", title="Gamma Exposure Profile")
                st.plotly_chart(gex_fig, use_container_width=True)
                
        with tabs[2]:
            st.subheader("// OPTIONS_CHAIN_LOCKED")
            if opt_dates:
                # Fixed: Pulling chain for the nearest available expiry
                chain = yf.Ticker(st.session_state.ticker).option_chain(opt_dates[0])
                st.dataframe(chain.calls, use_container_width=True, height=600)
            else:
                st.info("NO_DERIVATIVES_DATA_FOUND")

        with tabs[3]:
            # Locked Financials Logic
            if financials is not None and not financials.empty:
                rev_fig = go.Figure(data=[go.Bar(x=financials.columns, y=financials.iloc[0], marker_color='#00ff41')])
                rev_fig.update_layout(template="plotly_dark", title="Quarterly Revenue Matrix")
                st.plotly_chart(rev_fig, use_container_width=True)
                st.dataframe(financials, use_container_width=True)
                
        with tabs[4]:
            # --- AI GHOSTWRITER FIXED (Clean HTML Rendering) ---
            ai_story = ""
            if GEMINI_API_KEY:
                try:
                    genai.configure(api_key=GEMINI_API_KEY)
                    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    target_model = available_models[0] if available_models else "gemini-1.5-flash"
                    model_engine = genai.GenerativeModel(target_model)
                    
                    # Ingest real headlines
                    h_list = "\n".join([f"- {n['title']}" for n in live_news[:5]]) if live_news else "Tape silent."
                    prompt = (f"Write a snarky, humorous institutional Wall Street newspaper article for {st.session_state.ticker}. "
                              f"Data: Price ${df['Close'].iloc[-1]:.2f}, RSI {df['RSI'].iloc[-1]:.1f}. "
                              f"Headlines: {h_list}. Use financial slang and mention 'retail bagholders'.")
                    
                    response = model_engine.generate_content(prompt)
                    ai_story = response.text.replace("*", "").replace("#", "") # Clean AI markdown artifacts
                except Exception as e:
                    ai_story = f"SYSTEM_ERROR: The Ghostwriter was detained by the SEC. ({e})"
            
            # Rendering Gazette as a single cohesive block
            newspaper_html = f"""
            <div class="gazette-body">
                <div class="gazette-title">The {st.session_state.ticker} Global Gazette</div>
                <div class="gazette-sub">
                    <span>PRICE: ${df['Close'].iloc[-1]:.2f}</span>
                    <span>{datetime.now().strftime('%B %d, %Y')}</span>
                    <span>SENTIMENT: GEMINI_SENTIENT</span>
                </div>
                <div class="column-wrapper">
                    <p><span class="dropcap">{ai_story[0] if ai_story else 'T'}</span>{ai_story[1:] if ai_story else 'The wires are cold.'}</p>
                </div>
            </div>
            """
            st.markdown(newspaper_html, unsafe_allow_html=True)

except Exception as e:
    st.error(f"SYSTEM_HALTED: {e}")
