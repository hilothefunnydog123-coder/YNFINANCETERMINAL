import streamlit as st
import yfinance as yf
import pandas as pd
import pydeck as pdk
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# --- 1. HUD ARCHITECTURE (STRICT STARK THEME) ---
st.set_page_config(layout="wide", page_title="SOVEREIGN_HUD", initial_sidebar_state="collapsed")

def apply_stark_zero_ui():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
        
        /* Global UI Blackout */
        .stApp { background-color: #000000; color: #00ffff; font-family: 'JetBrains Mono', monospace; }
        
        /* FIX: STICKY HUD */
        [data-testid="stHeader"] { background: rgba(0,0,0,0.9); border-bottom: 1px solid #00ffff; }
        .sticky-hud {
            position: sticky; top: 0; z-index: 9999; 
            background: #000; padding: 15px; border-bottom: 2px solid #00ffff;
            box-shadow: 0 0 30px rgba(0, 255, 255, 0.5);
        }

        /* DATA MATRIX - FULL WIDTH TELEMETRY */
        .block-container { padding: 0rem 1rem; max-width: 100%; }
        .telemetry-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
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
            box-shadow: inset 0 0 10px #00ffff;
        }
        .tag { color: #333; font-size: 9px; text-transform: uppercase; letter-spacing: 2px; }
        .val { color: #00ffff; font-weight: bold; font-size: 14px; margin-top: 5px; }

        /* KILLS ALL MAP TILES / PROVIDERS */
        .deckgl-container { background-color: #000 !important; }
        </style>
    """, unsafe_allow_html=True)

apply_stark_zero_ui()

# --- 2. THE STICKY HUD COMMANDER ---
st.markdown(f"""
    <div class="sticky-hud">
        <h2 style='margin:0; color:#00ffff; letter-spacing: 8px;'>// SOVEREIGN_STARK_ZERO: {datetime.now().strftime('%H:%M:%S')}</h2>
    </div>
""", unsafe_allow_html=True)

# --- 3. DATA INTERCEPT (Real-Time) ---
ticker = st.sidebar.text_input("CMD_INPUT", "NVDA").upper()
stock = yf.Ticker(ticker)
hist = stock.history(period="1d", interval="1m")
info = stock.info

# --- 4. THE CUSTOM HOLOGRAPHIC VECTOR MAP ---
# [Image of a holographic wireframe world map with glowing cyan country outlines and 3D data arcs]
st.markdown("### // GLOBAL_NETWORK_SURVEILLANCE")

# Custom connection links for the "Lines Across" look
nodes = pd.DataFrame([
    {"s": [-74.0, 40.7], "e": [139.6, 35.6], "id": "NY_TOK"},
    {"s": [103.8, 1.3], "e": [2.35, 48.8], "id": "SG_PAR"},
    {"s": [55.2, 25.2], "e": [114.1, 22.3], "id": "DXB_HK"},
    {"s": [-118.2, 34.0], "e": [-0.12, 51.5], "id": "LA_LDN"}
])

# We use a raw GeoJSON file to draw our OWN map borders
GEO_JSON = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"

st.pydeck_chart(pdk.Deck(
    map_style=None, # COMPLETELY REMOVES OPENSTREETMAP
    initial_view_state=pdk.ViewState(latitude=15, longitude=10, zoom=1.1, pitch=45),
    layers=[
        # CUSTOM HOLOGRAPHIC LANDMASSES
        pdk.Layer(
            "GeoJsonLayer",
            GEO_JSON,
            stroked=True, filled=True,
            get_fill_color=[0, 255, 255, 5], # Deep space blue fill
            get_line_color=[0, 255, 255, 120], # Glowing cyan borders
            get_line_width=3
        ),
        # 3D DATA ARCS
        pdk.Layer(
            "ArcLayer", data=nodes, get_source_position="s", get_target_position="e",
            get_width=4, get_source_color="[0, 255, 255, 255]", get_target_color="[0, 255, 100, 255]",
            great_circle=True
        )
    ],
    tooltip={"text": "LINK_ID: {id}"}
))

# --- 5. THE TRI-STACK QUANTUM CHARTS ---
st.markdown("### // SIGNAL_STACK_FLOW")
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.01)

# Price Action
fig.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'],
                             low=hist['Low'], close=hist['Close']), row=1, col=1)
# Institutional Volume
fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], marker_color='#00ffff'), row=2, col=1)
# Alpha Signal Line
fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'].rolling(14).mean(), line_color='#00ff66'), row=3, col=1)

fig.update_layout(template="plotly_dark", height=500, showlegend=False, 
                  xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0),
                  plot_bgcolor='black', paper_bgcolor='black')
st.plotly_chart(fig, use_container_width=True)

# --- 6. THE 100+ LINE TELEMETRY MATRIX (Full Screen) ---
st.markdown("### // RAW_TELEMETRY_DUMP")
st.markdown('<div class="telemetry-grid">', unsafe_allow_html=True)

# This loop pulls 100+ REAL data points from the yfinance object
for key, value in info.items():
    if value and len(str(value)) < 40:
        st.markdown(f"""
            <div class="telemetry-tile">
                <div class="tag">{str(key).upper()}</div>
                <div class="val">{str(value)}</div>
            </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
