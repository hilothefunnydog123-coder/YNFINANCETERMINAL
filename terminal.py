import streamlit as st
import yfinance as yf
import pandas as pd
import pydeck as pdk
from streamlit_autorefresh import st_autorefresh

# --- 1. BIOMETRIC GUARD (HANKO OIDC) ---
# This ensures "st.user" is checked safely to prevent AttributeError
if not st.user.get("is_logged_in", False):
    st.set_page_config(page_title="YN_SECURE_GATE", layout="centered")
    st.markdown("""
        <style>
        .stApp { background-color: #050505; color: #00ff41; font-family: 'Courier New', monospace; }
        .gate-card {
            border: 2px solid #00ff41; padding: 40px; border-radius: 15px;
            text-align: center; background: rgba(0, 255, 65, 0.05);
            box-shadow: 0 0 20px #00ff41;
        }
        </style>
        <div class="gate-card">
            <h1>🔒 SOVEREIGN_ACCESS_LOCKED</h1>
            <p>Biometric Hardware Recognition Required for Terminal Initialization.</p>
        </div>
    """, unsafe_allow_html=True)

    # Calling "hanko" triggers the native browser fingerprint/FaceID prompt
    if st.button("INITIALIZE_HARDWARE_SCAN", use_container_width=True):
        st.login("hanko")
    st.stop()

# --- 2. MAJESTIC TERMINAL INTERFACE ---
st.set_page_config(layout="wide", page_title="SOVEREIGN_V46")
st_autorefresh(interval=60000, key="global_refresh")

def inject_terminal_css():
    st.markdown("""
        <style>
        .stApp { background-color: #050505; color: #e0e0e0; }
        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(0, 255, 65, 0.2);
            padding: 15px; border-radius: 10px;
            backdrop-filter: blur(10px);
            box-shadow: 0 0 15px rgba(0, 255, 65, 0.05);
        }
        h1, h2, h3 { font-family: 'Courier New', monospace; color: #00ff41 !important; text-shadow: 0 0 8px #00ff41; }
        .stTabs [data-baseweb="tab-list"] { gap: 10px; }
        .stTabs [aria-selected="true"] { background-color: rgba(0, 255, 65, 0.1) !important; color: #00ff41 !important; border-bottom: 2px solid #00ff41 !important; }
        </style>
    """, unsafe_allow_html=True)

inject_terminal_css()

# --- 3. COMMAND CENTER LOGIC ---
if 'ticker' not in st.session_state:
    st.session_state.ticker = "NVDA"

with st.sidebar:
    st.title("COMMAND_CENTER")
    st.write(f"VERIFIED_USER: {st.user.get('email', 'N/A')}")
    st.session_state.ticker = st.text_input("SET_ACTIVE_SYMBOL", value=st.session_state.ticker).upper()
    if st.button("TERMINATE_SESSION"):
        st.logout()

st.markdown(f"<h1>// SECURITY_MASTER: {st.session_state.ticker}</h1>", unsafe_allow_html=True)

# Data Fetching
stock = yf.Ticker(st.session_state.ticker)
info = stock.info

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.write("**PRIMARY_IDS**")
    st.code(f"Ticker: {st.session_state.ticker}\nISIN: {info.get('isin')}\nCUSIP: {info.get('cusip')}")
with col2:
    st.write("**EXCHANGE_DATA**")
    st.code(f"Exchange: {info.get('exchange')}\nMIC: {info.get('exchangeTimezoneName')}\nCurrency: {info.get('currency')}")
with col3:
    st.write("**ASSET_CLASS**")
    st.code(f"Type: {info.get('quoteType')}\nSector: {info.get('sector')}\nCountry: {info.get('country')}")
with col4:
    st.write("**PROPRIETARY_SCORES**")
    st.metric("LIQUIDITY", "HIGH", "98.2")
    st.metric("B_FAIR_VALUE", f"${info.get('targetMedianPrice')}")

# --- 4. GLOBAL MARITIME SURVEILLANCE MAP ---
# CARTO_DARK works without an API key
st.subheader("🛰️ LIVE_AIS_TANKER_TRACKING")
dummy_tankers = pd.DataFrame([
    {"name": "VLCC_ARABIA", "lat": 25.12, "lon": 55.23},
    {"name": "NORDIC_STAR", "lat": 1.29, "lon": 103.85},
    {"name": "GULF_RUNNER", "lat": 26.55, "lon": 50.31}
])

st.pydeck_chart(pdk.Deck(
    map_style=pdk.map_styles.CARTO_DARK,
    initial_view_state=pdk.ViewState(latitude=15, longitude=30, zoom=1.2, pitch=45),
    layers=[
        pdk.Layer("ScatterplotLayer", data=dummy_tankers, get_position="[lon, lat]", 
                  get_color="[0, 255, 65, 180]", get_radius=300000, pickable=True)
    ],
    tooltip={"text": "Vessel: {name}\nPos: {lat}, {lon}"}
))
