import streamlit as st
import yfinance as yf
import pandas_ta as ta
import vectorbt as vbt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# --- 1. BLOOMBERG LED MARQUEE (Animated & Colorful) ---
ticker_data = [
    {"s": "NVDA", "p": "124.50", "c": "+2.4%", "clr": "#00ff41"}, {"s": "BTC-USD", "p": "64,210", "c": "+1.2%", "clr": "#00ff41"},
    {"s": "AAPL", "p": "214.20", "c": "-0.4%", "clr": "#ff4b4b"}, {"s": "TSLA", "p": "210.10", "c": "+5.1%", "clr": "#00ff41"},
    {"s": "ETH-USD", "p": "3,450", "c": "-0.8%", "clr": "#ff4b4b"}, {"s": "AMZN", "p": "189.30", "c": "+0.9%", "clr": "#00ff41"}
]
ticker_html = "".join([f"<span style='color:{x['clr']}; padding-right:50px;'>{x['s']}: {x['p']} ({x['c']})</span>" for x in ticker_data])

st.set_page_config(layout="wide", page_title="TERMINAL_ULTRA_V9")
st.html(f"""
    <style>
    .stApp {{ background: #000000; color: #00ff41; font-family: 'Courier New', monospace; }}
    @keyframes marquee {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
    .led-ticker {{ background: #050505; border-bottom: 2px solid #333; padding: 12px; overflow: hidden; white-space: nowrap; width: 100%; font-weight: bold; font-size: 20px; }}
    .led-ticker div {{ display: inline-block; animation: marquee 25s linear infinite; }}
    .stButton>button {{ background: transparent; color: #00ff41; border: 1px solid #00ff41; font-size: 11px; width: 100%; height: 35px; text-transform: uppercase; }}
    .stButton>button:hover {{ background: #00ff41; color: black; box-shadow: 0 0 15px #00ff41; }}
    </style>
    <div class="led-ticker"><div>{ticker_html} | {ticker_html}</div></div>
""")

# --- 2. PERSISTENT STATE ---
if 'active_layers' not in st.session_state: st.session_state.active_layers = []
if 'ticker' not in st.session_state: st.session_state.ticker = "NVDA"

# --- 3. DEEP DATA ENGINE (Options & Fundamentals) ---
@st.cache_data(ttl=3600)
def load_institutional_data(ticker):
    s = yf.Ticker(ticker)
    df = s.history(period="5y", auto_adjust=True)
    df['EMA20'] = ta.ema(df['Close'], length=20)
    df['EMA50'] = ta.ema(df['Close'], length=50)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    return df, s.info, s.quarterly_financials, s.quarterly_balance_sheet, s.options

