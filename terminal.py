import streamlit as st
import yfinance as yf
import pandas_ta as ta
import vectorbt as vbt
import plotly.graph_objects as go
import pandas as pd

# --- AUTO-REFRESH & THEME CONFIG ---
vbt.settings.plotting['use_widgets'] = False
st.set_page_config(layout="wide", page_title="PRO-TERMINAL V4", page_icon="📈")

# --- BLOOMBERG CSS OVERRIDE ---
st.markdown("""
    <style>
    .stApp { background-color: #0c0e15; color: #f6f6f6; font-family: 'Space Grotesk', sans-serif; }
    [data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #2962ff; }
    [data-testid="stMetric"] { border: 1px solid #2962ff; padding: 15px; background: #131722; border-radius: 5px; }
    .signal-header { border: 2px solid #2962ff; padding: 20px; text-align: center; border-radius: 10px; margin-bottom: 25px; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR: ADVANCED CUSTOMIZATION ---
with st.sidebar:
    st.header("⚙️ TERMINAL_CONFIG")
    mode = st.radio("UI_COMPLEXITY", ["Simple", "Institutional (Complex)"])
    ticker = st.text_input("ENTER_SYMBOL", value="NVDA").upper().strip()
    
    with st.expander("🛠️ SIGNAL PARAMETERS"):
        rsi_len = st.slider("RSI Length", 7, 21, 14)
        ma_fast = st.number_input("Fast EMA", value=20)
        ma_slow = st.number_input("Slow EMA", value=50)

# --- REACTIVE DATA ENGINE (No Button Needed) ---
@st.cache_data(ttl=3600)
def fetch_mega_data(symbol):
    t = yf.Ticker(symbol)
    df = t.history(period="5y") # Pulling 5 years of historical ticks
    df['EMA_F'] = ta.ema(df['Close'], length=ma_fast)
    df['EMA_S'] = ta.ema(df['Close'], length=ma_slow)
    df['RSI'] = ta.rsi(df['Close'], length=rsi_len)
    return df, t.info, t.dividends, t.options

df, info, dividends, options = fetch_mega_data(ticker)

# --- TOP HUD: AUTOMATED SIGNAL ---
score = 0
if df['EMA_F'].iloc[-1] > df['EMA_S'].iloc[-1]: score += 1
if df['RSI'].iloc[-1] < 45: score += 1
if df['Close'].iloc[-1] > df['EMA_F'].iloc[-1]: score += 1

sig_text = "STRONG BUY" if score == 3 else "BUY" if score == 2 else "NEUTRAL"
sig_color = "#00ff41" if score >= 2 else "#ff4b4b"

st.markdown(f"""<div class='signal-header'><h1 style='color:{sig_color};'>{sig_text} ({score}/3)</h1>
<p>Institutional Algorithm Result | Data Confidence: High</p></div>""", unsafe_allow_html=True)

# --- TABBED LAYOUT (Complex Version) ---
if mode == "Institutional (Complex)":
    tab1, tab2, tab3, tab4 = st.tabs(["📊 ANALYSIS & BACKTEST", "📉 OPTIONS FLOW", "💰 DIVIDENDS/DIVS", "📑 RAW_DATA"])
    
    with tab1:
        st.subheader("// PRICE_ACTION_VISUAL")
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_dark", paper_bgcolor='black', plot_bgcolor='black', height=600)
        st.plotly_chart(fig, use_container_width=True)
        
        # Backtest Report
        pf = vbt.Portfolio.from_signals(df['Close'], (df['EMA_F'] > df['EMA_S']), (df['EMA_F'] < df['EMA_S']))
        st.dataframe(pf.stats().to_frame(), use_container_width=True)

    with tab2:
        st.subheader("// DERIVATIVES_CHAIN")
        st.metric("IMPLIED_VOLATILITY", f"{info.get('impliedVolatility', 0)*100:.2f}%")
        st.write("Current Expiration Dates:", options)

    with tab3:
        st.subheader("// YIELD_DISTRIBUTION")
        if not dividends.empty:
            st.line_chart(dividends)
            st.metric("DIVIDEND_YIELD", f"{info.get('dividendYield', 0)*100:.2f}%")
        else:
            st.info("No Dividends Recorded for this Asset.")

    with tab4:
        st.dataframe(df.tail(500), use_container_width=True)

else:
    # Simple Mode Logic
    st.line_chart(df['Close'])
    st.metric("Price", f"${df['Close'].iloc[-1]:.2f}")
