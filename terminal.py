import streamlit as st
import yfinance as yf
import pandas as pd
import pydeck as pdk
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# --- 1. SYSTEM HUD ARCHITECTURE ---
st.set_page_config(layout="wide", page_title="SOVEREIGN_HUD", initial_sidebar_state="collapsed")

def apply_holographic_ui():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
        
        /* Global Reset to Pitch Black */
        .stApp { background-color: #000000; color: #00ffff; font-family: 'JetBrains Mono', monospace; }
        
        /* STICKY HUD HEADER */
        [data-testid="stHeader"] { background: rgba(0,0,0,0.9); border-bottom: 1px solid #00ffff; }
        .sticky-nav {
            position: sticky; top: 0; z-index: 999; 
            background: #000; padding: 10px; border-bottom: 2px solid #00ffff;
            box-shadow: 0 0 15px rgba(0, 255, 255, 0.2);
        }

        /* DATA MATRIX GRID - FULL SCREEN */
        .data-matrix {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 2px; width: 100%; margin-top: 20px;
        }
        .data-cell {
            background: rgba(0, 255, 255, 0.02);
            border: 1px solid rgba(0, 255, 255, 0.3);
            padding: 12px; transition: all 0.3s;
        }
        .data-cell:hover { background: rgba(0, 255, 255, 0.1); border-color: #00ffff; }
        .tag { color: #555; font-size: 10px; text-transform: uppercase; }
        .val { color: #00ffff; font-weight: bold; font-size: 14px; margin-top: 4px; }

        /* KILLS THE OPENSTREETMAP PROVIDER */
        .deckgl-container { background-color: #000 !important; }
        </style>
    """, unsafe_allow_html=True)

apply_holographic_ui()

# --- 2. THE STICKY HUD COMMANDER ---
st.markdown(f"""
    <div class="sticky-nav">
        <h2 style='margin:0; color:#00ffff; letter-spacing: 4px;'>// SOVEREIGN_OS_TERMINAL: {datetime.now().strftime('%H:%M:%S')}</h2>
    </div>
""", unsafe_allow_html=True)

# --- 3. DATA INTERCEPT (Direct Hook) ---
ticker = st.sidebar.text_input("INPUT_CMD", "TSLA").upper()
stock = yf.Ticker(ticker)
hist = stock.history(period="1d", interval="1m")
info = stock.info

# --- 4. THE HOLOGRAPHIC NEURAL MAP ---
# st.markdown("### // GLOBAL_NODE_INTERCEPT")

# Simulating high-tech connection paths between global data hubs
node_links = pd.DataFrame([
    {"s": [-74.00, 40.71], "e": [139.6, 35.67]}, # NY-Tokyo
    {"s": [103.8, 1.35], "e": [2.35, 48.85]},   # Singapore-Paris
    {"s": [55.27, 25.20], "e": [114.1, 22.39]}, # Dubai-HK
    {"s": [-118.2, 34.0], "e": [12.49, 41.89]}  # LA-Rome
])

st.pydeck_chart(pdk.Deck(
    map_style=None, # Pure black background, no "map" tiles
    initial_view_state=pdk.ViewState(latitude=20, longitude=20, zoom=1.1, pitch=50),
    layers=[
        # Glowing Arcs
        pdk.Layer("ArcLayer", data=node_links, get_source_position="s", get_target_position="e",
                  get_width=3, get_source_color="[0, 255, 255, 150]", get_target_color="[0, 255, 100, 150]",
                  great_circle=True),
        # Neural Nodes
        pdk.Layer("ScatterplotLayer", data=node_links, get_position="s", get_radius=300000,
                  get_fill_color="[0, 255, 255, 255]", stroked=True, get_line_color="[255, 255, 255]")
    ]
))

# --- 5. TRI-STACK QUANTUM CHARTS ---
st.markdown("### // PRICE_VOLUME_FLOW")
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.01)

# Price Action
fig.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'],
                             low=hist['Low'], close=hist['Close']), row=1, col=1)
# Volume Bars
fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], marker_color='#00ffff'), row=2, col=1)
# Signal Line
fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'].rolling(14).mean(), line_color='#00ff66'), row=3, col=1)

fig.update_layout(template="plotly_dark", height=500, showlegend=False, 
                  xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0),
                  plot_bgcolor='black', paper_bgcolor='black')
st.plotly_chart(fig, use_container_width=True)

# --- 6. THE 100+ LINE DATA MATRIX (Full Width) ---
st.markdown("### // RAW_TELEMETRY_DUMP")
st.markdown('<div class="data-matrix">', unsafe_allow_html=True)

# Extracts over 100 keys from the yfinance object to fill the lower half of the HUD
for key, value in info.items():
    if value and len(str(value)) < 40:
        st.markdown(f"""
            <div class="data-cell">
                <div class="tag">{str(key).upper()}</div>
                <div class="val">{str(value)}</div>
            </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
