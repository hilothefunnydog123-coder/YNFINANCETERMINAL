import streamlit as st
import yfinance as yf
import pandas as pd
import pydeck as pdk
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# --- 1. HUD CORE ARCHITECTURE ---
st.set_page_config(layout="wide", page_title="SOVEREIGN_HUD", initial_sidebar_state="collapsed")

def apply_stark_ui():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
        
        /* Global Reset */
        .stApp { background-color: #000000; color: #00ffff; font-family: 'JetBrains Mono', monospace; }
        
        /* STICKY HUD HEADER */
        [data-testid="stHeader"] { background: rgba(0,0,0,0.9); border-bottom: 1px solid #00ffff; }
        .sticky-header {
            position: sticky; top: 0; z-index: 999; 
            background: #000; padding: 10px 0; border-bottom: 2px solid #00ffff;
            box-shadow: 0 0 20px rgba(0, 255, 255, 0.4);
        }

        /* DATA MATRIX - FULL WIDTH PHOTO STYLE */
        .data-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 2px; width: 100%;
        }
        .data-tile {
            background: rgba(0, 255, 255, 0.03);
            border: 1px solid rgba(0, 255, 255, 0.2);
            padding: 12px; transition: 0.3s;
        }
        .data-tile:hover { background: rgba(0, 255, 255, 0.1); border-color: #00ffff; }
        .tag { color: #444; font-size: 10px; text-transform: uppercase; }
        .val { color: #00ffff; font-weight: bold; font-size: 14px; margin-top: 5px; }

        /* Removing Mapbox/OpenStreetMap textures */
        .deckgl-container { background-color: #000 !important; }
        </style>
    """, unsafe_allow_html=True)

apply_stark_ui()

# --- 2. THE STICKY HUD COMMANDER ---
st.markdown(f"""
    <div class="sticky-header">
        <h2 style='margin:0; color:#00ffff; letter-spacing: 5px;'>// SOVEREIGN_STARK_HUD: {datetime.now().strftime('%H:%M:%S')}</h2>
    </div>
""", unsafe_allow_html=True)

# --- 3. DATA INTERCEPT ---
ticker = st.sidebar.text_input("INPUT_CMD", "NVDA").upper()
stock = yf.Ticker(ticker)
hist = stock.history(period="1d", interval="1m")
info = stock.info

# --- 4. THE HOLOGRAPHIC VECTOR MAP ---
# st.markdown("### // GLOBAL_NODE_SURVEILLANCE")

# Real-world node links for the "Lines Across" look
links = pd.DataFrame([
    {"s": [-74.00, 40.71], "e": [139.6, 35.67]}, # NY-Tokyo
    {"s": [103.8, 1.35], "e": [2.35, 48.85]},   # Singapore-Paris
    {"s": [55.27, 25.20], "e": [114.1, 22.39]}, # Dubai-HK
    {"s": [-0.12, 51.50], "e": [-118.2, 34.0]}  # London-LA
])

# Use GeoJSON to build a holographic wireframe world
COUNTRIES = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"

st.pydeck_chart(pdk.Deck(
    map_style=None, # Kills standard map tiles
    initial_view_state=pdk.ViewState(latitude=20, longitude=10, zoom=1.1, pitch=45),
    layers=[
        # The Holographic Wireframe World
        pdk.Layer(
            "GeoJsonLayer",
            COUNTRIES,
            stroked=True, filled=True,
            get_fill_color=[0, 255, 255, 10], # Semi-transparent blue fill
            get_line_color=[0, 255, 255, 80], # Glowing cyan borders
            get_line_width=2
        ),
        # 3D Arcing Connection Lines
        pdk.Layer(
            "ArcLayer", data=links, get_source_position="s", get_target_position="e",
            get_width=3, get_source_color="[0, 255, 255, 200]", get_target_color="[0, 255, 100, 200]",
            great_circle=True
        )
    ]
))

# --- 5. TRI-STACK QUANTUM CHARTS (Back-to-Back) ---
st.markdown("### // SIGNAL_ANALYSIS_STACK")
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

# --- 6. THE 100-LINE FULL-SCREEN DATA WALL (Photo Style) ---
st.markdown("### // RAW_TELEMETRY_DUMP")
st.markdown('<div class="data-grid">', unsafe_allow_html=True)

# This loop grabs 100+ real data points from the yfinance object
for key, value in info.items():
    if value and len(str(value)) < 40:
        st.markdown(f"""
            <div class="data-tile">
                <div class="tag">{str(key).upper()}</div>
                <div class="val">{str(value)}</div>
            </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
