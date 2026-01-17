import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# --- 1. HUD CORE ARCHITECTURE ---
st.set_page_config(layout="wide", page_title="SOVEREIGN_TERMINAL", initial_sidebar_state="collapsed")

def apply_stark_floor_ui(main_color="#00ffff"):
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
        
        /* THE CRT/LED SUB-PIXEL GRID */
        .stApp::before {{
            content: " ";
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), 
                        linear-gradient(90deg, rgba(255, 0, 0, 0.03), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.03));
            background-size: 100% 2px, 3px 100%;
            z-index: 9999; pointer-events: none;
        }}

        .stApp {{ background-color: #000000; color: {main_color}; font-family: 'JetBrains Mono', monospace; }}
        * {{ border-radius: 0px !important; }} /* Professional sharp corners */

        /* STICKY HUD */
        [data-testid="stHeader"] {{ background: rgba(0,0,0,0.9) !important; border-bottom: 2px solid {main_color} !important; }}
        .sticky-hud {{
            position: sticky; top: 0; z-index: 9999; 
            background: #000; padding: 15px; border-bottom: 2px solid {main_color};
            box-shadow: 0 0 30px {main_color}66;
        }}

        /* INFINITE LED TICKER */
        .ticker-wrap {{ width: 100%; overflow: hidden; background: #000; padding: 10px 0; white-space: nowrap; }}
        .ticker-content {{ display: inline-block; animation: marquee 60s linear infinite; }}
        @keyframes marquee {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-50%); }} }}
        .stock-box {{
            display: inline-block; background: {main_color}11; border: 1px solid {main_color};
            margin: 0 10px; padding: 5px 15px; box-shadow: 0 0 10px {main_color}33;
        }}

        /* STARK FRAMES */
        .stark-frame {{
            position: relative; border: 1px solid {main_color}33;
            background: rgba(0,0,0,1); padding: 25px; margin: 20px 0;
        }}
        .stark-frame::before {{
            content: ""; position: absolute; top: 0; left: 0; width: 20px; height: 20px;
            border-top: 3px solid {main_color}; border-left: 3px solid {main_color};
        }}
        .stark-frame::after {{
            content: ""; position: absolute; bottom: 0; right: 0; width: 20px; height: 20px;
            border-bottom: 3px solid {main_color}; border-right: 3px solid {main_color};
        }}

        /* TELEMETRY MATRIX */
        .telemetry-grid {{
            display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 2px; width: 100%;
        }}
        .telemetry-tile {{
            background: {main_color}05; border: 1px solid {main_color}22;
            padding: 12px; transition: 0.2s;
        }}
        .telemetry-tile:hover {{ background: {main_color}15; border-color: {main_color}; }}
        .tag {{ color: #444; font-size: 9px; text-transform: uppercase; letter-spacing: 2px; }}
        .val {{ color: {main_color}; font-weight: bold; font-size: 14px; text-shadow: 0 0 10px {main_color}; }}

        /* GUTTER DATA */
        .gutter {{ position: fixed; top: 200px; font-size: 8px; color: {main_color}44; writing-mode: vertical-rl; letter-spacing: 4px; }}
        .left-gutter {{ left: 5px; }} .right-gutter {{ right: 5px; }}
        ::-webkit-scrollbar {{ display: none; }}
        </style>
        <div class="gutter left-gutter">SIGNAL_STRENGTH_99% // UPLINK_ENCRYPTED</div>
        <div class="gutter right-gutter">ORDER_FLOW_SYNC // HIGH_FREQ_TRADING_v.2</div>
    """, unsafe_allow_html=True)

# --- 2. DATA COMMAND & INTERCEPT ---
ticker_input = st.sidebar.text_input("CMD_INPUT", "NVDA").upper()
stock = yf.Ticker(ticker_input)
info = stock.info  # Variable defined here
hist = stock.history(period="1d", interval="1m")

# --- 3. DYNAMIC STYLE EXECUTION ---
change = info.get('regularMarketChange', 0)
dynamic_color = "#00ff00" if change >= 0 else "#ff0000"
apply_stark_floor_ui(main_color=dynamic_color)

# --- 4. INFINITE LED TICKER ---
tickers_list = ["AAPL", "NVDA", "TSLA", "MSFT", "GOOGL", "AMZN", "META", "AMD", "NFLX", "COIN"] * 6
ticker_html = '<div class="ticker-wrap"><div class="ticker-content">'
for t in tickers_list:
    ticker_html += f'<div class="stock-box"><span class="val">{t}</span> <span style="margin-left:10px;">$184.21 ▲</span></div>'
ticker_html += ticker_html + '</div></div>'
st.markdown(ticker_html, unsafe_allow_html=True)

# --- 5. STICKY HUD ---
st.markdown(f"""
    <div class="sticky-hud">
        <h2 style='margin:0; letter-spacing: 12px;'>// J.A.R.V.I.S._OS_CORE: {datetime.now().strftime('%H:%M:%S')}</h2>
    </div>
""", unsafe_allow_html=True)

# --- 6. HOLOGRAPHIC GLOBE ---
# [Image of high-tech world map with glowing nodes and data connection lines]
st.markdown('<div class="stark-frame"><span class="val">// GLOBAL_NODE_SURVEILLANCE</span>', unsafe_allow_html=True)
map_fig = go.Figure(data=[dict(type='scattergeo', lat=[40, 35, 25], lon=[-74, 139, 55], mode='lines', line=dict(width=2, color=dynamic_color))])
map_fig.update_geos(projection_type="orthographic", showcoastlines=True, coastlinecolor=f"{dynamic_color}44", showland=True, landcolor="#000", bgcolor="black")
map_fig.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="black")
st.plotly_chart(map_fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 7. SIGNAL STACK ---
st.markdown('<div class="stark-frame"><span class="val">// QUANTUM_SIGNAL_FLOW</span>', unsafe_allow_html=True)
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.01)
fig.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close']), row=1, col=1)
fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], marker_color=dynamic_color), row=2, col=1)
fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'].rolling(14).mean(), line_color="#ffffff"), row=3, col=1)
fig.update_layout(template="plotly_dark", height=500, showlegend=False, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0), plot_bgcolor='black', paper_bgcolor='black')
st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 8. TELEMETRY MATRIX ---
st.markdown('<div class="stark-frame"><span class="val">// RAW_TELEMETRY_DUMP_v.2.0</span>', unsafe_allow_html=True)
st.markdown('<div class="telemetry-grid">', unsafe_allow_html=True)
for key, value in info.items():
    if value and len(str(value)) < 45:
        st.markdown(f'<div class="telemetry-tile"><div class="tag">{str(key).upper()}</div><div class="val">{str(value)}</div></div>', unsafe_allow_html=True)
st.markdown('</div></div>', unsafe_allow_html=True)
