import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# --- 1. CORE CONFIGURATION ---
st.set_page_config(layout="wide", page_title="SOVEREIGN_NEON_PRIME", initial_sidebar_state="collapsed")

# --- 2. THE NEON UI ENGINE (MAX GLOW) ---
def apply_neon_ui(main_color="#00f0ff", alert_color="#ff2a00"):
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

        /* 2. GLOBAL DARK MODE */
        .stApp {{ background-color: #020202; color: {main_color}; font-family: 'JetBrains Mono', monospace; }}
        * {{ border-radius: 0px !important; }} 

        /* 3. STICKY NEON HUD */
        [data-testid="stHeader"] {{ background: rgba(0,0,0,0.95) !important; border-bottom: 2px solid {main_color} !important; }}
        .sticky-hud {{
            position: sticky; top: 0; z-index: 9999; 
            background: #000; padding: 10px; border-bottom: 2px solid {main_color};
            display: flex; justify-content: space-between; align-items: center;
            box-shadow: 0 5px 40px {main_color}44; /* HELLA NEON GLOW */
        }}

        /* 4. INFINITE TICKER */
        .ticker-wrap {{ width: 100%; overflow: hidden; background: #000; border-bottom: 1px solid {main_color}55; padding: 6px 0; white-space: nowrap; }}
        .ticker-content {{ display: inline-block; animation: marquee 35s linear infinite; }}
        @keyframes marquee {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-50%); }} }}
        
        .stock-box {{
            display: inline-block; padding: 4px 15px; margin: 0 5px;
            border: 1px solid {main_color}44; background: {main_color}08;
            font-size: 14px; font-weight: bold; color: {main_color};
            box-shadow: inset 0 0 15px {main_color}22; /* INTERNAL GLOW */
            text-shadow: 0 0 5px {main_color};
        }}

        /* 5. STARK BRACKET FRAMES */
        .stark-frame {{
            position: relative; margin: 20px 0; padding: 25px;
            border: 1px solid {main_color}22; background: rgba(0,0,0,0.6);
            box-shadow: 0 0 30px rgba(0,0,0,0.9);
        }}
        /* GLOWING CORNERS */
        .stark-frame::before {{ 
            content: ""; position: absolute; top: 0; left: 0; width: 15px; height: 15px; 
            border-top: 3px solid {main_color}; border-left: 3px solid {main_color}; 
            filter: drop-shadow(0 0 8px {main_color}); 
        }}
        .stark-frame::after {{ 
            content: ""; position: absolute; bottom: 0; right: 0; width: 15px; height: 15px; 
            border-bottom: 3px solid {main_color}; border-right: 3px solid {main_color}; 
            filter: drop-shadow(0 0 8px {main_color}); 
        }}

        /* 6. TELEMETRY GRID */
        .telemetry-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 4px; }}
        .telemetry-tile {{ 
            background: {main_color}05; border: 1px solid {main_color}15; padding: 12px; 
            transition: all 0.3s ease;
        }}
        .telemetry-tile:hover {{ 
            background: {main_color}15; border-color: {main_color}; 
            box-shadow: 0 0 25px {main_color}44; /* HOVER GLOW */
        }}
        
        .tag {{ font-size: 9px; color: #555; letter-spacing: 2px; text-transform: uppercase; }}
        .val {{ font-size: 14px; font-weight: bold; color: {main_color}; text-shadow: 0 0 12px {main_color}; }}
        
        /* 7. ALERT OVERRIDES */
        .alert-mode .val {{ color: {alert_color} !important; text-shadow: 0 0 15px {alert_color} !important; }}
        .alert-mode .stock-box {{ border-color: {alert_color}; color: {alert_color}; background: {alert_color}11; box-shadow: inset 0 0 15px {alert_color}22; }}
        .alert-mode .sticky-hud {{ border-color: {alert_color}; box-shadow: 0 5px 40px {alert_color}44; }}

        ::-webkit-scrollbar {{ display: none; }}
        </style>
    """, unsafe_allow_html=True)

# --- 3. ROBUST DATA ENGINE (Live + Sim Fallback) ---
ticker_input = st.sidebar.text_input("CMD_INPUT", "NVDA").upper()

# Variables
info = {}
hist = pd.DataFrame()
theme_color = "#00f0ff" # Default Electric Cyan
alert_class = ""
data_source = "LIVE_UPLINK"

try:
    # 1. Attempt Live Fetch
    stock = yf.Ticker(ticker_input)
    # Only fetch if we haven't hit limit
    info = stock.info
    hist = stock.history(period="1d", interval="1m")
    
    if hist.empty: raise Exception("Empty Data")

    # 2. Color Logic
    current = info.get('currentPrice', hist['Close'].iloc[-1])
    previous = info.get('previousClose', hist['Open'].iloc[0])
    
    if current >= previous:
        theme_color = "#00f0ff" # Neon Cyan
    else:
        theme_color = "#ff2a00" # Neon Danger Red
        alert_class = "alert-mode"

except Exception:
    # 3. SIMULATION MODE (Fallback)
    data_source = "SIMULATION_MODE (OFFLINE)"
    theme_color = "#00f0ff"
    
    # Generate Fake Candle Data
    dates = pd.date_range(end=datetime.now(), periods=100, freq="1min")
    prices = 150.0 + np.random.randn(100).cumsum()
    
    hist = pd.DataFrame(index=dates)
    hist['Open'] = prices
    hist['High'] = prices + 0.5
    hist['Low'] = prices - 0.5
    hist['Close'] = prices + np.random.randn(100) * 0.2
    hist['Volume'] = np.random.randint(1000, 50000, size=100)
    
    # Fake Info Dict to keep the grid populated
    info = {
        'symbol': ticker_input, 'currentPrice': round(prices[-1], 2),
        'marketCap': 2000000000000, 'volume': 45000000,
        'sector': 'Technology', 'auditRisk': 'LOW'
    }

# APPLY NEON STYLE
apply_neon_ui(main_color=theme_color, alert_color="#ff2a00")

# --- 4. INFINITE TICKER (Hybrid) ---
tape_tickers = ["NVDA", "TSLA", "AMD", "PLTR", "COIN", "MSTR", "SMCI", "ARM", "NET", "CRWD"]
ticker_html = '<div class="ticker-wrap"><div class="ticker-content">'
for _ in range(3):
    for t in tape_tickers:
        # Use random price in case of rate limit, ensures visual consistency
        rand_price = np.random.uniform(100, 1000)
        ticker_html += f'<div class="stock-box">{t} <span style="opacity:0.8;">${rand_price:.2f}</span></div>'
ticker_html += '</div></div>'
st.markdown(ticker_html, unsafe_allow_html=True)

# --- 5. STICKY HUD ---
st.markdown(f"""
    <div class="sticky-hud {alert_class}">
        <div style="font-size: 20px; font-weight: bold; letter-spacing: 6px; text-shadow: 0 0 15px {theme_color};">SOVEREIGN_NEON</div>
        <div style="font-family: monospace; font-size: 12px; opacity: 0.8;">{data_source} // {datetime.now().strftime('%H:%M:%S')}</div>
    </div>
""", unsafe_allow_html=True)

# --- 6. HOLOGRAPHIC MAP ---
st.markdown(f'<div class="stark-frame"><div class="tag">// GLOBAL_MARKET_FLOW</div>', unsafe_allow_html=True)
connections = [
    dict(type='scattergeo', lat=[40.7, 35.6], lon=[-74.0, 139.6], mode='lines', line=dict(width=2, color=theme_color)),
    dict(type='scattergeo', lat=[35.6, 1.3], lon=[139.6, 103.8], mode='lines', line=dict(width=2, color=theme_color)),
    dict(type='scattergeo', lat=[51.5, 25.2], lon=[-0.1, 55.3], mode='lines', line=dict(width=2, color=theme_color)),
]
map_fig = go.Figure(data=connections)
map_fig.update_geos(
    projection_type="orthographic", showcoastlines=True, coastlinecolor=theme_color,
    showland=True, landcolor="#050505", showocean=True, oceancolor="#020202",
    showcountries=True, countrycolor="#1a1a1a", bgcolor="rgba(0,0,0,0)",
    lataxis=dict(showgrid=True, gridcolor="#151515"), lonaxis=dict(showgrid=True, gridcolor="#151515")
)
map_fig.update_layout(height=450, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(map_fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 7. SIGNAL CHARTS ---
st.markdown(f'<div class="stark-frame"><div class="tag">// TECHNICAL_INTERCEPT: {ticker_input}</div>', unsafe_allow_html=True)
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.5, 0.25, 0.25])
fig.add_trace(go.Candlestick(
    x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'],
    increasing_line_color='#00f0ff', decreasing_line_color='#ff2a00'
), row=1, col=1)
fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], marker_color=theme_color, opacity=0.3), row=2, col=1)
fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'].rolling(20).mean(), line=dict(color='white', width=1, dash='dot')), row=3, col=1)
fig.update_layout(template="plotly_dark", height=600, showlegend=False, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=True, gridcolor='#1a1a1a')
st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 8. TELEMETRY MATRIX (100 LINES) ---
st.markdown(f'<div class="stark-frame"><div class="tag">// FUNDAMENTAL_MATRIX_DUMP</div>', unsafe_allow_html=True)
st.markdown('<div class="telemetry-grid">', unsafe_allow_html=True)
for key, value in info.items():
    if value and len(str(value)) < 25:
        st.markdown(f'<div class="telemetry-tile"><div class="tag">{str(key).upper()}</div><div class="val">{str(value)}</div></div>', unsafe_allow_html=True)
st.markdown('</div></div>', unsafe_allow_html=True)
