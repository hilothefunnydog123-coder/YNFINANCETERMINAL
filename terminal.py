import streamlit as st
import yfinance as yf
import pandas as pd
import pydeck as pdk
import plotly.graph_objects as go
from datetime import datetime

# --- 1. BLOOMBERG TERMINAL CORE THEME ---
st.set_page_config(layout="wide", page_title="TERMINAL_v46", page_icon="📈")

def apply_majestic_theme():
    st.markdown("""
        <style>
        /* Bloomberg-Standard Font and Colors */
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
        
        .stApp { background-color: #000000; color: #efefef; font-family: 'Roboto Mono', monospace; }

        /* Force High Density Grid */
        .block-container { padding: 1rem 1rem; max-width: 100%; }
        [data-testid="column"] { padding: 0.5rem; }

        /* Neon & Amber Metric Cards */
        [data-testid="stMetricValue"] { color: #ff9900 !important; font-size: 1.6rem !important; }
        [data-testid="stMetricLabel"] { color: #00ff00 !important; letter-spacing: 2px; }

        /* Sidebar Glassmorphism */
        section[data-testid="stSidebar"] {
            background-color: #0a0a0a !important;
            border-right: 1px solid #333333;
        }

        /* Ticker Tape Effect at Top */
        .ticker-bar {
            background: #111; color: #00ff00; padding: 5px;
            border-bottom: 2px solid #333; font-size: 12px;
            white-space: nowrap; overflow: hidden; margin-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

apply_majestic_theme()

# --- 2. GLOBAL STATE ---
if 'ticker' not in st.session_state: st.session_state.ticker = "NVDA"

# --- 3. COMMAND INTERFACE (Sidebar) ---
with st.sidebar:
    st.markdown("<h2 style='color:#ff9900;'>BLOOMBERG_v46</h2>", unsafe_allow_html=True)
    st.session_state.ticker = st.text_input("COMMAND_INPUT > ", value=st.session_state.ticker).upper()
    st.markdown("---")
    st.write(f"USER: **YN_ANALYST**")
    st.write(f"TIME: {datetime.now().strftime('%H:%M:%S')}")
    st.write("SEC_LEVEL: **SOVEREIGN**")

# --- 4. REAL-TIME DATA ENGINE (Direct Scraping) ---
try:
    stock = yf.Ticker(st.session_state.ticker)
    # Fetch 1m data for the 'Live' feel
    hist = stock.history(period="1d", interval="1m")
    info = stock.info
    
    # Top Ticker Bar
    st.markdown(f"""
        <div class="ticker-bar">
            {st.session_state.ticker} | PX: {hist['Close'].iloc[-1]:.2f} | 
            EXCH: {info.get('exchange', 'N/A')} | 
            MKT_CAP: {info.get('marketCap', 0)/1e9:.1f}B | 
            STATUS: <span style="color:#00ff00;">STREAMING_LIVE</span>
        </div>
    """, unsafe_allow_html=True)

    # --- 5. THE DUAL-MONITOR GRID LAYOUT ---
    row1_left, row1_right = st.columns([2.5, 1])

    with row1_left:
        # High Density Charts
        fig = go.Figure(data=[go.Candlestick(
            x=hist.index, open=hist['Open'], high=hist['High'],
            low=hist['Low'], close=hist['Close'],
            increasing_line_color='#00ff00', decreasing_line_color='#ff0000'
        )])
        fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0, r=0, t=0, b=0),
                          plot_bgcolor='black', paper_bgcolor='black', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Live Maritime Layer (3D Columns)
        st.markdown("<h4 style='color:#ff9900;'>🛰️ AIS_SURVEILLANCE_INTERCEPT</h4>", unsafe_allow_html=True)
        ships = pd.DataFrame([
            {"lat": 25.12, "lon": 55.23, "load": 100}, {"lat": 1.29, "lon": 103.85, "load": 80},
            {"lat": 35.10, "lon": 129.04, "load": 40}, {"lat": 29.93, "lon": 32.55, "load": 95}
        ])
        st.pydeck_chart(pdk.Deck(
            map_style=pdk.map_styles.CARTO_DARK,
            initial_view_state=pdk.ViewState(latitude=15, longitude=60, zoom=1, pitch=45),
            layers=[pdk.Layer("ColumnLayer", data=ships, get_position="[lon, lat]", 
                              get_elevation="load * 5000", radius=250000, 
                              get_fill_color="[0, 255, 65, 180]", pickable=True)]
        ))

    with row1_right:
        # Valuation Matrix
        st.markdown("<h4 style='color:#ff9900;'>VALUATION_STATS</h4>", unsafe_allow_html=True)
        metrics_df = pd.DataFrame({
            "Label": ["PE_RATIO", "EPS_TRAIL", "DIV_YIELD", "52W_HIGH"],
            "Value": [f"{info.get('trailingPE', 0):.2f}", f"{info.get('trailingEps', 0):.2f}", 
                      f"{info.get('dividendYield', 0)*100:.2f}%", f"{info.get('fiftyTwoWeekHigh', 0):.2f}"]
        })
        st.table(metrics_df.set_index("Label"))

        # News Feed (Bulletproof Version)
        st.markdown("<h4 style='color:#ff9900;'>NEWS_WIRE</h4>", unsafe_allow_html=True)
        for n in stock.news[:6]:
            pub_time = n.get('providerPublishTime')
            time_str = datetime.fromtimestamp(pub_time).strftime('%H:%M') if pub_time else "--:--"
            st.markdown(f"<span style='color:#00ff00;'>[{time_str}]</span> {n.get('title')}", unsafe_allow_html=True)
            st.markdown("---")

except Exception as e:
    st.error(f"SYSTEM_FAILURE: {str(e)}")
