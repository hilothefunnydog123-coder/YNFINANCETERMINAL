import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# --- 1. HUD ARCHITECTURE (STARK THEME) ---
st.set_page_config(layout="wide", page_title="STARK_CORE_v1", initial_sidebar_state="collapsed")

def apply_stark_ui():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
        .stApp { background-color: #000000; color: #00ffff; font-family: 'JetBrains Mono', monospace; }
        
        /* STICKY HUD HEADER */
        [data-testid="stHeader"] { background: rgba(0,0,0,0.9); border-bottom: 1px solid #00ffff; }
        .sticky-hud {
            position: sticky; top: 0; z-index: 9999; 
            background: #000; padding: 15px; border-bottom: 2px solid #00ffff;
            box-shadow: 0 0 30px rgba(0, 255, 255, 0.4);
        }

        /* FULL-SCREEN DATA MATRIX (100+ LINES) */
        .telemetry-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 2px; width: 100%; margin-top: 30px;
        }
        .telemetry-tile {
            background: rgba(0, 255, 255, 0.02);
            border: 1px solid rgba(0, 255, 255, 0.15);
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

apply_stark_ui()

# --- 2. THE STICKY HUD COMMANDER ---
st.markdown(f"""
    <div class="sticky-hud">
        <h2 style='margin:0; color:#00ffff; letter-spacing: 10px;'>// J.A.R.V.I.S._OS_CORE: {datetime.now().strftime('%H:%M:%S')}</h2>
    </div>
""", unsafe_allow_html=True)

# --- 3. DATA INTERCEPT ---
ticker = st.sidebar.text_input("CMD_INPUT", "NVDA").upper()
stock = yf.Ticker(ticker)
hist = stock.history(period="1d", interval="1m")
info = stock.info

# --- 4. THE J.A.R.V.I.S. HOLOGRAPHIC MAP ---
# st.markdown("### // GLOBAL_NODE_SURVEILLANCE")

# Real coordinates for connection lines (Routes)
routes = [
    dict(type='scattergeo', lat=[40.71, 35.67], lon=[-74.00, 139.65], mode='lines', line=dict(width=2, color='#00ffff')),
    dict(type='scattergeo', lat=[51.50, 1.35], lon=[-0.12, 103.82], mode='lines', line=dict(width=2, color='#00ffff')),
    dict(type='scattergeo', lat=[25.20, 22.39], lon=[55.27, 114.10], mode='lines', line=dict(width=2, color='#00ff66')),
]

map_fig = go.Figure(data=routes)
map_fig.update_geos(
    projection_type="orthographic",
    showcoastlines=True, coastlinecolor="#004444",
    showland=True, landcolor="#000000",
    showocean=True, oceancolor="#000000",
    showlakes=False,
    showcountries=True, countrycolor="#002222",
    bgcolor="black"
)
map_fig.update_layout(
    height=500, margin=dict(l=0, r=0, t=0, b=0),
    paper_bgcolor="black", plot_bgcolor="black"
)
st.plotly_chart(map_fig, use_container_width=True)

# --- 5. THE TRI-STACK SIGNAL CHARTS ---
st.markdown("### // QUANTUM_SIGNAL_STACK")
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.01)

fig.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'],
                             low=hist['Low'], close=hist['Close']), row=1, col=1)
fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], marker_color='#00ffff'), row=2, col=1)
fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'].rolling(14).mean(), line_color='#00ff66'), row=3, col=1)

fig.update_layout(template="plotly_dark", height=500, showlegend=False, 
                  xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0),
                  plot_bgcolor='black', paper_bgcolor='black')
st.plotly_chart(fig, use_container_width=True)

# --- 6. THE 100+ LINE FULL-SCREEN TELEMETRY GRID ---
st.markdown("### // RAW_TELEMETRY_DUMP")
st.markdown('<div class="telemetry-grid">', unsafe_allow_html=True)

for key, value in info.items():
    if value and len(str(value)) < 45:
        st.markdown(f"""
            <div class="telemetry-tile">
                <div class="tag">{str(key).upper()}</div>
                <div class="val">{str(value)}</div>
            </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
