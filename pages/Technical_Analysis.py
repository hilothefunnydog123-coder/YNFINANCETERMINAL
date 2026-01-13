import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. SETUP & STYLE
st.set_page_config(layout="wide", page_title="TECH_COMMAND_2026")

st.markdown("""
<style>
    [data-testid="stAppViewBlockContainer"] { padding-top: 1rem; max-width: 98% !important; }
    .signal-card { 
        background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(0, 255, 65, 0.2); 
        padding: 15px; border-radius: 12px; margin-bottom: 20px;
    }
    .status-glow { color: #00ff41; text-shadow: 0 0 8px #00ff41; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)

st.markdown(f"<h1 style='color:#00ff41; font-family:monospace;'>// TECH_ANALYSIS: {ticker}</h1>", unsafe_allow_html=True)

# 2. DATA ACQUISITION & QUANT CALCS
with st.spinner("CALCULATING_MOMENTUM_SIGNALS..."):
    # Fetch 1 year of data for context
    df = stock.history(period="1y")
    
    # Calculate RSI (14-period standard)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    
    # Calculate MACD
    macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
    df = pd.concat([df, macd], axis=1)

# 3. MAJESTIC MULTI-PANE CHART
# Row 1: Price | Row 2: MACD | Row 3: RSI
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                    vertical_spacing=0.03, 
                    row_heights=[0.5, 0.25, 0.25])

# Pane 1: Candlesticks
fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price'), row=1, col=1)

# Pane 2: MACD
fig.add_trace(go.Bar(x=df.index, y=df['MACDh_12_26_9'], name='Histogram', marker_color='grey', opacity=0.5), row=2, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['MACD_12_26_9'], name='MACD', line=dict(color='#00f0ff', width=2)), row=2, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['MACDs_12_26_9'], name='Signal', line=dict(color='#ff4b4b', width=2)), row=2, col=1)

# Pane 3: RSI
fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='#00ff41', width=2)), row=3, col=1)
fig.add_hline(y=70, line_dash="dot", line_color="red", annotation_text="OVERBOUGHT", row=3, col=1)
fig.add_hline(y=30, line_dash="dot", line_color="green", annotation_text="OVERSOLD", row=3, col=1)

fig.update_layout(template="plotly_dark", height=800, showlegend=False, 
                  xaxis_rangeslider_visible=False, margin=dict(l=10,r=10,t=10,b=10))
st.plotly_chart(fig, use_container_width=True)

# 4. THE AI INTERPRETATION (Metric Cards)
c1, c2, c3 = st.columns(3)
latest_rsi = df['RSI'].iloc[-1]
latest_macd = df['MACD_12_26_9'].iloc[-1]
latest_sig = df['MACDs_12_26_9'].iloc[-1]

with c1:
    rsi_status = "OVERBOUGHT" if latest_rsi > 70 else "OVERSOLD" if latest_rsi < 30 else "NEUTRAL"
    st.metric("RSI_14_PERIOD", f"{latest_rsi:.2f}", rsi_status, delta_color="inverse")

with c2:
    macd_delta = latest_macd - latest_sig
    macd_status = "BULLISH_CROSS" if macd_delta > 0 else "BEARISH_CROSS"
    st.metric("MACD_DIVERGENCE", f"{latest_macd:.4f}", macd_status)

with c3:
    # A quick "Trend Power" calculation
    st.markdown("<div class='signal-card'>", unsafe_allow_html=True)
    st.markdown(f"<b>ORACLE_TREND:</b> The signal currently reads <span class='status-glow'>{'ACCELERATING' if macd_delta > 0 else 'COOLING'}</span>. RSI suggests the move is {rsi_status.lower()}.</div>", unsafe_allow_html=True)
