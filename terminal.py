import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz
import random

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(layout="wide", page_title="SOVEREIGN_INSTITUTIONAL", initial_sidebar_state="collapsed")

# --- 2. THE BLOOMBERG/TERMINAL CSS ENGINE ---
def inject_terminal_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&family=Inter:wght@400;600;800&display=swap');
        
        /* GLOBAL RESET */
        .stApp { background-color: #050505; color: #e0e0e0; font-family: 'Inter', sans-serif; }
        * { border-radius: 0px !important; }
        
        /* REMOVE STREAMLIT PADDING */
        .block-container { padding-top: 0rem; padding-bottom: 0rem; padding-left: 1rem; padding-right: 1rem; }
        [data-testid="stHeader"] { background: transparent; height: 0px; }
        
        /* UTILITY CLASSES */
        .pos { color: #00ff00 !important; }
        .neg { color: #ff3b3b !important; }
        .neu { color: #888 !important; }
        .mono { font-family: 'Roboto Mono', monospace; }
        .caps { text-transform: uppercase; letter-spacing: 1px; font-weight: 600; font-size: 11px; color: #666; }
        
        /* 1. TICKER TAPE (TOP) */
        .ticker-bar {
            width: 100%; background: #000; border-bottom: 1px solid #333;
            color: #ccc; font-family: 'Roboto Mono', monospace; font-size: 12px;
            white-space: nowrap; overflow: hidden; padding: 6px 0;
        }
        .ticker-content { display: inline-block; animation: marquee 45s linear infinite; }
        @keyframes marquee { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
        
        /* 2. PANEL CONTAINERS (The "Modules") */
        .panel {
            background: #0a0a0a; border: 1px solid #222; margin-bottom: 10px; padding: 10px;
            height: 100%; position: relative;
        }
        .panel-header {
            border-bottom: 1px solid #333; padding-bottom: 5px; margin-bottom: 8px;
            display: flex; justify-content: space-between; align-items: center;
        }
        .panel-title { font-size: 12px; font-weight: 800; color: #fff; text-transform: uppercase; letter-spacing: 0.5px; }
        
        /* 3. MARKET DATA ROWS */
        .mkt-row {
            display: flex; justify-content: space-between; font-family: 'Roboto Mono', monospace;
            font-size: 13px; padding: 3px 0; border-bottom: 1px dashed #1a1a1a;
        }
        .mkt-row:last-child { border-bottom: none; }
        
        /* 4. NEWS FEED STYLE */
        .news-item {
            font-size: 12px; border-left: 2px solid #333; padding-left: 8px; margin-bottom: 8px;
            color: #ddd; font-family: 'Inter', sans-serif;
        }
        .news-time { color: #555; font-size: 10px; font-family: 'Roboto Mono', monospace; margin-right: 5px; }
        .news-headline { font-weight: 600; text-transform: uppercase; }
        
        /* 5. FOOTER / CLOCKS */
        .status-bar {
            position: fixed; bottom: 0; left: 0; width: 100%; background: #080808; border-top: 1px solid #333;
            padding: 4px 10px; display: flex; justify-content: space-between; font-family: 'Roboto Mono', monospace;
            font-size: 10px; color: #555; z-index: 999;
        }
        
        /* HIDE SCROLLBARS */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-thumb { background: #333; }
        </style>
    """, unsafe_allow_html=True)

inject_terminal_css()

# --- 3. ROBUST DATA ENGINE (Self-Healing) ---
class MarketDataEngine:
    def __init__(self, main_ticker):
        self.main_ticker = main_ticker
        self.mode = "LIVE"
        self.data = {}
        
    def fetch(self):
        try:
            # 1. GLOBAL INDICES
            indices = {
                "S&P 500": "^GSPC", "NASDAQ": "^IXIC", "DOW JONES": "^DJI", 
                "RUSSELL 2K": "^RUT", "VIX": "^VIX", "10Y YIELD": "^TNX", "DXY": "DX-Y.NYB"
            }
            # Batch download for speed
            tickers_list = list(indices.values()) + [self.main_ticker]
            raw_data = yf.download(tickers_list, period="2d", progress=False)['Close']
            
            # Process Indices
            self.data['indices'] = {}
            for name, sym in indices.items():
                if sym in raw_data.columns:
                    curr = raw_data[sym].iloc[-1]
                    prev = raw_data[sym].iloc[-2]
                    chg = ((curr - prev) / prev) * 100
                    self.data['indices'][name] = {"price": curr, "chg": chg}
                else:
                    self.data['indices'][name] = {"price": 0.0, "chg": 0.0}

            # 2. NEWS (Real)
            main_stock = yf.Ticker(self.main_ticker)
            news = main_stock.news
            self.data['news'] = [n['title'] for n in news[:5]] if news else []

            # 3. MAIN CHART
            self.data['hist'] = main_stock.history(period="1d", interval="5m")
            
            # 4. MARKET INTERNALS (Simulated for "Pro" look as free APIs lack this)
            self.data['internals'] = self._simulate_internals()
            
            self.mode = "LIVE UPLINK"

        except Exception as e:
            # FALLBACK TO SIMULATION
            self.mode = "SIMULATION (FAILOVER)"
            self._generate_simulation()

    def _simulate_internals(self):
        # Realistic "Pro" data generation
        return {
            "AD_LINE": random.randint(1200, 2500),
            "PUT_CALL": round(random.uniform(0.7, 1.2), 2),
            "TRIN": round(random.uniform(0.8, 1.5), 2),
            "VOL_UP_DN": f"{random.randint(4,9)}:1"
        }

    def _generate_simulation(self):
        # Fake Global Markets
        self.data['indices'] = {
            "S&P 500": {"price": 4780.20, "chg": 0.42},
            "NASDAQ": {"price": 16300.50, "chg": -0.18},
            "VIX": {"price": 14.23, "chg": 1.2},
            "10Y YIELD": {"price": 4.11, "chg": 0.05},
            "DXY": {"price": 103.82, "chg": 0.12},
        }
        # Fake News
        self.data['news'] = [
            "FED SPEAKERS SIGNAL RATES HIGHER FOR LONGER",
            f"{self.main_ticker} GUIDES ABOVE EXPECTATIONS FOR Q4",
            "OIL RISES ON GEOPOLITICAL TENSIONS",
            "CPI YOY COMES IN HOT AT 3.4%",
            "INSTITUTIONAL FLOWS SHOW ROTATION INTO TECH"
        ]
        # Fake Candles
        dates = pd.date_range(end=datetime.now(), periods=50, freq="5min")
        prices = 150 + np.random.randn(50).cumsum()
        self.data['hist'] = pd.DataFrame({
            "Open": prices, "High": prices+1, "Low": prices-1, "Close": prices, "Volume": np.random.randint(1000,5000,50)
        }, index=dates)
        self.data['internals'] = self._simulate_internals()

# --- 4. INITIALIZE DATA ---
target_ticker = st.sidebar.text_input("SYMBOL", "NVDA").upper()
engine = MarketDataEngine(target_ticker)
engine.fetch()

# --- 5. UI COMPONENTS ---

# A. TICKER TAPE (TOP)
def render_ticker_tape():
    # Watchlist for tape
    tape_list = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "BTC-USD", "ETH-USD"]
    # Try to fetch live, else mock
    tape_html = '<div class="ticker-bar"><div class="ticker-content">'
    try:
        data = yf.download(tape_list, period="1d", progress=False)['Close'].iloc[-1]
        for t in tape_list:
            px = data.get(t, 0)
            chg = random.uniform(-2, 2) # Mock chg for speed/visuals
            color = "#00ff00" if chg > 0 else "#ff3b3b"
            tape_html += f'<span style="margin-right: 20px;">{t} <span style="color:#fff">{px:.2f}</span> <span style="color:{color}">{chg:+.2f}%</span></span>'
    except:
        tape_html += "DATA LINK SEVERED // CONNECTING TO BACKUP RELAY..."
    tape_html += '</div></div>'
    st.markdown(tape_html, unsafe_allow_html=True)

# B. GLOBAL MARKETS PANEL
def render_globals(data):
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header"><span class="panel-title">GLOBAL MKTS</span><span class="caps">REALTIME</span></div>', unsafe_allow_html=True)
    
    for name, vals in data['indices'].items():
        color = "pos" if vals['chg'] >= 0 else "neg"
        st.markdown(f"""
            <div class="mkt-row">
                <span style="color:#aaa">{name}</span>
                <span>
                    <span style="color:#fff; margin-right:10px;">{vals['price']:,.2f}</span>
                    <span class="{color} mono">{vals['chg']:+.2f}%</span>
                </span>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# C. NEWS FEED
def render_news(news_items):
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header"><span class="panel-title">NEWS WIRE</span><span class="caps">DJ/BBG</span></div>', unsafe_allow_html=True)
    
    for i, headline in enumerate(news_items):
        time_offset = 5 * (i+1)
        time_str = (datetime.now() - timedelta(minutes=time_offset)).strftime("%H:%M")
        st.markdown(f"""
            <div class="news-item">
                <span class="news-time">{time_str}</span>
                <span class="news-headline">{headline.upper()}</span>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# D. KEY CHARTS
def render_chart(hist, title):
    st.markdown(f'<div class="panel" style="height: 400px; padding:0;">', unsafe_allow_html=True)
    # Header inside plot area logic or just overlay
    
    fig = go.Figure()
    # Candles
    fig.add_trace(go.Candlestick(
        x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'],
        increasing_line_color='#00ff00', decreasing_line_color='#ff3b3b', name="Price"
    ))
    # VWAP (Simulated for visuals)
    vwap = (hist['Close'] + hist['High'] + hist['Low']) / 3
    fig.add_trace(go.Scatter(x=hist.index, y=vwap, line=dict(color='#00f0ff', width=1), name="VWAP"))
    
    fig.update_layout(
        template="plotly_dark",
        margin=dict(l=0, r=40, t=30, b=0), # Right margin for price scale
        paper_bgcolor='#0a0a0a', plot_bgcolor='#0a0a0a',
        title=dict(text=f"{title} [5M]", font=dict(color="#fff", size=12, family="Roboto Mono"), x=0.02, y=0.98),
        xaxis_rangeslider_visible=False,
        xaxis=dict(showgrid=True, gridcolor='#222', tickfont=dict(color='#666', size=10)),
        yaxis=dict(showgrid=True, gridcolor='#222', tickfont=dict(color='#666', size=10), side='right')
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# E. MARKET INTERNALS & ECON
def render_internals(data):
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header"><span class="panel-title">MKT INTERNALS</span><span class="caps">NYSE/NAS</span></div>', unsafe_allow_html=True)
    
    # Fake/Sim Real data points
    ints = data['internals']
    
    metrics = [
        ("ADV/DEC LINE", ints['AD_LINE'], "pos"),
        ("PUT/CALL", ints['PUT_CALL'], "neu"),
        ("TRIN (ARMS)", ints['TRIN'], "neg" if ints['TRIN'] > 1.2 else "pos"),
        ("VOL UP/DN", ints['VOL_UP_DN'], "pos")
    ]
    
    for label, val, status in metrics:
        st.markdown(f"""
            <div class="mkt-row">
                <span style="color:#888">{label}</span>
                <span class="{status} mono">{val}</span>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_econ():
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header"><span class="panel-title">ECON CALENDAR</span><span class="caps">TODAY</span></div>', unsafe_allow_html=True)
    
    events = [
        ("08:30 ET", "CPI YOY", "3.4%", "HIGH"),
        ("08:30 ET", "CORE CPI", "3.9%", "HIGH"),
        ("10:30 ET", "CRUDE INV", "-2.1M", "MED"),
        ("14:00 ET", "FOMC MINS", "--", "HIGH")
    ]
    
    for time, event, act, imp in events:
        color = "#ff3b3b" if imp == "HIGH" else "#ebae34"
        st.markdown(f"""
            <div class="mkt-row">
                <span class="mono" style="color:#555">{time}</span>
                <span style="color:#ddd">{event}</span>
                <span class="mono" style="color:#fff">{act}</span>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 6. LAYOUT CONSTRUCTION ---

# Top Ticker
render_ticker_tape()

# Main Grid
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    # LEFT COLUMN: MARKETS & WATCHLIST
    render_globals(engine.data)
    render_internals(engine.data)
    
    # Quick Watchlist
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header"><span class="panel-title">WATCHLIST</span></div>', unsafe_allow_html=True)
    wl = ["META", "AMD", "COIN", "PLTR"]
    for w in wl:
        chg = random.uniform(-3, 3)
        c = "pos" if chg > 0 else "neg"
        st.markdown(f'<div class="mkt-row"><span>{w}</span><span class="{c} mono">{chg:+.2f}%</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # CENTER COLUMN: CHARTS
    render_chart(engine.data['hist'], f"{target_ticker} PRICE ACTION")
    # Secondary Chart (Market Proxy)
    # In a real app we'd fetch SPY, here reusing hist for layout demo
    render_chart(engine.data['hist'], "ES FUTURES (PROXY)")

with col3:
    # RIGHT COLUMN: NEWS & ECON
    render_news(engine.data['news'])
    render_econ()
    
    # Gainers
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header"><span class="panel-title">TOP MOVERS</span></div>', unsafe_allow_html=True)
    movers = [("NVDA", "+3.2%"), ("ARM", "+2.8%"), ("TSLA", "-2.4%"), ("BA", "-1.9%")]
    for t, p in movers:
        c = "pos" if "+" in p else "neg"
        st.markdown(f'<div class="mkt-row"><span>{t}</span><span class="{c} mono">{p}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 7. FOOTER / CLOCKS ---
tz_ny = pytz.timezone('US/Eastern')
tz_ldn = pytz.timezone('Europe/London')
tz_tyo = pytz.timezone('Asia/Tokyo')
now_ny = datetime.now(tz_ny).strftime("%H:%M")
now_ldn = datetime.now(tz_ldn).strftime("%H:%M")
now_tyo = datetime.now(tz_tyo).strftime("%H:%M")

st.markdown(f"""
    <div class="status-bar">
        <span>STATUS: <span style="color:#00ff00">{engine.mode}</span></span>
        <span>NY: {now_ny} | LDN: {now_ldn} | TYO: {now_tyo}</span>
        <span>INTERNAL USE ONLY // SOVEREIGN TERMINAL v9.0</span>
    </div>
""", unsafe_allow_html=True)
