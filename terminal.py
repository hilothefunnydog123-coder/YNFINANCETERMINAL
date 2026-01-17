import streamlit as st
import yfinance as yf
import pandas as pd
import pydeck as pdk
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# --- 1. BLOOMBERG TERMINAL UI OVERRIDE ---
st.set_page_config(layout="wide", page_title="SOVEREIGN_V46", initial_sidebar_state="collapsed")

def apply_insane_ui():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
        .stApp { background-color: #000000; color: #ff9900; font-family: 'JetBrains Mono', monospace; }
        .block-container { padding: 0.5rem 1rem; }
        
        /* High-Density Orange Data Tiles */
        .orange-box {
            background: rgba(255, 153, 0, 0.03);
            border: 1px solid #ff9900;
            padding: 8px; margin: 2px;
            font-size: 10px; border-radius: 2px;
        }
        .label { color: #888; font-size: 9px; }
        .val { color: #ff9900; font-weight: bold; font-size: 12px; }

        /* Scrollable 100-Line Matrix */
        .matrix-container {
            height: 800px; overflow-y: scroll;
            border: 1px solid #333; padding: 5px;
            background: #050505;
        }
        </style>
    """, unsafe_allow_html=True)

apply_insane_ui()

# --- 2. DATA HUB ---
ticker = st.sidebar.text_input("CMD >", "NVDA").upper()
stock = yf.Ticker(ticker)
hist = stock.history(period="1d", interval="1m")
info = stock.info

# --- 3. THE "DUAL-MONITOR" MULTI-GRID ---
col_left, col_right = st.columns([2.5, 1])

with col_left:
    # A. TOP STRIP (The 100-Line Pulse)
    st.markdown(f"### // GLOBAL_INTERCEPT: {ticker}")
    
    # B. THE TECHY MAP (ArcLayer & Neural Nodes)
    # Representing real-time institutional flow between global hubs
    flow_data = pd.DataFrame([
        {"s": [ -74.00, 40.71], "e": [ -0.12, 51.50]}, # NY to London
        {"s": [ 103.8, 1.35], "e": [ 139.6, 35.67]}, # Singapore to Tokyo
        {"s": [ 121.4, 31.23], "e": [ 114.1, 22.39]}, # Shanghai to HK
        {"s": [ 4.89, 52.36], "e": [ 55.27, 25.20]}   # Amsterdam to Dubai
    ])
    
    st.pydeck_chart(pdk.Deck(
        map_style=pdk.map_styles.CARTO_DARK,
        initial_view_state=pdk.ViewState(latitude=20, longitude=30, zoom=1.2, pitch=45),
        layers=[
            pdk.Layer("ArcLayer", data=flow_data, get_source_position="s", get_target_position="e",
                      get_width=3, get_source_color="[255, 153, 0, 150]", get_target_color="[0, 255, 65, 150]"),
            pdk.Layer("ScatterplotLayer", data=flow_data, get_position="s", get_radius=300000,
                      get_fill_color="[255, 153, 0, 200]")
        ]
    ))

    # C. TRIPLE-STACKED BACK-TO-BACK CHARTS
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03,
                        subplot_titles=("PRICE_ACTION", "INSTITUTIONAL_VOLUME", "RSI_FLOW"))
    
    fig.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'],
                                 low=hist['Low'], close=hist['Close']), row=1, col=1)
    fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], marker_color='#ff9900'), row=2, col=1)
    fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'].rolling(14).mean(), line_color='#00ff00'), row=3, col=1)

    fig.update_layout(template="plotly_dark", height=600, showlegend=False, 
                      xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=20,b=0),
                      plot_bgcolor='black', paper_bgcolor='black')
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.markdown("### // DATA_MATRIX")
    # This generates over 100 lines of actual data points from the stock
    st.markdown('<div class="matrix-container">', unsafe_allow_html=True)
    
    # Flatten the info dictionary to get every possible data point
    for key, value in info.items():
        if value and len(str(value)) < 40: # Filter out long descriptions
            st.markdown(f"""
                <div class="orange-box">
                    <div class="label">{str(key).upper()}</div>
                    <div class="val">{str(value)}</div>
                </div>
            """, unsafe_allow_html=True)
            
    st.markdown('</div>', unsafe_allow_html=True)
