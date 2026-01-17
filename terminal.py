import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# --- 1. CORE SYSTEM ARCHITECTURE & HUD STYLING ---
st.set_page_config(layout="wide", page_title="SOVEREIGN_TERMINAL_v2", initial_sidebar_state="collapsed")

def apply_floor_spec_ui(price_color="#00ffff"):
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
        
        /* 1. THE CRT/LED SUB-PIXEL GRID */
        /* This creates the physical 'mesh' look over the whole screen */
        .stApp::before {{
            content: " ";
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), 
                        linear-gradient(90deg, rgba(255, 0, 0, 0.03), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.03));
            background-size: 100% 2px, 3px 100%;
            z-index: 9999;
            pointer-events: none;
        }}

        /* 2. GLOBAL HARDWARE RESET */
        .stApp {{ 
            background-color: #000000; 
            color: {price_color}; 
            font-family: 'JetBrains Mono', monospace; 
        }}

        /* Kill all consumer-app rounding; stay sharp and professional */
        * {{ border-radius: 0px !important; }}

        /* 3. DYNAMIC STARK FRAMES */
        .stark-frame {{
            position: relative;
            border: 1px solid {price_color}33 !important;
            background: rgba(0, 0, 0, 1) !important;
            padding: 20px;
            margin: 15px 0;
            box-shadow: inset 0 0 20px {price_color}11;
        }}

        /* NEON GHOSTING EFFECT */
        .stark-header, .val, .ticker-symbol {{
            text-shadow: 0 0 10px {price_color}, 0 0 20px {price_color}44 !important;
            letter-spacing: 2px;
        }}

        /* 4. THE GUTTER DATA (Side Tickers) */
        .gutter {{
            position: fixed; top: 150px; font-size: 8px;
            color: {price_color}44; text-transform: uppercase;
            writing-mode: vertical-rl; letter-spacing: 4px;
            z-index: 1000;
        }}
        .left-gutter {{ left: 5px; }}
        .right-gutter {{ right: 5px; }}

        /* Hide Scrollbars to keep it a fixed Command Center */
        ::-webkit-scrollbar {{ display: none; }}
        </style>
        
        <div class="gutter left-gutter">SIGNAL_STRENGTH_98% // CORE_TEMP_42C // UPLINK_ACTIVE</div>
        <div class="gutter right-gutter">ORDER_FLOW_SYNC // HIGH_FREQ_TRADING_ENABLED</div>
    """, unsafe_allow_html=True)

# CALL THIS IN YOUR MAIN CODE AFTER PULLING THE TICKER INFO
# Change the color based on market movement
current_change = info.get('regularMarketChange', 0)
dynamic_color = "#00ff00" if current_change >= 0 else "#ff0000"
apply_floor_spec_ui(price_color=dynamic_color)

# --- 2. INFINITE LED TICKER (WALL STREET FLOOR) ---
tickers = ["AAPL", "NVDA", "TSLA", "MSFT", "GOOGL", "AMZN", "META", "AMD", "NFLX", "COIN"] * 5
ticker_html = '<div class="ticker-wrap"><div class="ticker-content">'
for t in tickers:
    ticker_html += f'<div class="stock-box"><span style="color:#00ffff;">{t}</span> <span style="color:#00ff00; margin-left:10px;">$184.21 ▲</span></div>'
ticker_html += ticker_html + '</div></div>' # Duplicate for seamless loop
st.markdown(ticker_html, unsafe_allow_html=True)

# --- 3. STICKY COMMAND HUD ---
st.markdown(f"""
    <div class="sticky-hud">
        <h2 style='margin:0; color:#00ffff; letter-spacing: 12px;'>// J.A.R.V.I.S._OS_CORE: {datetime.now().strftime('%H:%M:%S')}</h2>
    </div>
""", unsafe_allow_html=True)

# --- 4. DATA INTERCEPT (Real-Time) ---
ticker_input = st.sidebar.text_input("CMD_INPUT", "NVDA").upper()
stock = yf.Ticker(ticker_input)
hist = stock.history(period="1d", interval="1m")
info = stock.info

# --- 5. HOLOGRAPHIC GLOBAL MAP (The Wireframe) ---
st.markdown('<div class="stark-frame"><span style="color:#00ffff; letter-spacing:5px;">// GLOBAL_NODE_SURVEILLANCE</span>', unsafe_allow_html=True)

routes = [
    dict(type='scattergeo', lat=[40.71, 35.67], lon=[-74.00, 139.65], mode='lines', line=dict(width=2, color='#00ffff')),
    dict(type='scattergeo', lat=[51.50, 1.35], lon=[-0.12, 103.82], mode='lines', line=dict(width=2, color='#00ffff')),
    dict(type='scattergeo', lat=[25.20, 22.39], lon=[55.27, 114.10], mode='lines', line=dict(width=2, color='#00ff66')),
]

map_fig = go.Figure(data=routes)
map_fig.update_geos(
    projection_type="orthographic", showcoastlines=True, coastlinecolor="#004444",
    showland=True, landcolor="#000000", showocean=True, oceancolor="#000000",
    showcountries=True, countrycolor="#002222", bgcolor="black"
)
map_fig.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="black")
st.plotly_chart(map_fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 6. QUANTUM SIGNAL STACK (The Charts) ---
st.markdown('<div class="stark-frame"><span style="color:#00ffff; letter-spacing:5px;">// SIGNAL_FLOW_ANALYSIS</span>', unsafe_allow_html=True)
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.01)
fig.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close']), row=1, col=1)
fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], marker_color='#00ffff'), row=2, col=1)
fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'].rolling(14).mean(), line_color='#00ff66'), row=3, col=1)

fig.update_layout(template="plotly_dark", height=500, showlegend=False, xaxis_rangeslider_visible=False, 
                  margin=dict(l=0,r=0,t=0,b=0), plot_bgcolor='black', paper_bgcolor='black')
st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)
def draw_market_heatmap():
    st.markdown('<div class="stark-frame"><span class="stark-header">// SECTOR_PROXIMITY_HEATMAP</span>', unsafe_allow_html=True)
    # Mock data representing S&P 500 sectors
    data = {
        'Sector': ['Tech', 'Energy', 'Finance', 'Health', 'Retail', 'Defense'],
        'Parent': ['', '', '', '', '', ''],
        'Change': [2.4, -1.2, 0.5, -0.8, 1.1, 3.2]
    }
    fig = go.Figure(go.Treemap(
        labels=data['Sector'],
        parents=data['Parent'],
        values=[30, 15, 20, 15, 10, 10],
        marker=dict(colors=data['Change'], colorscale='RdYlGn', showscale=True),
        textinfo="label+value"
    ))
    fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), paper_bgcolor='black', height=300)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 7. RAW TELEMETRY DUMP (100+ LINES) ---
st.markdown('<div class="stark-frame"><span style="color:#00ffff; letter-spacing:5px;">// RAW_TELEMETRY_DUMP_v.2.0</span>', unsafe_allow_html=True)
st.markdown('<div class="telemetry-grid">', unsafe_allow_html=True)

for key, value in info.items():
    if value and len(str(value)) < 45:
        st.markdown(f"""
            <div class="telemetry-tile">
                <div class="tag">{str(key).upper()}</div>
                <div class="val">{str(value)}</div>
            </div>
        """, unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)
