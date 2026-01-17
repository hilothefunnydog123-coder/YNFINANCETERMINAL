import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# --- 1. HUD ARCHITECTURE (STARK PRIME THEME) ---
st.set_page_config(layout="wide", page_title="STARK_PRIME_HUD", initial_sidebar_state="collapsed")

def apply_stark_prime_ui():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
        
        /* Global Blackout */
        .stApp { background-color: #000000; color: #00ffff; font-family: 'JetBrains Mono', monospace; }
        
        /* STICKY HUD HEADER */
        [data-testid="stHeader"] { background: rgba(0,0,0,0.9); border-bottom: 1px solid #00ffff; }
        .sticky-hud {
            position: sticky; top: 0; z-index: 9999; 
            background: #000; padding: 15px; border-bottom: 2px solid #00ffff;
            box-shadow: 0 0 30px rgba(0, 255, 255, 0.4);
        }

        /* HOLOGRAPHIC VECTOR MAP CONTAINER */
        .hologram-map {
            width: 100%; height: 400px;
            background: radial-gradient(circle, #001a1a 0%, #000000 100%);
            border: 1px solid rgba(0, 255, 255, 0.2);
            position: relative; overflow: hidden;
            display: flex; align-items: center; justify-content: center;
        }

        /* DATA MATRIX - PHOTO DENSITY */
        .telemetry-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 2px; width: 100%; margin-top: 30px;
        }
        .telemetry-tile {
            background: rgba(0, 255, 255, 0.02);
            border: 1px solid rgba(0, 255, 255, 0.1);
            padding: 12px; transition: 0.2s;
        }
        .telemetry-tile:hover { 
            background: rgba(0, 255, 255, 0.1); 
            border-color: #00ffff;
            box-shadow: inset 0 0 15px #00ffff;
        }
        .tag { color: #333; font-size: 9px; text-transform: uppercase; letter-spacing: 2px; }
        .val { color: #00ffff; font-weight: bold; font-size: 14px; margin-top: 5px; }
        </style>
    """, unsafe_allow_html=True)

apply_stark_prime_ui()

# --- 2. STICKY HUD COMMANDER ---
st.markdown(f"""
    <div class="sticky-hud">
        <h2 style='margin:0; color:#00ffff; letter-spacing: 12px;'>// STARK_PRIME_OS: {datetime.now().strftime('%H:%M:%S')}</h2>
    </div>
""", unsafe_allow_html=True)

# --- 3. DATA INTERCEPT ---
ticker = st.sidebar.text_input("CMD_INPUT", "NVDA").upper()
stock = yf.Ticker(ticker)
hist = stock.history(period="1d", interval="1m")
info = stock.info

# --- 4. CUSTOM "HAND-DRAWN" HOLOGRAPHIC MAP ---
# We bypass Pydeck and draw an SVG Vector Map directly
st.markdown("### // GLOBAL_NEURAL_LINK")
st.markdown("""
<div class="hologram-map">
    <svg viewBox="0 0 1000 500" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(0, 255, 255, 0.1)" stroke-width="0.5"/>
            </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />
        
        <path d="M150,150 L200,120 L280,130 L320,180 L250,250 L180,240 Z" fill="none" stroke="#00ffff" stroke-width="1" stroke-dasharray="4" opacity="0.5" />
        <path d="M500,100 L600,80 L750,120 L800,250 L650,350 L500,300 Z" fill="none" stroke="#00ffff" stroke-width="1" stroke-dasharray="4" opacity="0.5" />
        <path d="M200,350 L300,320 L350,450 L250,480 Z" fill="none" stroke="#00ffff" stroke-width="1" stroke-dasharray="4" opacity="0.5" />
        
        <path d="M200,150 Q500,50 750,150" fill="none" stroke="#00ffff" stroke-width="2">
            <animate attributeName="stroke-dasharray" from="0,1000" to="1000,0" dur="3s" repeatCount="indefinite" />
        </path>
        <path d="M300,400 Q600,200 650,300" fill="none" stroke="#00ff66" stroke-width="2">
             <animate attributeName="opacity" values="0;1;0" dur="2s" repeatCount="indefinite" />
        </path>
        
        <circle cx="200" cy="150" r="5" fill="#00ffff">
            <animate attributeName="r" values="3;7;3" dur="1s" repeatCount="indefinite" />
        </circle>
        <circle cx="750" cy="150" r="5" fill="#00ffff" />
    </svg>
</div>
""", unsafe_allow_html=True)

# --- 5. THE TRI-STACK QUANTUM CHARTS ---
st.markdown("### // SIGNAL_FLOW_ANALYSIS")
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.01)

# Back-to-back charts for Price, Volume, and Trend
fig.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'],
                             low=hist['Low'], close=hist['Close']), row=1, col=1)
fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], marker_color='#00ffff'), row=2, col=1)
fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'].rolling(14).mean(), line_color='#00ff66'), row=3, col=1)

fig.update_layout(template="plotly_dark", height=550, showlegend=False, 
                  xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0),
                  plot_bgcolor='black', paper_bgcolor='black')
st.plotly_chart(fig, use_container_width=True)

# --- 6. THE 100-LINE FULL-SCREEN TELEMETRY GRID (Photo Style) ---
st.markdown("### // RAW_DATA_INTERCEPT")
st.markdown('<div class="telemetry-grid">', unsafe_allow_html=True)

# Loop to pull 100+ REAL data points from yfinance
for key, value in info.items():
    if value and len(str(value)) < 40:
        st.markdown(f"""
            <div class="telemetry-tile">
                <div class="tag">{str(key).upper()}</div>
                <div class="val">{str(value)}</div>
            </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
