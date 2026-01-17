import streamlit as st
import yfinance as yf
import pandas as pd
import pydeck as pdk
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# --- 1. HUD ARCHITECTURE (Sticky Header & Iron Man Theme) ---
st.set_page_config(layout="wide", page_title="SOVEREIGN_HUD", initial_sidebar_state="collapsed")

def apply_iron_man_ui():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
        
        /* Global Reset */
        .stApp { background-color: #000000; color: #ff9900; font-family: 'JetBrains Mono', monospace; }
        
        /* FIX: STICKY HEADER */
        [data-testid="stHeader"] { background: rgba(0,0,0,0.9); border-bottom: 1px solid #ff9900; }
        
        /* FULL SCREEN DATA BLOCKS */
        .block-container { padding: 0rem 1rem; max-width: 100%; }
        
        /* THE ORANGE BOX MATRIX (Photo Style) */
        .data-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 5px;
            width: 100%;
        }
        .orange-tile {
            background: rgba(255, 153, 0, 0.05);
            border: 1px solid #ff9900;
            padding: 10px;
            font-size: 11px;
            text-align: left;
        }
        .label { color: #555; font-size: 9px; text-transform: uppercase; }
        .value { color: #ff9900; font-weight: bold; margin-top: 2px; }

        /* Kills the OpenStreetMap feel */
        .deckgl-container { background-color: #000 !important; }
        </style>
    """, unsafe_allow_html=True)

apply_iron_man_ui()

# --- 2. THE STICKY COMMAND STRIP ---
st.markdown(f"""
    <div style='position: sticky; top: 0; z-index: 99; background: #000; padding: 10px 0; border-bottom: 2px solid #ff9900;'>
        <h2 style='margin:0; color:#ff9900;'>// SYSTEM_HUD: {datetime.now().strftime('%H:%M:%S')}</h2>
    </div>
""", unsafe_allow_html=True)

# --- 3. DATA INTERCEPT ---
ticker = st.sidebar.text_input("CMD", "NVDA").upper()
stock = yf.Ticker(ticker)
hist = stock.history(period="1d", interval="1m")
info = stock.info

# --- 4. THE TECH-NEURAL MAP (Iron Man Arc System) ---
# We use a completely black map style with glowing arcs
st.markdown("### // GLOBAL_NODE_FLOW")
flow_data = pd.DataFrame([
    {"s": [-74.00, 40.71], "e": [139.6, 35.67], "v": 100}, # NY -> Tokyo
    {"s": [103.8, 1.35], "e": [-0.12, 51.50], "v": 80},   # Singapore -> London
    {"s": [55.27, 25.20], "e": [114.1, 22.39], "v": 60}   # Dubai -> Hong Kong
])

st.pydeck_chart(pdk.Deck(
    map_style=None, # Kills OpenStreetMap
    initial_view_state=pdk.ViewState(latitude=20, longitude=30, zoom=1.2, pitch=50),
    layers=[
        pdk.Layer("ArcLayer", data=flow_data, get_source_position="s", get_target_position="e",
                  get_width=4, get_source_color="[255, 153, 0, 180]", get_target_color="[0, 255, 255, 180]",
                  great_circle=True),
        pdk.Layer("ScatterplotLayer", data=flow_data, get_position="s", get_radius=400000,
                  get_fill_color="[255, 153, 0, 255]", stroked=True, get_line_color="[255,255,255]")
    ]
))

# --- 5. TRI-STACK CHARTS (Back-to-Back) ---
st.markdown("### // QUANTUM_FLOW_ANALYSIS")
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02)
fig.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'],
                             low=hist['Low'], close=hist['Close']), row=1, col=1)
fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], marker_color='#ff9900'), row=2, col=1)
fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'].rolling(14).mean(), line_color='#00ffff'), row=3, col=1)

fig.update_layout(template="plotly_dark", height=600, showlegend=False, 
                  xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0),
                  plot_bgcolor='black', paper_bgcolor='black')
st.plotly_chart(fig, use_container_width=True)

# --- 6. THE 100-LINE FULL-SCREEN MATRIX (Scroll Down for the Photo Look) ---
st.markdown("### // RAW_DATA_INTERCEPT")
st.markdown('<div class="data-grid">', unsafe_allow_html=True)

# This loop pulls EVERY available data point to fill the screen
for key, value in info.items():
    if value and len(str(value)) < 50:
        st.markdown(f"""
            <div class="orange-tile">
                <div class="label">{str(key).upper()}</div>
                <div class="value">{str(value)}</div>
            </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
