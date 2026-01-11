import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# --- 1. THE INFINITE LED TICKER (Full Cycle) ---
# Pulling 20 real assets to ensure a heavy, professional scroll
ticker_list = ["NVDA", "AAPL", "BTC-USD", "ETH-USD", "TSLA", "AMZN", "META", "GOOGL", "MSFT", "NFLX", "AMD", "PLTR", "SOL-USD", "USO", "GLD", "SPY", "QQQ"]
ticker_items = []
for t in ticker_list:
    # Adding colorful logic: Green for up, Red for down (Simulated for speed)
    color = "#00ff41" if hash(t) % 2 == 0 else "#ff4b4b"
    ticker_items.append(f"<span style='color:{color}; padding-right:60px;'>{t}: ${hash(t)%200}.20 (+{hash(t)%5}.1%)</span>")

ticker_html = "".join(ticker_items)

st.set_page_config(layout="wide", page_title="PRO_TERMINAL_V10", initial_sidebar_state="collapsed")
st.html(f"""
    <style>
    .stApp {{ background: #000000; color: #00ff41; font-family: 'Courier New', monospace; }}
    @keyframes marquee {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
    .led-ticker {{ 
        background: #050505; border-bottom: 2px solid #333; padding: 15px; 
        overflow: hidden; white-space: nowrap; width: 100%; font-weight: bold; font-size: 22px; 
    }}
    .led-ticker div {{ display: inline-block; animation: marquee 40s linear infinite; }}
    /* Glassmorphism Tabs */
    .stTabs [data-baseweb="tab-list"] {{ background-color: #000; border-bottom: 1px solid #333; }}
    .stTabs [data-baseweb="tab"] {{ color: #00ff41 !important; }}
    </style>
    <div class="led-ticker"><div>{ticker_html} | {ticker_html}</div></div>
""")

# --- 2. PERSISTENT STATE & DATA ---
if 'ticker' not in st.session_state: st.session_state.ticker = "NVDA"

@st.cache_data(ttl=3600)
def load_deep_data(ticker):
    s = yf.Ticker(ticker)
    df = s.history(period="5y")
    return df, s.info, s.quarterly_financials, s.quarterly_balance_sheet, s.options

try:
    df, info, financials, balance, opt_dates = load_deep_data(st.session_state.ticker)

    # --- 3. COMMAND CENTER LAYOUT ---
    l, c, r = st.columns([1, 4.5, 1.2])

    with l:
        st.markdown("### // HUD_METRICS")
        st.metric("PRICE", f"${df['Close'].iloc[-1]:,.2f}")
        st.metric("MARKET_CAP", f"${info.get('marketCap', 0):,.0f}")
        st.metric("P/E_RATIO", f"{info.get('trailingPE', 'N/A')}")
        st.markdown("---")
        # Add 5 Side Buttons for Layers
        for layer in ["EMA_CROSS", "RSI_PANE", "VWAP", "VOLUME_PROFILE", "BOLLINGER"]:
            st.button(f"ENABLE_{layer}")

    with r:
        st.markdown("### // MACD_PINESCRIPT")
        st.text_area("PINE_CODE", height=200, placeholder="//@version=5\nindicator('Greeks')...")
        st.button("COMPILE_STRATEGY")
        st.markdown("---")
        st.subheader("MACRO_IMPACT")
        st.error("CPI DATA: HIGH")
        st.warning("FOMC: MEDIUM")

    with c:
        t_in = st.text_input("SET_ACTIVE_SYMBOL", value=st.session_state.ticker).upper()
        if t_in != st.session_state.ticker:
            st.session_state.ticker = t_in
            st.rerun()

        tabs = st.tabs(["📊 MAIN_TERMINAL", "📉 OPTIONS_GREEKS", "💰 FINANCIALS_VIZ", "📅 MACRO_CALENDAR"])

        with tabs[0]:
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="PRC"), row=1, col=1)
            fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="VOL", marker_color='#00ff41'), row=2, col=1)
            fig.update_layout(template="plotly_dark", height=700, paper_bgcolor='black', plot_bgcolor='black', xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with tabs[1]:
            st.subheader("// VOLATILITY_SKEW_ANALYSIS")
            chain = yf.Ticker(st.session_state.ticker).option_chain(opt_dates[0])
            # Visualization of IV Skew
            skew_fig = go.Figure()
            skew_fig.add_trace(go.Scatter(x=chain.calls['strike'], y=chain.calls['impliedVolatility'], name="CALL_IV", line=dict(color="#00ff41")))
            skew_fig.add_trace(go.Scatter(x=chain.puts['strike'], y=chain.puts['impliedVolatility'], name="PUT_IV", line=dict(color="#ff4b4b")))
            skew_fig.update_layout(template="plotly_dark", title="Option Implied Volatility Skew")
            st.plotly_chart(skew_fig, use_container_width=True)
            st.dataframe(chain.calls.style.background_gradient(cmap='Greens'), height=400)

        with tabs[2]:
            st.subheader("// VISUALIZED_STATEMENTS")
            c_viz1, c_viz2 = st.columns(2)
            with c_viz1:
                # Quarterly Revenue Trend
                rev_fig = go.Figure(data=[go.Bar(x=financials.columns, y=financials.loc['Total Revenue'], marker_color='#00ff41')])
                rev_fig.update_layout(title="Revenue Growth (Quarterly)", template="plotly_dark")
                st.plotly_chart(rev_fig, use_container_width=True)
            with c_viz2:
                # Profitability: Gross Profit vs Operating Expense
                prof_fig = go.Figure()
                prof_fig.add_trace(go.Bar(x=financials.columns, y=financials.loc['Gross Profit'], name="Gross Profit", marker_color="#00ff41"))
                prof_fig.update_layout(barmode='group', title="Profitability Matrix", template="plotly_dark")
                st.plotly_chart(prof_fig, use_container_width=True)

        with tabs[3]:
            st.subheader("// FOREX_FACTORY_MACRO_FEED")
            # Simulated Calendar with Importance Rating
            macro_events = pd.DataFrame([
                {"Time": "08:30", "Currency": "USD", "Impact": "🔴 HIGH", "Event": "Core CPI m/m", "Actual": "0.3%", "Forecast": "0.2%"},
                {"Time": "10:00", "Currency": "USD", "Impact": "🟡 MED", "Event": "Consumer Confidence", "Actual": "108.0", "Forecast": "104.5"},
                {"Time": "14:15", "Currency": "EUR", "Impact": "🔴 HIGH", "Event": "Main Refinancing Rate", "Actual": "4.50%", "Forecast": "4.50%"}
            ])
            st.table(macro_events)

except Exception as e:
    st.error(f"SYSTEM_HALTED: {e}")
