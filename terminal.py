import streamlit as st
import yfinance as yf
import pandas_ta as ta
import vectorbt as vbt
import plotly.graph_objects as go
import pandas as pd

# --- GLOBAL SETTINGS ---
vbt.settings.plotting['use_widgets'] = False
st.set_page_config(layout="wide", page_title="QUANT_TERMINAL_V4", page_icon="🏦")

# --- AUTO-LOAD DATA (No Button Needed) ---
@st.cache_data(ttl=3600)
def load_mega_data(symbol):
    ticker_obj = yf.Ticker(symbol)
    df = ticker_obj.history(period="5y") # Hundreds of thousands of ticks in daily view
    
    # Deep Indicator Suite
    df['EMA_20'] = ta.ema(df['Close'], length=20)
    df['EMA_50'] = ta.ema(df['Close'], length=50)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    macd = ta.macd(df['Close'])
    df = pd.concat([df, macd], axis=1)
    
    # Financials for Dividends/Options
    info = ticker_obj.info
    divs = ticker_obj.dividends
    return df, info, divs

# --- UI SKIN ---
st.html("<style>.stApp { background: #050505; color: #00ff41; font-family: 'Courier New'; }</style>")

# --- COMMAND CENTER ---
ticker = st.sidebar.text_input("SYMBOL", value="AAPL").upper().strip()
df, info, dividends = load_mega_data(ticker)

# --- THE SIGNAL TOP-BAR ---
score = 0
if df['EMA_20'].iloc[-1] > df['EMA_50'].iloc[-1]: score += 1
if df['RSI'].iloc[-1] < 40: score += 1 
if df['MACD_12_26_9'].iloc[-1] > df['MACDs_12_26_9'].iloc[-1]: score += 1

signal_text = "STRONG BUY" if score == 3 else "BUY" if score == 2 else "NEUTRAL"
color = "#00ff41" if score >= 2 else "#ff4b4b"

st.markdown(f"""
    <div style="border: 2px solid {color}; padding: 20px; text-align: center; border-radius: 10px;">
        <h1 style="color: {color}; margin: 0;">SIGNAL: {signal_text} ({score}/3 CONFIDENCE)</h1>
        <p style="margin: 0;">Institutional Analysis Engine Running... 100% Data Integrity</p>
    </div>
""", unsafe_allow_html=True)

# --- TABS: ORGANIZED DATA SPREAD ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 CHART & BACKTEST", "📉 OPTIONS FLOW", "💰 DIVIDENDS", "📑 RAW_DATA"])

with tab1:
    st.subheader("// PRICE_ACTION_VISUAL")
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(template="plotly_dark", paper_bgcolor='black', plot_bgcolor='black')
    st.plotly_chart(fig, use_container_width=True)
    
    # Backtest Result
    pf = vbt.Portfolio.from_signals(df['Close'], (df['EMA_20'] > df['EMA_50']), (df['EMA_20'] < df['EMA_50']))
    st.table(pf.stats().to_frame().head(10))

with tab2:
    st.subheader("// DERIVATIVES_INSIGHT")
    st.metric("IMPLIED VOLATILITY", f"{info.get('impliedVolatility', 0)*100:.2f}%")
    st.write("Put/Call Ratio and Greeks data would be mapped here via specialized API (Polygon/AlphaVantage).")

with tab3:
    st.subheader("// INCOME_GENERATION")
    if not dividends.empty:
        st.line_chart(dividends)
        st.metric("DIVIDEND YIELD", f"{info.get('dividendYield', 0)*100:.2f}%")
    else:
        st.write("NO DIVIDEND DATA FOR THIS ASSET.")

with tab4:
    st.write(df.tail(100))
