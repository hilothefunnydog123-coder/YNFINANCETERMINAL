import streamlit as st
import yfinance as yf
import pandas as pd
import pydeck as pdk
from datetime import datetime

# --- 1. CORE SYSTEM THEME (CSS Injection) ---
st.set_page_config(layout="wide", page_title="SOVEREIGN_V46")

def apply_terminal_styling():
    st.markdown("""
        <style>
        /* Bloomberg-Style High Density Layout */
        .block-container { padding: 1rem 2rem; }
        
        /* The "Orange Box" Data Tiles */
        .terminal-box {
            background-color: rgba(255, 153, 0, 0.05);
            border: 1px solid #ff9900;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 10px;
            box-shadow: 0 0 10px rgba(255, 153, 0, 0.1);
        }
        
        .label { color: #888; font-size: 10px; text-transform: uppercase; letter-spacing: 2px; }
        .value { color: #ff9900; font-size: 20px; font-family: 'JetBrains Mono', monospace; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

apply_terminal_styling()

# --- 2. DATA ENGINE ---
ticker = st.sidebar.text_input("CMD >", "NVDA").upper()
stock = yf.Ticker(ticker)
info = stock.info

# --- 3. THE "ORANGE BOX" GRID ---
st.markdown(f"### // TERMINAL_FEED: {ticker}")
cols = st.columns(4)

metrics = [
    ("LAST_PRICE", f"${info.get('currentPrice', 0):.2f}"),
    ("DAY_CHANGE", f"{info.get('revenueGrowth', 0)*100:.2f}%"),
    ("MKT_CAP", f"{info.get('marketCap', 0)/1e9:.1f}B"),
    ("PE_RATIO", f"{info.get('trailingPE', 0):.2f}")
]

for i, (label, val) in enumerate(metrics):
    cols[i].markdown(f"""
        <div class="terminal-box">
            <div class="label">{label}</div>
            <div class="value">{val}</div>
        </div>
    """, unsafe_allow_html=True)

# --- 4. THE TECHY GLOBAL MAP (ArcLayer) ---
st.markdown("### // GLOBAL_AIS_SURVEILLANCE")

# Real coordinates for major shipping/finance hubs
arc_data = pd.DataFrame([
    {"s_lat": 40.71, "s_lon": -74.00, "e_lat": 51.50, "e_lon": -0.12}, # NY to London
    {"s_lat": 35.67, "s_lon": 139.65, "e_lat": 1.35, "e_lon": 103.81}, # Tokyo to Singapore
    {"s_lat": 25.20, "s_lon": 55.27, "e_lat": 52.36, "e_lon": 4.89}    # Dubai to Amsterdam
])

st.pydeck_chart(pdk.Deck(
    map_style=pdk.map_styles.CARTO_DARK, #
    initial_view_state=pdk.ViewState(latitude=25, longitude=10, zoom=1.5, pitch=45),
    layers=[
        pdk.Layer(
            "ArcLayer", # Draws futuristic connection lines
            data=arc_data,
            get_source_position="[s_lon, s_lat]",
            get_target_position="[e_lon, e_lat]",
            get_source_color="[255, 153, 0, 150]",
            get_target_color="[0, 255, 65, 150]",
            get_width=3,
        )
    ]
))
