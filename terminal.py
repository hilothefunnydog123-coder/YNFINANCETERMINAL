import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import random

# --- 1. CORE CONFIGURATION ---
st.set_page_config(layout="wide", page_title="SOVEREIGN_SPECTRUM", initial_sidebar_state="collapsed")

# --- 2. THE MULTI-COLOR NEON ENGINE ---
def apply_spectrum_ui():
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
        
        /* 1. PHYSICAL MESH OVERLAY */
        .stApp::before {{
            content: " "; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(rgba(10, 10, 10, 0) 50%, rgba(0, 0, 0, 0.4) 50%), 
                        linear-gradient(90deg, rgba(255, 0, 0, 0.03), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.03));
            background-size: 100% 3px, 3px 100%; z-index: 9999; pointer-events: none;
        }}

        /* 2. DARK MODE BASE */
        .stApp {{ background-color: #020202; color: #fff; font-family: 'JetBrains Mono', monospace; }}
        * {{ border-radius: 0px !important; }} 

        /* 3. STICKY HUD (RGB GRADIENT BORDER) */
        [data-testid="stHeader"] {{ background: rgba(0,0,0,0.95) !important; }}
        .sticky-hud {{
            position: sticky; top: 0; z-index: 9999; 
            background: #000; padding: 10px; 
            border-bottom: 3px solid transparent;
            border-image: linear-gradient(to right, #00f0ff, #ff00aa, #00ff00) 1;
            display: flex; justify-content: space-between; align-items: center;
            box-shadow: 0 10px 30px rgba(0, 240, 255, 0.1);
        }}

        /* 4. INFINITE TICKER */
        .ticker-wrap {{ width: 100%; overflow: hidden; background: #000; border-bottom: 1px solid #333; padding: 6px 0; white-space: nowrap; }}
        .ticker-content {{ display: inline-block; animation: marquee 30s linear infinite; }}
        @keyframes marquee {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-50%); }} }}
        
        .stock-box {{
            display: inline-block; padding: 4px 15px; margin: 0 5px;
            border: 1px solid #333; background: rgba(255,255,255,0.05);
            font-size: 14px; font-weight: bold;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
        }}

        /* 5. STARK BRACKET FRAMES */
        .stark-frame {{
            position: relative; margin: 20px 0; padding: 25px;
            border: 1px solid rgba(255,255,255,0.1); background: rgba(0,0,0,0.6);
        }}
        
        /* 6. COLOR CLASSES FOR ELEMENTS */
        .c-cyan {{ color: #00f0ff; border-color: #00f0ff !important; text-shadow: 0 0 10px #00f0ff; }}
        .c-pink {{ color: #ff00aa; border-color: #ff00aa !important; text-shadow: 0 0 10px #ff00aa; }}
        .c-green {{ color: #00ff00; border-color: #00ff00 !important; text-shadow: 0 0 10px #00ff00; }}
        .c-orange {{ color: #ffae00; border-color: #ffae00 !important; text-shadow: 0 0 10px #ffae00; }}
        .c-purple {{ color: #bd00ff; border-color: #bd00ff !important; text-shadow: 0 0 10px #bd00ff; }}

        /* 7. TELEMETRY GRID */
        .telemetry-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 4px; }}
        .telemetry-tile {{ 
            background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.1); padding: 12px; 
            transition: all 0.3s ease;
        }}
        .telemetry-tile:hover {{ transform: translateY(-2px); }}
        
        .tag {{ font-size: 9px; color: #666; letter-spacing: 2px; text-transform: uppercase; }}
        .val {{ font-size: 14px; font-weight: bold; }}

        ::-webkit-scrollbar {{ display: none; }}
        </style>
    """, unsafe_allow_html=True)

# --- 3. ROBUST DATA ENGINE (Live + Sim Fallback) ---
ticker_input = st.sidebar.text_input("CMD_INPUT", "NVDA").upper()
info = {}
hist = pd.DataFrame()
data_source = "LIVE_UPLINK"

try:
    stock = yf.Ticker(ticker_input)
    info = stock.info
    hist = stock.history(period="1d", interval="1m")
    if hist.empty: raise Exception("Empty Data")
except Exception:
    data_source = "SIMULATION_MODE (OFFLINE)"
    dates = pd.date_range(end=datetime.now(), periods=100, freq="1min")
    prices = 150.0 + np.random.randn(100).cumsum()
    hist = pd.DataFrame(index=dates)
    hist['Open'] = prices
    hist['High'] = prices + 0.5
    hist['Low'] = prices - 0.5
    hist['Close'] = prices + np.random.randn(100) * 0.2
    hist['Volume'] = np.random.randint(1000, 50000, size=100)
    info = {'symbol': ticker_input, 'currentPrice': round(prices[-1], 2), 'sector': 'Tech', 'volume': 5000000, 'marketCap': 1000000000}

apply_spectrum_ui()

# --- 4. MULTI-COLOR TICKER TAPE ---
# Defines the neon palette to cycle through
colors = ["c-cyan", "c-pink", "c-green", "c-orange", "c-purple"]
tape_tickers = ["NVDA", "TSLA", "AMD", "PLTR", "COIN", "MSTR", "SMCI", "ARM", "NET", "CRWD"]

ticker_html = '<div class="ticker-wrap"><div class="ticker-content">'
for _ in range(3):
    for i, t in enumerate(tape_tickers):
        # Assign a random color class to each box
        color_class = colors[i % len(colors)]
        rand_price = np.random.uniform(100, 1000)
        ticker_html += f'<div class="stock-box {color_class}">{t} <span style="opacity:0.8;">${rand_price:.0f}</span></div>'
ticker_html += '</div></div>'
st.markdown(ticker_html, unsafe_allow_html=True)

# --- 5. STICKY HUD ---
st.markdown(f"""
    <div class="sticky-hud">
        <div style="font-size: 20px; font-weight: bold; letter-spacing: 6px; background: -webkit-linear-gradient(left, #00f0ff, #ff00aa); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">SOVEREIGN_SPECTRUM</div>
        <div style="font-family: monospace; font-size: 12px; opacity: 0.8; color: #00ff00;">{data_source} // {datetime.now().strftime('%H:%M:%S')}</div>
    </div>
""", unsafe_allow_html=True)

# --- 6. MULTI-COLOR HOLOGRAPHIC MAP ---
st.markdown(f'<div class="stark-frame"><div class="tag" style="color:#00f0ff">// GLOBAL_MARKET_FLOW</div>', unsafe_allow_html=True)
# Different colors for different routes
connections = [
    dict(type='scattergeo', lat=[40.7, 35.6], lon=[-74.0, 139.6], mode='lines', line=dict(width=2, color='#00f0ff')), # Cyan Route
    dict(type='scattergeo', lat=[35.6, 1.3], lon=[139.6, 103.8], mode='lines', line=dict(width=2, color='#ff00aa')), # Pink Route
    dict(type='scattergeo', lat=[51.5, 25.2], lon=[-0.1, 55.3], mode='lines', line=dict(width=2, color='#00ff00')), # Green Route
    dict(type='scattergeo', lat=[25.2, -33.8], lon=[55.3, 151.2], mode='lines', line=dict(width=2, color='#ffae00')), # Orange Route
]
map_fig = go.Figure(data=connections)
map_fig.update_geos(
    projection_type="orthographic", showcoastlines=True, coastlinecolor="#444",
    showland=True, landcolor="#050505", showocean=True, oceancolor="#000",
    showcountries=True, countrycolor="#222", bgcolor="rgba(0,0,0,0)",
    lataxis=dict(showgrid=True, gridcolor="#151515"), lonaxis=dict(showgrid=True, gridcolor="#151515")
)
map_fig.update_layout(height=450, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(map_fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 7. SIGNAL CHARTS (Color Coded) ---
st.markdown(f'<div class="stark-frame"><div class="tag" style="color:#ff00aa">// TECHNICAL_INTERCEPT: {ticker_input}</div>', unsafe_allow_html=True)
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.5, 0.25, 0.25])

# Cyan/Pink Candles
fig.add_trace(go.Candlestick(
    x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'],
    increasing_line_color='#00f0ff', decreasing_line_color='#ff00aa'
), row=1, col=1)

# Purple Volume
fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], marker_color='#bd00ff', opacity=0.5), row=2, col=1)

# Orange MA Line
fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'].rolling(20).mean(), line=dict(color='#ffae00', width=1)), row=3, col=1)

fig.update_layout(template="plotly_dark", height=600, showlegend=False, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=True, gridcolor='#1a1a1a')
st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 8. RAINBOW TELEMETRY MATRIX ---
st.markdown(f'<div class="stark-frame"><div class="tag" style="color:#00ff00">// FUNDAMENTAL_MATRIX_DUMP</div>', unsafe_allow_html=True)
st.markdown('<div class="telemetry-grid">', unsafe_allow_html=True)

# Cycle through colors for each tile to create the "Spectrum" effect
for i, (key, value) in enumerate(info.items()):
    if value and len(str(value)) < 25:
        color_class = colors[i % len(colors)] # Cycle colors
        st.markdown(f"""
            <div class="telemetry-tile {color_class}" style="border-width: 1px; border-style: solid;">
                <div class="tag" style="color: #888;">{str(key).upper()}</div>
                <div class="val" style="color: inherit;">{str(value)}</div>
            </div>
        """, unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)
