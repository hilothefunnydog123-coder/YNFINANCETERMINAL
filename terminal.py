import streamlit as st
import yfinance as yf
import pandas as pd
import pydeck as pdk
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# --- 1. BLOOMBERG "GLASS" SYSTEM ---
st.set_page_config(layout="wide", page_title="SOVEREIGN_V46", initial_sidebar_state="collapsed")

def apply_insane_ui():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
        .stApp { background-color: #000000; color: #00ff41; font-family: 'JetBrains Mono', monospace; }
        .block-container { padding: 0.5rem 1rem; }
        
        /* High-Density Data Table Styling */
        .terminal-table { font-size: 10px; border-collapse: collapse; width: 100%; border: 1px solid #333; }
        .terminal-table td { border-bottom: 1px solid #222; padding: 2px 5px; }
        .ticker-header { background: #1a1a1a; color: #ff9900; padding: 5px; border-bottom: 2px solid #333; }
        
        /* Neon Metric Cards */
        [data-testid="stMetric"] { background: #0a0a0a; border: 1px solid #333; border-left: 4px solid #00ff41; padding: 10px; }
        </style>
    """, unsafe_allow_html=True)

apply_insane_ui()

# --- 2. DATA HUB (Real Tickers) ---
# Fetching 100+ lines of data for the 'insane' look
ticker = st.sidebar.text_input("COMMAND", "NVDA").upper()
stock = yf.Ticker(ticker)
hist_1m = stock.history(period="1d", interval="1m")
info = stock.info

# --- 3. THE "DUAL SCREEN" GRID SYSTEM ---
col_map, col_data = st.columns([2.5, 1])

with col_map:
    # A. TOP STRIP: REAL-TIME HUD
    st.markdown(f"<div class='ticker-header'>IDENT: {ticker} | LAST: {hist_1m['Close'].iloc[-1]:.2f} | B/A: {info.get('bid')}/{info.get('ask')} | VOL: {info.get('volume'):,}</div>", unsafe_allow_html=True)
    
    # B. HIGH-TECH ARCLAYER MAP (Direct Intercept Logic)
    # Using real ports as nodes for connection lines
    routes = pd.DataFrame([
        {"from_lat": 25.12, "from_lon": 55.23, "to_lat": 1.29, "to_lon": 103.85}, # Dubai to Singapore
        {"from_lat": 35.10, "from_lon": 129.04, "to_lat": 34.05, "to_lon": -118.24}, # Busan to LA
        {"from_lat": 51.92, "from_lon": 4.47, "to_lat": 40.71, "to_lon": -74.00} # Rotterdam to NY
    ])
    
    st.pydeck_chart(pdk.Deck(
        map_style=pdk.map_styles.CARTO_DARK,
        initial_view_state=pdk.ViewState(latitude=20, longitude=0, zoom=1.2, pitch=45),
        layers=[
            pdk.Layer("ArcLayer", data=routes, get_source_position="[from_lon, from_lat]", 
                      get_target_position="[to_lon, to_lat]", get_width=2,
                      get_source_color="[0, 255, 65, 80]", get_target_color="[255, 153, 0, 80]"),
            pdk.Layer("ScatterplotLayer", data=routes, get_position="[from_lon, from_lat]",
                      get_radius=200000, get_fill_color="[0, 255, 65, 200]")
        ]
    ))

    # C. TRIPLE STACKED CHARTS (Back-to-Back)
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02,
                        subplot_titles=("PRICE_ACTION", "RELATIVE_STRENGTH", "VOLUME_FLOW"))
    
    # 1. Price
    fig.add_trace(go.Candlestick(x=hist_1m.index, open=hist_1m['Open'], high=hist_1m['High'],
                                 low=hist_1m['Low'], close=hist_1m['Close'], name="Price"), row=1, col=1)
    # 2. RSI Approximation
    fig.add_trace(go.Scatter(x=hist_1m.index, y=hist_1m['Close'].rolling(14).mean(), name="Trend"), row=2, col=1)
    # 3. Volume
    fig.add_trace(go.Bar(x=hist_1m.index, y=hist_1m['Volume'], name="Vol"), row=3, col=1)

    fig.update_layout(template="plotly_dark", height=600, showlegend=False, 
                      xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=20,b=0))
    st.plotly_chart(fig, use_container_width=True)

with col_data:
    st.markdown("### 🧬 VALUATION_MATRIX")
    # Generating 100+ lines of raw data points
    details = {k: v for k, v in info.items() if isinstance(v, (int, float, str)) and len(str(v)) < 50}
    df_details = pd.DataFrame(list(details.items()), columns=['VARIABLE', 'VALUE'])
    
    # CUSTOM TABLE FOR HIGH DENSITY
    st.dataframe(df_details, height=1000, use_container_width=True)

    # D. REAL NEWS FEED (No BS)
    st.markdown("### 🗞️ WIRE_SERVICE")
    for n in stock.news[:10]:
        st.markdown(f"**[{datetime.fromtimestamp(n['providerPublishTime']).strftime('%H:%M')}]** {n['title']}")
        st.markdown("---")
