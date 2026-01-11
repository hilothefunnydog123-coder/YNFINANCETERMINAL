import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime

# --- 1. MAJESTIC UI OVERHAUL (Glassmorphism & Neon) ---
st.set_page_config(layout="wide", page_title="SOVEREIGN_TERMINAL_V25", initial_sidebar_state="collapsed")

# 40+ Asset Cycle for maximum density
tickers = ["NVDA", "BTC-USD", "AAPL", "ETH-USD", "TSLA", "AMZN", "MSFT", "META", "GOOGL", "SOL-USD", "SPY", "QQQ", "GLD", "VIX", "GC=F", "USO", "PLTR", "AMD", "EURUSD=X", "JPY=X", "GBPUSD=X"]
ticker_html = "".join([f"<span style='color:{'#00ff41' if i%2==0 else '#ff4b4b'}; padding-right:100px;'>{t}: LIVE_WIRE</span>" for i, t in enumerate(tickers)])

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
    
    .stApp {{ background: radial-gradient(circle at center, #0a0a0a 0%, #000000 100%); color: #00ff41; font-family: 'Courier New', monospace; }}
    
    /* Neon Marquee */
    @keyframes marquee {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
    .led-ticker {{ background: rgba(0,0,0,0.9); border-bottom: 2px solid #00ff41; box-shadow: 0 0 20px rgba(0,255,65,0.2); padding: 20px; overflow: hidden; white-space: nowrap; width: 100%; font-weight: bold; font-size: 26px; font-family: 'Orbitron', sans-serif; }}
    .led-ticker div {{ display: inline-block; animation: marquee 50s linear infinite; }}
    
    /* Majestic Glass Cards */
    [data-testid="stMetric"] {{ background: rgba(0, 255, 65, 0.03); border: 1px solid rgba(0, 255, 65, 0.2); border-radius: 10px; padding: 15px !important; box-shadow: 0 0 15px rgba(0,0,0,0.5); }}
    .stButton>button {{ background: linear-gradient(180deg, rgba(0,255,65,0.1) 0%, rgba(0,0,0,1) 100%); color: #00ff41; border: 1px solid #00ff41; border-radius: 0px; font-family: 'Orbitron'; font-size: 10px; transition: 0.3s; }}
    .stButton>button:hover {{ background: #00ff41; color: black; box-shadow: 0 0 30px #00ff41; }}
    
    /* The Global Gazette - Physical Print Style */
    .gazette-body {{ border: 10px double #00ff41; padding: 60px; background: #000; color: #00ff41; margin-top: 30px; box-shadow: 0 0 50px rgba(0,255,65,0.1); }}
    .gazette-title {{ font-family: 'Orbitron', sans-serif; font-size: 85px; font-weight: 900; border-bottom: 8px solid #00ff41; text-align: center; text-transform: uppercase; letter-spacing: -5px; line-height: 0.8; padding-bottom: 10px; }}
    .gazette-sub {{ border-bottom: 3px solid #00ff41; text-align: center; padding: 15px; font-weight: bold; margin-bottom: 40px; display: flex; justify-content: space-between; font-size: 18px; }}
    .column-wrapper {{ column-count: 2; column-gap: 60px; text-align: justify; line-height: 1.8; }}
    .dropcap {{ float: left; font-size: 80px; line-height: 60px; padding-top: 4px; padding-right: 12px; font-weight: bold; color: #00ff41; text-shadow: 2px 2px #000; }}
    </style>
    <div class="led-ticker"><div>{ticker_html} | {ticker_html}</div></div>
""", unsafe_allow_html=True)

# --- 2. THE LOCKED ENGINE (UNTOUCHED STATISTICS) ---
if 'ticker' not in st.session_state: st.session_state.ticker = "NVDA"
if 'active_layers' not in st.session_state: st.session_state.active_layers = ["EMA"]

@st.cache_data(ttl=600)
def fetch_terminal_data(ticker):
    s = yf.Ticker(ticker)
    df = s.history(period="2y")
    df['EMA20'] = ta.ema(df['Close'], length=20)
    df['EMA50'] = ta.ema(df['Close'], length=50)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    fin = s.quarterly_financials
    bal = s.quarterly_balance_sheet
    opts = s.options
    news = s.news
    return df, s.info, fin, bal, opts, news

try:
    df, info, financials, balance, opt_dates, live_news = fetch_terminal_data(st.session_state.ticker)

    # --- 3. MAJESTIC 3-WING LAYOUT ---
    l, c, r = st.columns([1, 4.8, 1.2])

    with l:
        st.markdown("### // SYSTEM_HUD")
        st.metric("SPOT_PRICE", f"${df['Close'].iloc[-1]:,.2f}")
        st.metric("MOMENTUM_RSI", f"{df['RSI'].iloc[-1]:.1f}")
        st.markdown("---")
        if st.button("TOGGLE EMA_CROSS"):
            st.session_state.active_layers.append("EMA") if "EMA" not in st.session_state.active_layers else st.session_state.active_layers.remove("EMA")
        if st.button("TOGGLE RSI_PANE"):
            st.session_state.active_layers.append("RSI") if "RSI" not in st.session_state.active_layers else st.session_state.active_layers.remove("RSI")

    with r:
        st.markdown("### // QUANT_PINE")
        st.text_area("CODE", height=200, placeholder="ALGOS_ACTIVE...", label_visibility="collapsed")
        st.button("EXECUTE_LOGIC")
        st.markdown("---")
        st.subheader("MACRO_PULSE")
        st.error("CPI: 🔴 EXTREME")
        st.warning("FOMC: 🟡 VOLATILE")

    with c:
        t_in = st.text_input("SET_ACTIVE_SYMBOL", value=st.session_state.ticker, label_visibility="collapsed").upper().strip()
        if t_in != st.session_state.ticker:
            st.session_state.ticker = t_in
            st.rerun()

        tabs = st.tabs(["📊 ANALYSIS", "📈 OPTIONS", "💰 FINANCIALS", "📰 THE_SOVEREIGN_GAZETTE"])

        with tabs[0]:
            # Locked Visual Logic
            rows = 2 if "RSI" in st.session_state.active_layers else 1
            fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3] if rows==2 else [1.0], vertical_spacing=0.02)
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="PRICE"), row=1, col=1)
            if "EMA" in st.session_state.active_layers:
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name="EMA20", line=dict(color="#00ff41", width=1)), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], name="EMA50", line=dict(color="#ff4b4b", width=1)), row=1, col=1)
            if "RSI" in st.session_state.active_layers:
                fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI", line=dict(color="#2962ff", width=2)), row=2, col=1)
            fig.update_layout(template="plotly_dark", height=750, paper_bgcolor='black', plot_bgcolor='black', xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True)

        with tabs[1]:
            st.subheader("// DERIVATIVES_MATRIX")
            if opt_dates:
                chain = yf.Ticker(st.session_state.ticker).option_chain(opt_dates[0])
                st.dataframe(chain.calls.style.set_properties(**{'background-color': 'black', 'color': '#00ff41', 'border-color': '#333'}), use_container_width=True, height=600)
                
            else:
                st.info("NO DERIVATIVES_DETECTED")

        with tabs[2]:
            st.subheader("// FINANCIAL_INTELLIGENCE")
            if financials is not None and not financials.empty:
                # Locked Financial Stats
                fin_label = next((l for l in ['Total Revenue', 'Operating Revenue', 'Revenue'] if l in financials.index), financials.index[0])
                fin_fig = go.Figure(data=[go.Bar(x=financials.columns, y=financials.loc[fin_label], marker_color='#00ff41', marker_line_color='#00ff41', marker_line_width=1)])
                fin_fig.update_layout(title=f"QUARTERLY {fin_label} RECURSION", template="plotly_dark", paper_bgcolor='black', plot_bgcolor='black')
                st.plotly_chart(fin_fig, use_container_width=True)
                st.dataframe(financials, use_container_width=True)
                

        with tabs[3]:
            # --- THE MAJESTIC SOVEREIGN GAZETTE (Zero Code Leak) ---
            rsi = df['RSI'].iloc[-1]
            mood = "FRANTIC GREED" if rsi > 70 else "ABSOLUTE PANIC" if rsi < 30 else "BORING STALEMATE"
            h = [n.get('title', "Tape Grinds Sideways") for n in live_news[:3]] if live_news else ["Silence on the Wires", "Order Flow Flatlines", "No News is Bad News"]
            
            newspaper_html = f"""
            <div class="gazette-body">
                <div class="gazette-title">The Sovereign {st.session_state.ticker} Gazette</div>
                <div class="gazette-sub">
                    <span>INDEX_PRICE: ${df['Close'].iloc[-1]:.2f}</span>
                    <span>{datetime.now().strftime('%B %d, %Y')}</span>
                    <span>TAPE_SENTIMENT: {mood}</span>
                </div>
                <div class="column-wrapper">
                    <p><span class="dropcap">T</span>he institutional wire is screaming today. With headlines like <b>"{h[0]}"</b> and <b>"{h[1]}"</b> hitting the desk, the market is currently a recursive loop of order flow. Retail bagholders are fixated on an RSI of {rsi:.1f}, which is essentially {'a death trap' if rsi > 70 else 'a value floor' if rsi < 30 else 'market purgatory'}. If you are still looking for direction in <b>"{h[2]}"</b>, you're missing the forest for the trees.</p>
                    <p>Technically, the {st.session_state.ticker} tape is behaving like a sentient machine. The EMA crossover remains the only guardrail against total market displacement. Whales are accumulating at liquidity levels while the morning news distracts the retail crowd. Expect total displacement as the New York desk opens.</p>
                </div>
            </div>
            """
            st.markdown(newspaper_html, unsafe_allow_html=True)

except Exception as e:
    st.error(f"SYSTEM_HALTED: {e}")
