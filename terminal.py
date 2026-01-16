import streamlit as st
import yfinance as yf
import pandas as pd
import pydeck as pdk
import plotly.graph_objects as go
from datetime import datetime

# --- 1. THE GLASS-NEON DESIGN SYSTEM ---
st.set_page_config(layout="wide", page_title="SOVEREIGN_V46", page_icon="🛰️")

def apply_insane_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
        
        /* Global Background & Font */
        .stApp {
            background: radial-gradient(circle at center, #0a0a0a 0%, #000000 100%);
            color: #00ff41;
            font-family: 'JetBrains Mono', monospace;
        }

        /* The "Glass" Metric Cards */
        [data-testid="stMetric"] {
            background: rgba(0, 255, 65, 0.03);
            border-left: 5px solid #00ff41;
            border-top: 1px solid rgba(0, 255, 65, 0.2);
            padding: 20px;
            border-radius: 4px;
            box-shadow: 0 0 20px rgba(0, 255, 65, 0.05);
            transition: all 0.3s ease;
        }
        [data-testid="stMetric"]:hover {
            background: rgba(0, 255, 65, 0.08);
            transform: translateX(5px);
            box-shadow: 0 0 30px rgba(0, 255, 65, 0.15);
        }

        /* Floating Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: rgba(5, 5, 5, 0.95);
            border-right: 1px solid #00ff41;
        }

        /* Custom Header Neon Text */
        .neon-header {
            color: #00ff41;
            text-transform: uppercase;
            letter-spacing: 5px;
            text-shadow: 0 0 10px #00ff41, 0 0 20px #00ff41;
            border-bottom: 1px solid #00ff41;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }
        </style>
    """, unsafe_allow_html=True)

apply_insane_style()

# --- 2. HEADER & LOGO ---
st.markdown("<h1 class='neon-header'>// SOVEREIGN.OS_TERMINAL_V46</h1>", unsafe_allow_html=True)

# --- 3. LIVE HUD (Heads-Up Display) ---
if 'ticker' not in st.session_state: st.session_state.ticker = "NVDA"

with st.sidebar:
    st.markdown("### 📡 SYSTEM_LINK")
    st.session_state.ticker = st.text_input("INPUT_TARGET_SYMBOL", value=st.session_state.ticker).upper()
    st.markdown("---")
    st.write(f"SYSTEM_TIME: {datetime.now().strftime('%H:%M:%S')}")
    st.write("SAT_LINK: **CONNECTED**")
    st.write("ENCRYPTION: **AES-256**")

# --- 4. REAL-TIME DATA FUSION ---
stock = yf.Ticker(st.session_state.ticker)
hist = stock.history(period="1d", interval="1m")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("SPOT_PRICE", f"${hist['Close'].iloc[-1]:.2f}", f"{((hist['Close'].iloc[-1]/hist['Open'].iloc[0])-1)*100:.2f}%")
with col2:
    st.metric("VOL_TOTAL", f"{stock.info.get('volume', 0):,}")
with col3:
    st.metric("ALPHA_SCORE", "8.92", "+0.4")
with col4:
    st.metric("RISK_INDEX", "LOW", "-12%", delta_color="inverse")

# --- 5. THE "INSANE" CANDLESTICK RADAR ---
st.markdown("### ⚡ QUANTUM_PRICE_FLOW")
fig = go.Figure(data=[go.Candlestick(
    x=hist.index,
    open=hist['Open'], high=hist['High'],
    low=hist['Low'], close=hist['Close'],
    increasing_line_color='#00ff41', decreasing_line_color='#ff003c'
)])
fig.update_layout(
    template="plotly_dark",
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    xaxis_rangeslider_visible=False,
    margin=dict(l=0, r=0, t=0, b=0),
    height=400
)
st.plotly_chart(fig, use_container_width=True)

# --- 6. MARITIME SURVEILLANCE LAYER ---
st.markdown("### 🛰️ GLOBAL_AIS_INTERCEPT")
dummy_tankers = pd.DataFrame([
    {"name": "VLCC_ARABIA", "lat": 25.12, "lon": 55.23, "load": 95},
    {"name": "NORDIC_STAR", "lat": 1.29, "lon": 103.85, "load": 40},
    {"name": "GULF_RUNNER", "lat": 26.55, "lon": 50.31, "load": 10}
])

st.pydeck_chart(pdk.Deck(
    map_style=pdk.map_styles.CARTO_DARK,
    initial_view_state=pdk.ViewState(latitude=15, longitude=30, zoom=1.5, pitch=50),
    layers=[
        pdk.Layer(
            "ColumnLayer",
            data=dummy_tankers,
            get_position="[lon, lat]",
            get_elevation="load * 10000",
            elevation_scale=10,
            radius=100000,
            get_fill_color="[0, 255, 65, 150]",
            pickable=True,
            auto_highlight=True,
        )
    ],
    tooltip={"text": "Vessel: {name}\nCargo Load: {load}%"}
))
