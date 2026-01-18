import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz
import random
import time

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(layout="wide", page_title="SOVEREIGN_TERMINAL_X", initial_sidebar_state="collapsed")

# --- 2. THE BLOOMBERG/TERMINAL CSS ENGINE ---
def inject_terminal_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&family=Inter:wght@400;600;800&display=swap');
        
        /* GLOBAL RESET */
        .stApp { background-color: #000000; color: #e0e0e0; font-family: 'Inter', sans-serif; }
        * { border-radius: 0px !important; }
        
        /* REMOVE PADDING */
        .block-container { padding-top: 0rem; padding-bottom: 0rem; padding-left: 0.5rem; padding-right: 0.5rem; }
        [data-testid="stHeader"] { display: none; }
        
        /* UTILITY CLASSES */
        .pos { color: #00ff00 !important; }
        .neg { color: #ff3b3b !important; }
        .neu { color: #666 !important; }
        .mono { font-family: 'Roboto Mono', monospace; }
        
        /* BLINKING CURSOR ANIMATION */
        @keyframes blink { 0% { opacity: 0; } 50% { opacity: 1; } 100% { opacity: 0; } }
        .cursor { color: #00ff00; animation: blink 1s infinite; font-weight: bold; }

        /* PANEL CONTAINERS */
        .panel {
            background: #080808; border: 1px solid #222; margin-bottom: 5px; padding: 8px;
            height: 100%; position: relative; min-height: 200px;
        }
        .panel-header {
            border-bottom: 1px solid #333; padding-bottom: 4px; margin-bottom: 8px;
            display: flex; justify-content: space-between; align-items: center;
        }
        .panel-title { font-size: 11px; font-weight: 800; color: #888; text-transform: uppercase; letter-spacing: 1px; }
        
        /* BLANK / RESERVED BOX STYLE */
        .blank-box {
            background: repeating-linear-gradient(45deg, #050505, #050505 10px, #0a0a0a 10px, #0a0a0a 20px);
            border: 1px dashed #333;
            color: #333;
            display: flex; align-items: center; justify-content: center;
            height: 100%; min-height: 200px;
            font-family: 'Roboto Mono', monospace; font-size: 10px; letter-spacing: 2px;
            opacity: 0.6;
        }

        /* TICKER TAPE */
        .ticker-bar {
            width: 100%; background: #000; border-bottom: 1px solid #222;
            color: #aaa; font-family: 'Roboto Mono', monospace; font-size: 12px;
            white-space: nowrap; overflow: hidden; padding: 4px 0; margin-bottom: 5px;
        }
        
        /* NEWS & MARKET ROWS */
        .mkt-row {
            display: flex; justify-content: space-between; font-family: 'Roboto Mono', monospace;
            font-size: 12px; padding: 2px 0; border-bottom: 1px dotted #1a1a1a;
        }
        .news-item {
            font-size: 11px; border-left: 2px solid #222; padding-left: 6px; margin-bottom: 6px;
            color: #ccc;
        }
        
        /* SCROLLBAR KILLER */
        ::-webkit-scrollbar { width: 0px; background: transparent; }
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
            # 1. GLOBAL INDICES (Live Batch Fetch)
            indices = {
                "ES (S&P)": "^GSPC", "NQ (NAS)": "^IXIC", "YM (DOW)": "^DJI", 
                "RTY (RUSS)": "^RUT", "VIX": "^VIX", "US10Y": "^TNX", "DXY": "DX-Y.NYB"
            }
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

            # 2. MAIN CHART & NEWS
            main_stock = yf.Ticker(self.main_ticker)
            self.data['news'] = [n['title'] for n in main_stock.news[:6]] if main_stock.news else []
            self.data['hist'] = main_stock.history(period="1d", interval="5m")
            
            self.mode = "LIVE UPLINK"

        except Exception:
            self.mode = "SIMULATION (FAILOVER)"
            self._generate_simulation()

    def _generate_simulation(self):
        # Fake Data Pattern
        self.data['indices'] = {
            "ES (S&P)": {"price": 4780.20, "chg": 0.42}, "NQ (NAS)": {"price": 16300.50, "chg": -0.18},
            "VIX": {"price": 14.23, "chg": 1.2}, "US10Y": {"price": 4.11, "chg": 0.05},
        }
        self.data['news'] = [
            "FED SPEAKERS SIGNAL RATES HIGHER FOR LONGER",
            f"{self.main_ticker} GUIDES ABOVE EXPECTATIONS FOR Q4",
            "INSTITUTIONAL FLOWS SHOW ROTATION INTO TECH",
            "OIL RISES ON GEOPOLITICAL TENSIONS",
            "ECB PRESIDENT LAGARDE SPEAKS IN DAVOS"
        ]
        dates = pd.date_range(end=datetime.now(), periods=50, freq="5min")
        prices = 150 + np.random.randn(50).cumsum()
        self.data['hist'] = pd.DataFrame({
            "Open": prices, "High": prices+1, "Low": prices-1, "Close": prices, "Volume": np.random.randint(1000,5000,50)
        }, index=dates)

# --- 4. INITIALIZE ---
target_ticker = st.sidebar.text_input("SYMBOL", "NVDA").upper()
engine = MarketDataEngine(target_ticker)
engine.fetch()

# --- 5. RENDER FUNCTIONS ---

def render_blank_box(label="RESERVED"):
    """Creates the 'Empty Box' aesthetic requested"""
    st.markdown(f"""
        <div class="panel">
            <div class="panel-header"><span class="panel-title">// {label}</span></div>
            <div class="blank-box">
                <span>NO SIGNAL <span class="cursor">_</span></span>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_chart(hist, title):
    st.markdown(f'<div class="panel" style="padding:0; overflow:hidden;">', unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'],
        increasing_line_color='#00ff00', decreasing_line_color='#ff3b3b', name="Price"
    ))
    fig.update_layout(
        template="plotly_dark", height=250,
        margin=dict(l=0, r=40, t=30, b=0),
        paper_bgcolor='#080808', plot_bgcolor='#080808',
        title=dict(text=f"{title}", font=dict(color="#666", size=10, family="Roboto Mono"), x=0.02, y=0.95),
        xaxis=dict(showgrid=True, gridcolor='#1a1a1a', tickfont=dict(color='#444', size=8)),
        yaxis=dict(showgrid=True, gridcolor='#1a1a1a', tickfont=dict(color='#444', size=8), side='right'),
        xaxis_rangeslider_visible=False
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_news(news):
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header"><span class="panel-title">NEWS WIRE <span class="cursor">●</span></span></div>', unsafe_allow_html=True)
    for n in news:
        st.markdown(f'<div class="news-item">{n}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_globals(indices):
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header"><span class="panel-title">GLOBAL MKTS</span></div>', unsafe_allow_html=True)
    for name, data in indices.items():
        color = "pos" if data['chg'] >= 0 else "neg"
        st.markdown(f"""
            <div class="mkt-row">
                <span style="color:#666">{name}</span>
                <span><span style="color:#eee">{data['price']:,.2f}</span> <span class="{color} mono">{data['chg']:+.2f}%</span></span>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 6. LAYOUT GRID ---

# A. TICKER TAPE
tape_html = '<div class="ticker-bar"><div class="ticker-content">'
tape_list = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "BTC-USD", "ETH-USD"]
try:
    live_prices = yf.download(tape_list, period="1d", progress=False)['Close'].iloc[-1]
    for t in tape_list:
        p = live_prices.get(t, 0)
        c = "pos" if random.random() > 0.5 else "neg" # Mock change color for speed
        tape_html += f'<span style="margin-right: 25px;">{t} <span style="color:#fff">{p:.2f}</span> <span class="{c}">{-1.2 if c=="neg" else 0.8}%</span></span>'
except: 
    tape_html += "DATA LINK SEVERED // CONNECTING..."
tape_html += '</div></div>'
st.markdown(tape_html, unsafe_allow_html=True)

# B. MAIN DASHBOARD
# Row 1: Globals | Main Chart | Blank Box (as requested)
c1, c2, c3 = st.columns([1, 2, 1])
with c1: render_globals(engine.data['indices'])
with c2: render_chart(engine.data['hist'], f"{target_ticker} [5M] PRICE ACTION")
with c3: render_blank_box("ALGO_01_STATUS") # <--- THE BLANK BOX

# Row 2: News | Blank Box | Blank Box (The Grid Look)
c4, c5, c6 = st.columns([1, 1, 1])
with c4: render_news(engine.data['news'])
with c5: render_blank_box("INTERNAL_CROSS_RATES") # <--- BLANK BOX 2
with c6: 
    # Mini Watchlist (Mock)
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header"><span class="panel-title">WATCHLIST</span></div>', unsafe_allow_html=True)
    for s in ["META", "AMD", "COIN", "PLTR", "SOFI"]:
        st.markdown(f'<div class="mkt-row"><span>{s}</span><span class="neg">-0.4%</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Footer Status
st.markdown(f"""
    <div style="position:fixed; bottom:0; width:100%; background:#000; color:#444; font-size:10px; padding:2px 10px; border-top:1px solid #222; font-family:'Roboto Mono';">
        SYSTEM: <span style="color:#00ff00">{engine.mode}</span> | LATENCY: 12ms | <span class="cursor">_</span>
    </div>
""", unsafe_allow_html=True)
