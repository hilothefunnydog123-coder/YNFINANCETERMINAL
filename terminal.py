import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# --- 1. CORE CONFIGURATION ---
st.set_page_config(layout="wide", page_title="SOVEREIGN_PRIME", initial_sidebar_state="collapsed")

# --- 2. THE STARK UI ENGINE ---
def apply_stark_ui(main_color="#00ffff"):
    # We inject CSS *after* we know the color (Green/Red) based on the stock price
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
        
        /* 1. PHYSICAL HARDWARE MESH OVERLAY */
        /* This creates the "Screen Door" effect of a high-end LED wall */
        .stApp::before {{
            content: " "; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), 
                        linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
            background-size: 100% 2px, 3px 100%; z-index: 9999; pointer-events: none;
        }}

        /* 2. GLOBAL RESET */
        .stApp {{ background-color: #000000; color: {main_color}; font-family: 'JetBrains Mono', monospace; }}
        * {{ border-radius: 0px !important; }} /* Sharp Professional Corners */

        /* 3. STICKY COMMAND HUD */
        [data-testid="stHeader"] {{ background: rgba(0,0,0,0.95) !important; border-bottom: 2px solid {main_color} !important; }}
        .sticky-hud {{
            position: sticky; top: 0; z-index: 9999; 
            background: #000; padding: 10px; border-bottom: 2px solid {main_color};
            display: flex; justify-content: space-between; align-items: center;
            box-shadow: 0 5px 30px {main_color}44;
        }}

        /* 4. INFINITE TICKER TAPE */
        .ticker-wrap {{ width: 100%; overflow: hidden; background: #000; border-bottom: 1px solid {main_color}44; padding: 5px 0; white-space: nowrap; }}
        .ticker-content {{ display: inline-block; animation: marquee 40s linear infinite; }}
        @keyframes marquee {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-50%); }} }}
        
        .stock-box {{
            display: inline-block; padding: 4px 15px; margin: 0 5px;
            border: 1px solid {main_color}44; background: {main_color}11;
            font-size: 14px; font-weight: bold;
        }}

        /* 5. STARK CONTAINERS (The Brackets) */
        .stark-frame {{
            position: relative; margin: 20px 0; padding: 20px;
            border: 1px solid {main_color}33; background: rgba(0,0,0,0.5);
        }}
        /* Glowing Corner Brackets */
        .stark-frame::before {{ content: ""; position: absolute; top: 0; left: 0; width: 15px; height: 15px; border-top: 3px solid {main_color}; border-left: 3px solid {main_color}; }}
        .stark-frame::after {{ content: ""; position: absolute; bottom: 0; right: 0; width: 15px; height: 15px; border-bottom: 3px solid {main_color}; border-right: 3px solid {main_color}; }}

        /* 6. DATA MATRIX GRID */
        .telemetry-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 4px; }}
        .telemetry-tile {{ background: {main_color}08; border: 1px solid {main_color}22; padding: 10px; }}
        .telemetry-tile:hover {{ background: {main_color}22; border-color: {main_color}; cursor: crosshair; }}
        
        .tag {{ font-size: 9px; color: #666; letter-spacing: 1px; }}
        .val {{ font-size: 14px; font-weight: bold; color: {main_color}; text-shadow: 0 0 10px {main_color}; }}

        /* 7. GUTTER DATA (Vertical Text) */
        .gutter {{ position: fixed; top: 200px; font-size: 9px; color: {main_color}44; writing-mode: vertical-rl; letter-spacing: 3px; z-index: 0; }}
        .left-gutter {{ left: 8px; }} .right-gutter {{ right: 8px; }}
        
        ::-webkit-scrollbar {{ display: none; }}
        </style>
        
        <div class="gutter left-gutter">SECURE_UPLINK_ESTABLISHED // NODE_734</div>
        <div class="gutter right-gutter">QUANTUM_SYNC_ACTIVE // LATENCY_12MS</div>
    """, unsafe_allow_html=True)

# --- 3. DATA ACQUISITION LAYER ---
# We fetch data FIRST so we can color the UI based on the result

# A. Main Ticker Input
ticker_input = st.sidebar.text_input("CMD_INPUT", "NVDA").upper()
stock = yf.Ticker(ticker_input)

# B. Fetch Core Data
try:
    info = stock.info
    hist = stock.history(period="1d", interval="1m")
    
    # Calculate Theme Color (Green for Up, Red for Down)
    current_price = info.get('currentPrice', 0)
    prev_close = info.get('previousClose', 0)
    if current_price >= prev_close:
        theme_color = "#00ff00" # Neon Green
    else:
        theme_color = "#ff0000" # Warning Red
        
except Exception as e:
    st.error(f"DATA_LINK_FAILURE: {e}")
    st.stop()

# --- 4. APPLY STYLES ---
apply_stark_ui(main_color=theme_color)

# --- 5. LIVE TICKER TAPE (REAL DATA) ---
# We download a batch of tickers to get real prices for the scrolling tape
tape_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "AMD", "INTC", "QCOM", "IBM"]
try:
    tape_data = yf.download(tape_tickers, period="1d", progress=False)['Close'].iloc[-1]
    ticker_html = '<div class="ticker-wrap"><div class="ticker-content">'
    # Repeat the list to ensure the marquee feels infinite
    for _ in range(3): 
        for t in tape_tickers:
            price = tape_data.get(t, 0)
            ticker_html += f'<div class="stock-box">{t} <span style="opacity:0.8;">${price:.2f}</span></div>'
    ticker_html += '</div></div>'
    st.markdown(ticker_html, unsafe_allow_html=True)
except:
    st.markdown('<div class="ticker-wrap"><div class="ticker-content">OFFLINE // RECONNECTING...</div></div>', unsafe_allow_html=True)

# --- 6. STICKY HUD HEADER ---
st.markdown(f"""
    <div class="sticky-hud">
        <div style="font-size: 20px; font-weight: bold; letter-spacing: 5px;">SOVEREIGN_TERMINAL</div>
        <div style="font-family: monospace; font-size: 14px;">{datetime.now().strftime('%H:%M:%S')} UTC</div>
    </div>
""", unsafe_allow_html=True)

# --- 7. HOLOGRAPHIC NEURAL MAP (FIXED) ---

st.markdown(f'<div class="stark-frame"><div class="tag">// GLOBAL_MARKET_FLOW</div>', unsafe_allow_html=True)

# Generate connection arcs
connections = [
    dict(type='scattergeo', lat=[40.7, 51.5], lon=[-74.0, -0.1], mode='lines', line=dict(width=2, color=theme_color)), # NY-Lon
    dict(type='scattergeo', lat=[35.6, 1.3], lon=[139.6, 103.8], mode='lines', line=dict(width=2, color=theme_color)), # Tok-Sin
    dict(type='scattergeo', lat=[40.7, 35.6], lon=[-74.0, 139.6], mode='lines', line=dict(width=1, color=theme_color, dash="dot")), # NY-Tok
]

map_fig = go.Figure(data=connections)

# Safe Geoplot config (Removed invalid arguments)
map_fig.update_geos(
    projection_type="orthographic",
    showcoastlines=True, coastlinecolor=theme_color,
    showland=True, landcolor="#050505", # Almost black land
    showocean=True, oceancolor="#000000",
    showcountries=True, countrycolor="#333333",
    bgcolor="black",
    lataxis=dict(showgrid=True, gridcolor="#1a1a1a"),
    lonaxis=dict(showgrid=True, gridcolor="#1a1a1a")
)
map_fig.update_layout(height=450, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="black")
st.plotly_chart(map_fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 8. SIGNAL ANALYSIS STACK (Triple Chart) ---
st.markdown(f'<div class="stark-frame"><div class="tag">// TECHNICAL_INTERCEPT: {ticker_input}</div>', unsafe_allow_html=True)
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.5, 0.25, 0.25])

# Candle
fig.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'], name="Price"), row=1, col=1)
# Volume
fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], marker_color=theme_color, name="Vol"), row=2, col=1)
# MA
fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'].rolling(20).mean(), line=dict(color='white', width=1), name="MA20"), row=3, col=1)

fig.update_layout(
    template="plotly_dark", height=600, showlegend=False, 
    xaxis_rangeslider_visible=False, 
    margin=dict(l=0,r=0,t=10,b=0), 
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)'
)
# Hide Gridlines for cleaner look
fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=True, gridcolor='#222')

st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 9. 100-LINE TELEMETRY MATRIX ---
st.markdown(f'<div class="stark-frame"><div class="tag">// FUNDAMENTAL_MATRIX_DUMP</div>', unsafe_allow_html=True)
st.markdown('<div class="telemetry-grid">', unsafe_allow_html=True)

# Loop safely through info to create the "Wall of Numbers"
for key, value in info.items():
    # Clean up the key name for display
    clean_key = str(key).replace("regularMarket", "").replace("fiftyTwoWeek", "52W").upper()
    
    # Only show short values to keep the grid tight
    if value and len(str(value)) < 20:
        st.markdown(f"""
            <div class="telemetry-tile">
                <div class="tag">{clean_key}</div>
                <div class="val">{str(value)}</div>
            </div>
        """, unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)