try:
    df, info, financials, balance, opt_dates = load_institutional_data(st.session_state.ticker)

    # --- 4. 3-WING INTERFACE ---
    l, c, r = st.columns([1, 4, 1.2])

    with l:
        st.markdown("### // ANALYSIS_CTRL")
        if st.button("EMA_CROSS"): st.session_state.active_layers.append("EMA") if "EMA" not in st.session_state.active_layers else st.session_state.active_layers.remove("EMA")
        if st.button("RSI_OSCILLATOR"): st.session_state.active_layers.append("RSI") if "RSI" not in st.session_state.active_layers else st.session_state.active_layers.remove("RSI")
        st.markdown("---")
        st.metric("MARKET_CAP", f"${info.get('marketCap', 0):,.0f}")
        st.metric("P/E_RATIO", f"{info.get('trailingPE', 'N/A')}")
        st.metric("INSTITUTIONAL_HOLD", f"{info.get('heldPercentInstitutions', 0)*100:.1f}%")

    with r:
        st.markdown("### // PINE_SCRIPT_HUB")
        pine_in = st.text_area("CODE_INPUT", height=250, placeholder="//@version=5\nindicator('EMA')...")
        if st.button("EXECUTE_PINE"):
            if "ta.rsi" in pine_in.lower(): st.session_state.active_layers.append("RSI")
            st.toast("Syncing Pine Logic to Layers...")

    with c:
        t_in = st.text_input("ACTIVE_SYMBOL", value=st.session_state.ticker).upper()
        if t_in != st.session_state.ticker:
            st.session_state.ticker = t_in
            st.rerun()

        # --- 5. TABS: THE DATA COMMAND CENTER ---
        t1, t2, t3, t4 = st.tabs(["📊 CHART", "📈 OPTIONS_HUB", "💰 FINANCIALS", "📅 NEWS_MACRO"])

        with t1:
            rows = 2 if "RSI" in st.session_state.active_layers else 1
            fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3] if rows==2 else [1.0])
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="PRC"), row=1, col=1)
            if "EMA" in st.session_state.active_layers:
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name="EMA20", line=dict(color="#00ff41")), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], name="EMA50", line=dict(color="#ff4b4b")), row=1, col=1)
            if "RSI" in st.session_state.active_layers:
                fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI", line=dict(color="#2962ff")), row=2, col=1)
            fig.update_layout(template="plotly_dark", height=700, paper_bgcolor='black', plot_bgcolor='black', xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with t2:
            st.subheader("// OPTIONS_VOLATILITY_SKEW")
            # Fetch Call/Put Skew Visualization
            chain = yf.Ticker(st.session_state.ticker).option_chain(opt_dates[0])
            calls, puts = chain.calls, chain.puts
            
            # Chart: Implied Volatility across Strikes
            fig_iv = go.Figure()
            fig_iv.add_trace(go.Scatter(x=calls['strike'], y=calls['impliedVolatility'], name="Calls IV", line=dict(color="#00ff41")))
            fig_iv.add_trace(go.Scatter(x=puts['strike'], y=puts['impliedVolatility'], name="Puts IV", line=dict(color="#ff4b4b")))
            fig_iv.update_layout(title="Volatility Skew Matrix", template="plotly_dark", height=400)
            st.plotly_chart(fig_iv, use_container_width=True)
            
            st.markdown("#### FULL_DEEP_CHAIN")
            st.dataframe(calls, height=500, use_container_width=True)

        with t3:
            st.subheader("// FINANCIAL_HEALTH_DASHBOARD")
            c_f1, c_f2 = st.columns(2)
            with c_f1:
                # Chart: Quarterly Revenue Growth
                rev_fig = go.Figure(data=[go.Bar(x=financials.columns, y=financials.loc['Total Revenue'], marker_color='#00ff41')])
                rev_fig.update_layout(title="Quarterly Revenue ($)", template="plotly_dark", height=350)
                st.plotly_chart(rev_fig, use_container_width=True)
            with c_f2:
                # Chart: Debt vs Cash
                debt_fig = go.Figure(data=[go.Bar(x=balance.columns, y=balance.loc['Total Debt'], name="Debt", marker_color="#ff4b4b"),
                                           go.Bar(x=balance.columns, y=balance.loc['Cash Cash Equivalents And Short Term Investments'], name="Cash", marker_color="#00ff41")])
                debt_fig.update_layout(title="Debt vs Liquidity ($)", barmode='group', template="plotly_dark", height=350)
                st.plotly_chart(debt_fig, use_container_width=True)
            
            st.markdown("#### RAW_BALANCE_SHEET")
            st.dataframe(balance, height=400, use_container_width=True)

        with t4:
            st.subheader("// GLOBAL_MACRO_CALENDAR (Forex Factory Standard)")
            # Simulated institutional news feed with Importance Ratings
            news_data = [
                {"Event": "US Core CPI m/m", "Impact": "HIGH", "Market": "USD", "Forecast": "0.3%", "Previous": "0.2%"},
                {"Event": "ECB Press Conference", "Impact": "HIGH", "Market": "EUR", "Forecast": "N/A", "Previous": "N/A"},
                {"Event": "Unemployment Claims", "Impact": "MEDIUM", "Market": "USD", "Forecast": "225K", "Previous": "230K"},
                {"Event": "Consumer Confidence", "Impact": "LOW", "Market": "USD", "Forecast": "101.5", "Previous": "100.2"}
            ]
            news_df = pd.DataFrame(news_data)
            
            # Stylizing Impact Colors
            def color_impact(val):
                color = '#ff4b4b' if val == 'HIGH' else '#ffaa00' if val == 'MEDIUM' else '#00ff41'
                return f'color: {color}; font-weight: bold'
            
            st.table(news_df.style.applymap(color_impact, subset=['Impact']))

except Exception as e:
    st.error(f"SYSTEM_CRASH: {e}")
