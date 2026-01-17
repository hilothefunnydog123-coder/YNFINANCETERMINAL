import streamlit as st
import yfinance as yf
import pandas as pd
import pydeck as pdk
import plotly.graph_objects as go
from datetime import datetime

# --- 1. BLOOMBERG UI OVERRIDE ---
# We use 'wide' layout and custom CSS to kill the whitespace
st.set_page_config(layout="wide", page_title="YN_TERMINAL_v46", page_icon="📈")

def apply_terminal_theme():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
        
        /* The Bloomberg Signature: Pitch Black Background & Mono Font */
        .stApp { background-color: #000000; color: #efefef; font-family: 'Roboto Mono', monospace; }

        /* Remove Streamlit's huge default padding to maximize data density */
        .block-container { padding-top: 1rem; padding-bottom: 0rem; padding-left: 1rem; padding-right: 1rem; }
        
        /* Metric Cards: Glowing Amber on Black */
        [data-testid="stMetricValue"] { color: #ff9900 !important; font-size: 1.8rem !important; }
        [data-testid="stMetricLabel"] { color: #00ff00 !important; text-transform: uppercase; font-size: 0.8rem !important; }

        /* Compact Table Styling */
        .stTable { font-size: 10px !important; }
        
        /* Custom Header Bar */
        .terminal-header {
            color: #00ff00; background-color: #1a1a1a;
            padding: 5px 15px; border-bottom: 2px solid #333333;
            font-size: 11px; margin-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

apply_terminal_theme()

# --- 2. GLOBAL STATE ---
if 'ticker' not in st.session_state: st.session_state.ticker = "NVDA"

# --- 3. COMMAND LINE INTERFACE (Sidebar) ---
with st.sidebar:
    st.markdown("<h2 style='color:#ff9900;'>BLOOMBERG_v46</h2>", unsafe_allow_html=True)
    st.session_state.ticker = st.text_input("COMMAND > ", value=st.session_state.ticker).upper()
    st.markdown("---")
    st.write(f"SYSTEM_TIME: {datetime.now().strftime('%H:%M:%S')}")
    st.write("SEC_LEVEL: **SOVEREIGN**")

# --- 4. DATA FUSION ENGINE ---
try:
    stock = yf.Ticker(st.session_state.ticker)
    hist = stock.history(period="1d", interval="1m")
    info = stock.info

    # TOP DASHBOARD STRIP
    st.markdown(f"""
        <div class="terminal-header">
            SEC: {st.session_state.ticker} | EXCH: {info.get('exchange')} | CUR: {info.get('currency')} | STATUS: <span style="color:#00ff00;">STREAMING_LIVE</span>
        </div>
    """, unsafe_allow_html=True)

    # --- 5. THE HIGH-DENSITY GRID ---
    # Col 1: Main Monitor (Charts/Maps) | Col 2: Side Monitor (Stats/News)
    col_main, col_side = st.columns([3, 1])

    with col_main:
        # Candlestick HUD
        fig = go.Figure(data=[go.Candlestick(
            x=hist.index, open=hist['Open'], high=hist['High'],
            low=hist['Low'], close=hist['Close'],
            increasing_line_color='#00ff00', decreasing_line_color='#ff0000'
        )])
        fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0, r=0, t=0, b=0),
                          plot_bgcolor='black', paper_bgcolor='black', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

        # Maritime Logistics surveillance (3D Columns)
        st.markdown("<h4 style='color:#ff9900;'>🛰️ AIS_SURVEILLANCE</h4>", unsafe_allow_html=True)
        ships = pd.DataFrame([
            {"lat": 25.12, "lon": 55.23, "load": 100}, {"lat": 1.29, "lon": 103.85, "load": 85},
            {"lat": 35.10, "lon": 129.04, "load": 50}, {"lat": 29.93, "lon": 32.55, "load": 95}
        ])
        st.pydeck_chart(pdk.Deck(
            map_style=pdk.map_styles.CARTO_DARK,
            initial_view_state=pdk.ViewState(latitude=15, longitude=60, zoom=1, pitch=45),
            layers=[pdk.Layer("ColumnLayer", data=ships, get_position="[lon, lat]", 
                              get_elevation="load * 5000", radius=200000, 
                              get_fill_color="[0, 255, 65, 180]", pickable=True)]
        ))

    with col_side:
        # VALUATION MATRIX
        st.markdown("<h4 style='color:#ff9900;'>VALUATION</h4>", unsafe_allow_html=True)
        stats = {
            "Mkt Cap": f"{info.get('marketCap', 0)/1e9:.1f}B",
            "P/E": f"{info.get('trailingPE', 0):.2f}",
            "EPS": f"{info.get('trailingEps', 0):.2f}",
            "52W High": f"{info.get('fiftyTwoWeekHigh', 0):.2f}"
        }
        st.table(pd.Series(stats, name="VALUATION"))

        # LIVE NEWS WIRE (Bulletproof logic)
        st.markdown("<h4 style='color:#ff9900;'>NEWS_WIRE</h4>", unsafe_allow_html=True)
        for n in stock.news[:8]:
            pub_time = n.get('providerPublishTime')
            time_str = datetime.fromtimestamp(pub_time).strftime('%H:%M') if pub_time else "--:--"
            st.markdown(f"<span style='color:#00ff00;'>[{time_str}]</span> {n.get('title')}", unsafe_allow_html=True)
            st.markdown("<hr style='margin: 5px 0; border-color: #333;'>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"SYSTEM_FAILURE: {str(e)}")
