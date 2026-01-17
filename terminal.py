import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# --- 1. CORE SYSTEM ARCHITECTURE & HUD STYLING ---
st.set_page_config(layout="wide", page_title="SOVEREIGN_TERMINAL_v2", initial_sidebar_state="collapsed")

def apply_stark_terminal_ui():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
        
        /* Global UI Blackout & Neon Cyan */
        .stApp { background-color: #000000; color: #00ffff; font-family: 'JetBrains Mono', monospace; }
        
        /* STICKY HUD HEADER */
        [data-testid="stHeader"] { background: rgba(0,0,0,0.95) !important; border-bottom: 2px solid #00ffff !important; }
        .sticky-hud {
            position: sticky; top: 0; z-index: 9999; 
            background: #000; padding: 15px; border-bottom: 2px solid #00ffff;
            box-shadow: 0 0 30px rgba(0, 255, 255, 0.4);
        }

        /* INFINITE LED TICKER */
        .ticker-wrap {
            width: 100%; overflow: hidden; background: #000;
            border-bottom: 1px solid #333; white-space: nowrap; padding: 10px 0;
        }
        .ticker-content {
            display: inline-block; white-space: nowrap;
            animation: marquee 60s linear infinite;
        }
        @keyframes marquee { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
        
        .stock-box {
            display: inline-block; background: rgba(0, 255, 255, 0.05);
            border: 1px solid #00ffff; margin: 0 10px; padding: 5px 15px;
            box-shadow: 0 0 10px rgba(0, 255, 255, 0.2);
        }

        /* SECTION FRAMES (The Brackets) */
        .stark-frame {
            position: relative; border: 1px solid rgba(0, 255, 255, 0.1);
            background: rgba(0, 255, 255, 0.01); padding: 25px; margin: 20px 0;
            border-radius: 0 20px 0 20px; overflow: hidden;
        }
        .stark-frame::before {
            content: ""; position: absolute; top: 0; left: 0; width: 30px; height: 30px;
            border-top: 4px solid #00ffff; border-left: 4px solid #00ffff;
        }
        .stark-frame::after {
            content: ""; position: absolute; bottom: 0; right: 0; width: 30px; height: 30px;
            border-bottom: 4px solid #00ffff; border-right: 4px solid #00ffff;
        }

        /* TELEMETRY MATRIX GRID */
        .telemetry-grid {
            display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 2px; width: 100%;
        }
        .telemetry-tile {
            background: rgba(0, 255, 255, 0.02); border: 1px solid rgba(0, 255, 255, 0.1);
            padding: 12px; transition: 0.2s;
        }
        .telemetry-tile:hover { background: rgba(0, 255, 255, 0.1); border-color: #00ffff; }
        .tag { color: #333; font-size: 9px; text-transform: uppercase; letter-spacing: 2px; }
        .val { color: #00ffff; font-weight: bold; font-size: 14px; }
        </style>
    """, unsafe_allow_html=True)

apply_stark_terminal_ui()

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
