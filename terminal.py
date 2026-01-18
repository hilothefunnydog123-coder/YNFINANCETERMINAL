import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# --- 1. HUD ARCHITECTURE (STARK THEME) ---
st.set_page_config(layout="wide", page_title="SOVEREIGN_HUD", initial_sidebar_state="collapsed")

def apply_stark_ui(main_color="#00ffff"):
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
        
        /* SUB-PIXEL LED GRID OVERLAY */
        .stApp::before {{
            content: " "; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), 
                        linear-gradient(90deg, rgba(255, 0, 0, 0.03), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.03));
            background-size: 100% 2px, 3px 100%; z-index: 9999; pointer-events: none;
        }}

        .stApp {{ background-color: #000000; color: {main_color}; font-family: 'JetBrains Mono', monospace; }}
        * {{ border-radius: 0px !important; }}

        /* STICKY HUD */
        [data-testid="stHeader"] {{ background: rgba(0,0,0,0.9) !important; border-bottom: 2px solid {main_color} !important; }}
        .sticky-hud {{
            position: sticky; top: 0; z-index: 9999; 
            background: #000; padding: 15px; border-bottom: 2px solid {main_color};
            box-shadow: 0 0 30px {main_color}66;
        }}

        /* LIVE LED TICKER */
        .ticker-wrap {{ width: 100%; overflow: hidden; background: #000; padding: 10px 0; white-space: nowrap; }}
        .ticker-content {{ display: inline-block; animation: marquee 60s linear infinite; }}
        @keyframes marquee {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-50%); }} }}
        .stock-box {{
            display: inline-block; background: {main_color}11; border: 1px solid {main_color};
            margin: 0 10px; padding: 5px 15px; box-shadow: 0 0 10px {main_color}33;
        }}

        /* STARK HUD FRAMES */
        .stark-frame {{
            position: relative; border: 1px solid {main_color}33;
            background: rgba(0,0,0,1); padding: 25px; margin: 20px 0;
        }}
        .stark-frame::before {{
            content: ""; position: absolute; top: 0; left: 0; width: 25px; height: 25px;
            border-top: 4px solid {main_color}; border-left: 4px solid {main_color};
        }}
        .stark-frame::after {{
            content: ""; position: absolute; bottom: 0; right: 0; width: 25px; height: 25px;
            border-bottom: 4px solid {main_color}; border-right: 4px solid {main_color};
        }}

        .val {{ color: {main_color}; font-weight: bold; font-size: 14px; text-shadow: 0 0 10px {main_color}; }}
        .telemetry-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 2px; }}
        .telemetry-tile {{ background: {main_color}05; border: 1px solid {main_color}22; padding: 12px; }}
        
        ::-webkit-scrollbar {{ display: none; }}
        </style>
    """, unsafe_allow_html=True)

# --- 2. DATA COMMAND & LIVE TICKER CACHE ---
ticker_input = st.sidebar.text_input("CMD_INPUT", "NVDA").upper()
stock = yf.Ticker(ticker_input)
info = stock.info # Instant dictionary fetch
hist = stock.history(period="1d", interval="1m")

# Generate Dynamic Color
change = info.get('regularMarketChange', 0)
dynamic_color = "#00ff00" if change >= 0 else "#ff0000"
apply_stark_ui(main_color=dynamic_color)

# --- 3. LIVE MULTI-TICKER DATA ---
# Fetching actual prices for the top 10 tickers to replace static values
top_tickers = ["AAPL", "NVDA", "TSLA", "MSFT", "GOOGL", "AMZN", "META", "AMD", "NFLX", "COIN"]
ticker_data = yf.download(top_tickers, period="1d")['Close'].iloc[-1].to_dict()

ticker_html = '<div class="ticker-wrap"><div class="ticker-content">'
for t, price in ticker_data.items():
    ticker_html += f'<div class="stock-box"><span class="val">{t}</span> <span style="margin-left:10px;">${price:.2f}</span></div>'
ticker_html += ticker_html + '</div></div>' # Loop for infinite scroll
st.markdown(ticker_html, unsafe_allow_html=True)

# --- 4. STICKY HUD ---
st.markdown(f"""
    <div class="sticky-hud">
        <h2 style='margin:0; letter-spacing: 12px;'>// J.A.R.V.I.S._OS_v.4.0: {datetime.now().strftime('%H:%M:%S')}</h2>
    </div>
""", unsafe_allow_html=True)

# --- 5. HOLOGRAPHIC NEURAL GLOBE ---
st.markdown('<div class="stark-frame"><span class="val">// NEURAL_NODE_SURVEILLANCE</span>', unsafe_allow_html=True)

# Create glowing connection arcs
globe_data = [
    dict(type='scattergeo', lat=[40, 35], lon=[-74, 139], mode='lines', line=dict(width=3, color=dynamic_color)),
    dict(type='scattergeo', lat=[51, 1], lon=[-0, 103], mode='lines', line=dict(width=3, color=dynamic_color)),
    dict(type='scattergeo', lat=[40, 51], lon=[-74, -0], mode='lines', line=dict(width=1, color="white", dash="dash"))
]

map_fig = go.Figure(data=globe_data)
map_fig.update_geos(
    projection_type="orthographic",
    showcoastlines=True, coastlinecolor=f"{dynamic_color}", # Wired coastline
    showland=True, landcolor="#050505", # Dark holographic mass
    showocean=True, oceancolor="#000",
    showcountries=True, countrycolor=f"{dynamic_color}44",
    bgcolor="black",
    framecolor=dynamic_color,
    lataxis_showgrid=True, lonaxis_showgrid=True, gridcolor="#111"
)
map_fig.update_layout(height=450, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="black")
st.plotly_chart(map_fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 6. QUANTUM SIGNAL FLOW (The Charts) ---
st.markdown('<div class="stark-frame"><span class="val">// QUANTUM_SIGNAL_STACK</span>', unsafe_allow_html=True)
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.01)
fig.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close']), row=1, col=1)
fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], marker_color=dynamic_color), row=2, col=1)
fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'].rolling(14).mean(), line_color="#fff", opacity=0.5), row=3, col=1)
fig.update_layout(template="plotly_dark", height=500, showlegend=False, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0), plot_bgcolor='black', paper_bgcolor='black')
st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 7. RAW TELEMETRY MATRIX (100+ LINE WALL) ---
st.markdown('<div class="stark-frame"><span class="val">// RAW_TELEMETRY_DUMP_v.4.0</span>', unsafe_allow_html=True)
st.markdown('<div class="telemetry-grid">', unsafe_allow_html=True)
for key, value in info.items():
    if value and len(str(value)) < 45:
        st.markdown(f'<div class="telemetry-tile"><div style="color:#333; font-size:9px;">{str(key).upper()}</div><div class="val">{str(value)}</div></div>', unsafe_allow_html=True)
st.markdown('</div></div>', unsafe_allow_html=True)
