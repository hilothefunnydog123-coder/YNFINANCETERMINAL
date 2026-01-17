import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. BLOOMBERG UI OVERRIDE ---
st.set_page_config(layout="wide", page_title="TERMINAL_v46", page_icon="📈")

def apply_terminal_theme():
    st.markdown("""
        <style>
        /* Bloomberg Amber and Black Theme */
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
        
        .stApp {
            background-color: #000000;
            color: #efefef;
            font-family: 'Roboto Mono', monospace;
        }

        /* Tighten margins to fit more data */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }

        /* Metric styling: Amber text on dark background */
        [data-testid="stMetricValue"] {
            color: #ff9900 !important;
            font-size: 1.8rem !important;
        }
        
        /* Sidebar styling to look like an instrument panel */
        section[data-testid="stSidebar"] {
            background-color: #111111 !important;
            border-right: 1px solid #333333;
        }

        /* Bloomberg Style Dataframes */
        .stDataFrame {
            border: 1px solid #333333;
        }
        
        /* Header styling */
        .terminal-header {
            color: #00ff00;
            background-color: #1a1a1a;
            padding: 5px 15px;
            border-bottom: 2px solid #333333;
            font-size: 12px;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

apply_terminal_theme()

# --- 2. GLOBAL SESSION STATE ---
if 'ticker' not in st.session_state:
    st.session_state.ticker = "NVDA"

# --- 3. THE COMMAND LINE (Sidebar) ---
with st.sidebar:
    st.markdown("<h2 style='color:#ff9900;'>BLOOMBERG_v46</h2>", unsafe_allow_html=True)
    st.session_state.ticker = st.text_input("COMMAND > ", value=st.session_state.ticker).upper()
    st.markdown("---")
    st.write(f"USER: **YN_ANALYST**")
    st.write(f"LOC: **GLOBAL_CORE**")
    st.write(f"TIME: {datetime.now().strftime('%H:%M:%S')}")

# --- 4. DATA ENGINE (Live Direct Scrape) ---
stock = yf.Ticker(st.session_state.ticker)
hist = stock.history(period="1d", interval="1m")
info = stock.info

# Header Bar
st.markdown(f"""
    <div class="terminal-header">
        SEC: {st.session_state.ticker} | EXCH: {info.get('exchange')} | CUR: {info.get('currency')} | STATUS: <span style="color:#00ff00;">LIVE</span>
    </div>
""", unsafe_allow_html=True)

# --- 5. THE DUAL-MONITOR GRID ---
col_main, col_side = st.columns([3, 1])

with col_main:
    # Top Row Metrics
    m1, m2, m3, m4 = st.columns(4)
    curr_price = hist['Close'].iloc[-1]
    prev_close = info.get('previousClose', curr_price)
    change = curr_price - prev_close
    
    m1.metric("LAST", f"{curr_price:.2f}", f"{change:.2f}")
    m2.metric("BID", f"{info.get('bid', 0):.2f}")
    m3.metric("ASK", f"{info.get('ask', 0):.2f}")
    m4.metric("VOLUME", f"{info.get('volume', 0):,}")

    # The Big Chart (Candlestick Radar)
    fig = go.Figure(data=[go.Candlestick(
        x=hist.index,
        open=hist['Open'], high=hist['High'],
        low=hist['Low'], close=hist['Close'],
        increasing_line_color='#00ff00', decreasing_line_color='#ff0000'
    )])
    fig.update_layout(
        template="plotly_dark",
        height=500,
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='black',
        paper_bgcolor='black',
        xaxis_rangeslider_visible=False
    )
    st.plotly_chart(fig, use_container_width=True)

with col_side:
    st.markdown("<h4 style='color:#ff9900;'>ANALYSIS_DESK</h4>", unsafe_allow_html=True)
    
    # Financial Stats Table
    stats = {
        "Mkt Cap": f"{info.get('marketCap', 0)/1e9:.1f}B",
        "P/E Ratio": f"{info.get('trailingPE', 0):.2f}",
        "EPS": f"{info.get('trailingEps', 0):.2f}",
        "Div Yield": f"{info.get('dividendYield', 0)*100:.2f}%" if info.get('dividendYield') else "0.00%",
        "52W High": f"{info.get('fiftyTwoWeekHigh', 0):.2f}",
        "52W Low": f"{info.get('fiftyTwoWeekLow', 0):.2f}"
    }
    st.table(pd.Series(stats, name="VALUATION"))

    # AI Sentiment Signal
    st.markdown("<h4 style='color:#ff9900;'>INSTITUTIONAL_SIGNAL</h4>", unsafe_allow_html=True)
    # This is a placeholder for your Dark Pool Scraper
    st.markdown("""
        <div style='border: 1px solid #333; padding: 10px; background: #0a0a0a;'>
            <p style='color:#00ff00; margin:0;'>POS_ACCUMULATION: HIGH</p>
            <p style='color:#efefef; font-size: 10px; margin:0;'>BLOCK_ORDERS_DETECTED (LIT)</p>
        </div>
    """, unsafe_allow_html=True)

# --- 6. NEWS TICKER FOOTER ---
st.markdown("---")
st.markdown("<h4 style='color:#ff9900;'>LIVE_WIRE_NEWS</h4>", unsafe_allow_html=True)
for n in stock.news[:3]:
    st.markdown(f"**[{datetime.fromtimestamp(n['providerPublishTime']).strftime('%H:%M')}]** {n['title']}")
