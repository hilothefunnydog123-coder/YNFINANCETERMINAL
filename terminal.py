import streamlit as st
import yfinance as yf
import pandas as pd
import pydeck as pdk
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# --- 1. HUD ARCHITECTURE (STRICT STARK THEME) ---
st.set_page_config(layout="wide", page_title="SOVEREIGN_HUD", initial_sidebar_state="collapsed")

def apply_stark_core_ui():
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

        /* DATA MATRIX - FULL WIDTH TELEMETRY */
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

        /* KILL MAP TILES */
        .deckgl-container { background-color: #000 !important; }
        </style>
    """, unsafe_allow_html=True)

apply_stark_core_ui()

# --- 2. STICKY COMMAND HUD ---
st.markdown(f"""
    <div class="sticky-hud">
        <h2 style='margin:0; color:#00ffff; letter-spacing: 10px;'>// STARK_CORE_OS: {datetime.now().strftime('%H:%M:%S')}</h2>
    </div>
""", unsafe_allow_html=True)

# --- 3. DATA INTERCEPT ---
ticker = st.sidebar.text_input("CMD_INPUT", "NVDA").upper()
stock = yf.Ticker(ticker)
hist = stock.history(period="1d", interval="1m")
info = stock.info

# --- 4. HOLOGRAPHIC VECTOR MAP (ZERO-PRESET) ---
st.markdown("### // GLOBAL_NODE_SURVEILLANCE")

# Custom arc routes for the "Jarvis Link" look
nodes = pd.DataFrame([
    {"s": [-74.0, 40.7], "e": [139.6, 35.6]}, # NY-Tokyo
    {"s": [103.8, 1.3], "e": [2.35, 48.8]},   # Singapore-Paris
    {"s": [55.2, 25.2], "e": [114.1, 22.3]},  # Dubai-HK
    {"s": [-118.2, 34.0], "e": [-0.12, 51.5]} # LA-London
])

# Raw GeoJSON to "Draw" the world borders manually
GEO_JSON = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"

st.pydeck_chart(pdk.Deck(
    map_style=None, # COMPLETELY DELETES OPENSTREETMAP
    initial_view_state=pdk.ViewState(latitude=20, longitude=10, zoom=1.1, pitch=45),
    layers=[
        # THE WIREFRAME WORLD
        pdk.Layer(
            "GeoJsonLayer",
            GEO_JSON,
            stroked=True, filled=True,
            get_fill_color=[0, 255, 255, 5], 
            get_line_color=[0, 255, 255, 100], 
            get_line_width=2
        ),
        # 3D HOLOGRAPHIC ARCS
        pdk.Layer(
            "ArcLayer", data=nodes, get_source_position="s", get_target_position="e",
            get_width=4, get_source_color="[0, 255, 255, 255]", get_target_color="[0, 255, 100, 255]",
            great_circle=True
        )
    ]
))

# --- 5. THE TRI-STACK ANALYTICS CHARTS ---
st.markdown("### // QUANTUM_SIGNAL_STACK")
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.01)

# Price Action
fig.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'],
                             low=hist['Low'], close=hist['Close']), row=1, col=1)
# Volume Flow
fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], marker_color='#00ffff'), row=2, col=1)
# Signal Trendline
fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'].rolling(14).mean(), line_color='#00ff66'), row=3, col=1)

fig.update_layout(template="plotly_dark", height=500, showlegend=False, 
                  xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0),
                  plot_bgcolor='black', paper_bgcolor='black')
st.plotly_chart(fig, use_container_width=True)

# --- 6. THE 100+ LINE FULL-SCREEN TELEMETRY GRID ---
st.markdown("### // RAW_TELEMETRY_DUMP")
st.markdown('<div class="telemetry-grid">', unsafe_allow_html=True)

# Loop to pull every available real data point from yfinance
for key, value in info.items():
    if value and len(str(value)) < 40:
        st.markdown(f"""
            <div class="telemetry-tile">
                <div class="tag">{str(key).upper()}</div>
                <div class="val">{str(value)}</div>
            </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
