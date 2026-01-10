import streamlit as st
import yfinance as yf
import pandas_ta as ta
import vectorbt as vbt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# --- 1. SYSTEM CONFIG ---
vbt.settings.plotting['use_widgets'] = False
st.set_page_config(layout="wide", page_title="PRO-QUANT_V8_ULTRA")

# --- 2. THE "MATRIX" LED TICKER ---
ticker_data = [{"s": "NVDA", "p": "124.50", "c": "+2.4%"}, {"s": "BTC-USD", "p": "64,210", "c": "+1.2%"}]
ticker_string = " | ".join([f"{x['s']}: {x['p']} ({x['c']})" for x in ticker_data])
st.html(f"<div style='background:#050505;color:#00ff41;padding:10px;overflow:hidden;white-space:nowrap;font-weight:bold;border-bottom:2px solid #333;'><marquee scrollamount='5'>{ticker_string} | {ticker_string} | {ticker_string}</marquee></div>")

# --- 3. SESSION STATE ENGINE ---
if 'active_layers' not in st.session_state: st.session_state.active_layers = []
if 'ticker' not in st.session_state: st.session_state.ticker = "NVDA"

# --- 4. DEEP DATA ENGINE (Fixed Fundamentals) ---
@st.cache_data(ttl=3600)
def load_mega_data(ticker):
    s = yf.Ticker(ticker)
    df = s.history(period="5y", auto_adjust=True)
    
    # Technicals
    df['EMA20'] = ta.ema(df['Close'], length=20)
    df['EMA50'] = ta.ema(df['Close'], length=50)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    
    # Fundamentals
    stats = s.info
    financials = s.quarterly_financials
    balance = s.quarterly_balance_sheet
    return df, stats, financials, balance

try:
    df, stats, financials, balance = load_mega_data(st.session_state.ticker)

    # --- 5. THE 3-WING INTERFACE ---
    l, c, r = st.columns([1, 4, 1.2])

    with l:
        st.markdown("### // ANALYSIS_LAYERS")
        if st.button("TOGGLE EMA_CROSS"):
            st.session_state.active_layers.append("EMA") if "EMA" not in st.session_state.active_layers else st.session_state.active_layers.remove("EMA")
        if st.button("TOGGLE RSI_PANE"):
            st.session_state.active_layers.append("RSI") if "RSI" not in st.session_state.active_layers else st.session_state.active_layers.remove("RSI")
        
        st.markdown("---")
        st.metric("MARKET_CAP", f"${stats.get('marketCap', 0):,.0f}")
        st.metric("PE_RATIO", f"{stats.get('trailingPE', 'N/A')}")
        st.metric("52W_HIGH", f"${stats.get('fiftyTwoWeekHigh', 0):,.2f}")

    with r:
        st.markdown("### // PINE_SCRIPT_COMPILER")
        pine_in = st.text_area("PASTE_PINESCRIPT", height=200)
        if st.button("COMPILE_LOGIC"):
            if "ta.rsi" in pine_in.lower(): st.session_state.active_layers.append("RSI")
            if "ta.ema" in pine_in.lower(): st.session_state.active_layers.append("EMA")
            st.toast("Compiling Pine Logic...")

    with c:
        t_in = st.text_input("SET_TICKER", value=st.session_state.ticker).upper()
        if t_in != st.session_state.ticker:
            st.session_state.ticker = t_in
            st.rerun()

        t1, t2, t3 = st.tabs(["📊 CHART_SYSTEM", "📉 OPTION_FLOW", "💰 FINANCIAL_STATEMENTS"])

        with t1:
            # Multi-Pane Plotting
            rows = 2 if "RSI" in st.session_state.active_layers else 1
            fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3] if rows==2 else [1.0])
            
            # Subplot 1: Price
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="PRC"), row=1, col=1)
            if "EMA" in st.session_state.active_layers:
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name="EMA20", line=dict(color="#00ff41")), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], name="EMA50", line=dict(color="#ff4b4b")), row=1, col=1)
            
            # Subplot 2: RSI
            if "RSI" in st.session_state.active_layers:
                fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI", line=dict(color="#2962ff")), row=2, col=1)
                fig.add_hline(y=70, line_dash="dot", line_color="red", row=2, col=1)
                fig.add_hline(y=30, line_dash="dot", line_color="green", row=2, col=1)

            fig.update_layout(template="plotly_dark", height=700, paper_bgcolor='black', plot_bgcolor='black', xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with t2:
            st.subheader("// DEEP_OPTION_CHAIN")
            opts = yf.Ticker(st.session_state.ticker).option_chain(yf.Ticker(st.session_state.ticker).options[0])
            st.dataframe(opts.calls, use_container_width=True)

        with t3:
            st.subheader("// QUARTERLY_FINANCIALS")
            # This pulls 100+ points from Income Statement and Balance Sheet
            st.markdown("#### INCOME_STATEMENT")
            st.dataframe(financials, use_container_width=True)
            st.markdown("#### BALANCE_SHEET")
            st.dataframe(balance, use_container_width=True)

except Exception as e:
    st.error(f"SYSTEM_HALTED: {e}")
