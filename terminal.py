import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# --- 1. CORE CONFIGURATION ---
st.set_page_config(layout="wide", page_title="TOKYO_NEON_PRIME", initial_sidebar_state="collapsed")

# --- 2. TOKYO NEON UI ENGINE ---
def apply_tokyo_ui():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
        
        /* 1. RAIN/GLITCH OVERLAY (Subtle Texture) */
        .stApp::before {
            content: " "; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(rgba(0,0,0,0.9), rgba(0,0,0,0.4)), 
                        repeating-linear-gradient(0deg, transparent, transparent 2px, #00f0ff 3px);
            background-size: 100% 4px; opacity: 0.1;
            z-index: 9999; pointer-events: none;
        }

        /* 2. BASE TERMINAL STYLE */
        .stApp { background-color: #050505; color: #00f0ff; font-family: 'JetBrains Mono', monospace; }
        * { border-radius: 0px !important; } 

        /* 3. STICKY HUD (Cyber-Noir) */
        [data-testid="stHeader"] { background: rgba(0,0,0,0.95) !important; }
        .sticky-hud {
            position: sticky; top: 0; z-index: 9999; 
            background: #000; padding: 12px; 
            border-bottom: 2px solid #8a00c2; /* Electric Purple Border */
            box-shadow: 0 0 30px rgba(138, 0, 194, 0.3);
            display: flex; justify-content: space-between; align-items: center;
        }

        /* 4. INFINITE TICKER (Strict Color Logic) */
        .ticker-wrap { width: 100%; overflow: hidden; background: #000; border-bottom: 1px solid #1a1a1a; padding: 8px 0; white-space: nowrap; }
        .ticker-content { display: inline-block; animation: marquee 30s linear infinite; }
        @keyframes marquee { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
        
        .stock-box {
            display: inline-block; padding: 4px 15px; margin: 0 5px;
            border: 1px solid #333; background: #080808;
            font-size: 14px; font-weight: bold;
            color: #fff;
        }
        .up { color: #00ff41; border-color: #00ff41; box-shadow: inset 0 0 10px rgba(0, 255, 65, 0.1); }
        .down { color: #ff0055; border-color: #ff0055; box-shadow: inset 0 0 10px rgba(255, 0, 85, 0.1); }

        /* 5. TOKYO FRAMES (Dual Tone) */
        .stark-frame {
            position: relative; margin: 20px 0; padding: 25px;
            border: 1px solid #00f0ff; background: rgba(0, 10, 20, 0.8);
            box-shadow: 0 0 20px rgba(0, 240, 255, 0.1);
        }
        /* Cyan Top-Left, Purple Bottom-Right */
        .stark-frame::before { 
            content: ""; position: absolute; top: 0; left: 0; width: 15px; height: 15px; 
            border-top: 3px solid #00f0ff; border-left: 3px solid #00f0ff; 
            filter: drop-shadow(0 0 5px #00f0ff);
        }
        .stark-frame::after { 
            content: ""; position: absolute; bottom: 0; right: 0; width: 15px; height: 15px; 
            border-bottom: 3px solid #8a00c2; border-right: 3px solid #8a00c2; 
            filter: drop-shadow(0 0 5px #8a00c2);
        }

        /* 6. TELEMETRY GRID (Uniform Blue Matrix) */
        .telemetry-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 4px; }
        .telemetry-tile { 
            background: rgba(0, 240, 255, 0.02); border: 1px solid rgba(0, 240, 255, 0.15); padding: 12px; 
            transition: all 0.2s ease;
        }
        .telemetry-tile:hover { 
            background: rgba(0, 240, 255, 0.1); border-color: #00f0ff; 
            box-shadow: 0 0 15px rgba(0, 240, 255, 0.4); 
        }
        
        .tag { font-size: 9px; color: #888; letter-spacing: 2px; text-transform: uppercase; }
        .val { font-size: 14px; font-weight: bold; color: #00f0ff; text-shadow: 0 0 8px rgba(0, 240, 255, 0.6); }

        /* 7. GUTTER DATA */
        .gutter { position: fixed; top: 250px; font-size: 9px; color: #444; writing-mode: vertical-rl; letter-spacing: 4px; z-index: 0; }
        .left-gutter { left: 8px; border-right: 1px solid #222; padding-right: 5px; height: 300px; }
        .right-gutter { right: 8px; border-left: 1px solid #222; padding-left: 5px; height: 300px; }

        ::-webkit-scrollbar { display: none; }
        </style>
    """, unsafe_allow_html=True)

# --- 3. ROBUST DATA ENGINE ---
ticker_input = st.sidebar.text_input("CMD_INPUT", "NVDA").upper()
info = {}
hist = pd.DataFrame()
data_source = "LIVE_TOKYO_UPLINK"
status_color = "#00f0ff"

try:
    stock = yf.Ticker(ticker_input)
    info = stock.info
    hist = stock.history(period="1d", interval="1m")
    if hist.empty: raise Exception("Empty Data")
except Exception:
    data_source = "SIM_MODE // OFFLINE"
    status_color = "#ff0055"
    dates = pd.date_range(end=datetime.now(), periods=100, freq="1min")
    prices = 150.0 + np.random.randn(100).cumsum()
    hist = pd.DataFrame(index=dates)
    hist['Open'] = prices
    hist['High'] = prices + 0.5
    hist['Low'] = prices - 0.5
    hist['Close'] = prices + np.random.randn(100) * 0.2
    hist['Volume'] = np.random.randint(1000, 50000, size=100)
    info = {'symbol': ticker_input, 'currentPrice': round(prices[-1], 2), 'sector': 'Technology', 'volume': 8500000, 'marketCap': 2500000000}

apply_tokyo_ui()

# --- 4. LOGICAL TICKER TAPE (Green/Red Only) ---
tape_tickers = ["NVDA", "TSLA", "AMD", "PLTR", "COIN", "MSTR", "SMCI", "ARM", "NET", "CRWD"]
ticker_html = '<div class="ticker-wrap"><div class="ticker-content">'

for _ in range(3):
    for t in tape_tickers:
        # Generate random price and movement for the aesthetic
        rand_price = np.random.uniform(100, 1000)
        rand_change = np.random.uniform(-5, 5)
        
        # LOGIC: Green if up, Red if down. No Rainbows.
        color_class = "up" if rand_change >= 0 else "down"
        arrow = "▲" if rand_change >= 0 else "▼"
        
        ticker_html += f'<div class="stock-box {color_class}">{t} <span style="opacity:0.8;">${rand_price:.2f} {arrow} {abs(rand_change):.1f}%</span></div>'

ticker_html += '</div></div>'
st.markdown(ticker_html, unsafe_allow_html=True)

# --- 5. STICKY HUD ---
st.markdown(f"""
    <div class="sticky-hud">
        <div style="font-size: 20px; font-weight: bold; letter-spacing: 4px; color: #fff; text-shadow: 0 0 10px #00f0ff;">NEO_TOKYO_TERMINAL</div>
        <div style="font-family: monospace; font-size: 12px; color: {status_color}; text-shadow: 0 0 5px {status_color};">{data_source} // {datetime.now().strftime('%H:%M:%S')}</div>
    </div>
    <div class="gutter left-gutter">SYSTEM_OPTIMAL // NETWORK_SECURE</div>
    <div class="gutter right-gutter">QUANTUM_ENCRYPTION // NODE_88</div>
""", unsafe_allow_html=True)

# --- 6. HOLOGRAPHIC MAP (Cyber-Blue) ---
# 
st.markdown(f'<div class="stark-frame"><div class="tag" style="color:#8a00c2">// GLOBAL_DATA_FLOW</div>', unsafe_allow_html=True)

connections = [
    # Strictly Cyan and Purple lines. No other colors.
    dict(type='scattergeo', lat=[40.7, 35.6], lon=[-74.0, 139.6], mode='lines', line=dict(width=2, color='#00f0ff')),
    dict(type='scattergeo', lat=[35.6, 1.3], lon=[139.6, 103.8], mode='lines', line=dict(width=2, color='#8a00c2')),
    dict(type='scattergeo', lat=[51.5, 40.7], lon=[-0.1, -74.0], mode='lines', line=dict(width=2, color='#00f0ff')),
]

map_fig = go.Figure(data=connections)
map_fig.update_geos(
    projection_type="orthographic", showcoastlines=True, coastlinecolor="#00f0ff",
    showland=True, landcolor="#020202", showocean=True, oceancolor="#000",
    showcountries=True, countrycolor="#111", bgcolor="rgba(0,0,0,0)",
    lataxis=dict(showgrid=True, gridcolor="#080808"), lonaxis=dict(showgrid=True, gridcolor="#080808")
)
map_fig.update_layout(height=450, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(map_fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 7. SIGNAL CHARTS (Cyberpunk Palette) ---
st.markdown(f'<div class="stark-frame"><div class="tag" style="color:#00f0ff">// TECHNICAL_INTERCEPT: {ticker_input}</div>', unsafe_allow_html=True)
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.5, 0.25, 0.25])

# Cyberpunk Candles: Cyan (Up) vs Neon Red (Down)
fig.add_trace(go.Candlestick(
    x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'],
    increasing_line_color='#00f0ff', decreasing_line_color='#ff0055', name='Price'
), row=1, col=1)

# Purple Volume
fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], marker_color='#8a00c2', opacity=0.6, name='Vol'), row=2, col=1)

# White Trendline
fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'].rolling(20).mean(), line=dict(color='white', width=1, dash='dot'), name='MA'), row=3, col=1)

fig.update_layout(template="plotly_dark", height=600, showlegend=False, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=True, gridcolor='#111')
st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 8. UNIFORM TELEMETRY MATRIX ---
st.markdown(f'<div class="stark-frame"><div class="tag" style="color:#fff">// FUNDAMENTAL_MATRIX_DUMP</div>', unsafe_allow_html=True)
st.markdown('<div class="telemetry-grid">', unsafe_allow_html=True)

for key, value in info.items():
    if value and len(str(value)) < 25:
        # Uniform Cyber-Blue style for a clean "Matrix" look
        st.markdown(f"""
            <div class="telemetry-tile">
                <div class="tag">{str(key).upper()}</div>
                <div class="val">{str(value)}</div>
            </div>
        """, unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)
