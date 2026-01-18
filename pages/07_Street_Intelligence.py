import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz
import random
import time

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(layout="wide", page_title="SOVEREIGN_STREET_INTEL", initial_sidebar_state="collapsed")

# --- 2. THE INSTITUTIONAL CSS ENGINE ---
def inject_terminal_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&family=Inter:wght@400;600;800&display=swap');
        
        /* GLOBAL RESET */
        .stApp { background-color: #050505; color: #e0e0e0; font-family: 'Inter', sans-serif; }
        * { border-radius: 0px !important; }
        
        /* LAYOUT TWEAKS */
        .block-container { padding-top: 0rem; padding-bottom: 2rem; padding-left: 0.5rem; padding-right: 0.5rem; }
        [data-testid="stHeader"] { display: none; }
        
        /* UTILITY CLASSES */
        .pos { color: #00ff41 !important; text-shadow: 0 0 5px rgba(0,255,65,0.2); }
        .neg { color: #ff3b3b !important; text-shadow: 0 0 5px rgba(255,59,59,0.2); }
        .neu { color: #888 !important; }
        .warn { color: #ffcc00 !important; }
        .accent { color: #00f0ff !important; }
        .mono { font-family: 'Roboto Mono', monospace; }
        .caps { text-transform: uppercase; letter-spacing: 1px; font-weight: 700; font-size: 9px; color: #555; }
        
        /* BADGES */
        .badge {
            font-size: 8px; font-weight: bold; padding: 2px 4px; border: 1px solid #333; 
            margin-left: 5px; display: inline-block; letter-spacing: 0.5px;
        }
        .b-passive { color: #888; border-color: #444; }
        .b-hedge { color: #ffcc00; border-color: #664400; }
        .b-anchor { color: #00f0ff; border-color: #004455; }
        
        /* PANEL CONTAINERS */
        .panel {
            background: #0a0a0a; border: 1px solid #222; margin-bottom: 8px; padding: 10px;
            position: relative; height: 100%; min-height: 150px;
        }
        .panel-header {
            border-bottom: 1px solid #333; padding-bottom: 5px; margin-bottom: 8px;
            display: flex; justify-content: space-between; align-items: center;
        }
        .panel-title { font-size: 11px; font-weight: 800; color: #fff; text-transform: uppercase; letter-spacing: 0.5px; }
        
        /* OWNERSHIP TABLE */
        .own-row {
            display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; 
            font-family: 'Roboto Mono', monospace; font-size: 11px; 
            padding: 4px 0; border-bottom: 1px dashed #1a1a1a; align-items: center;
        }
        .own-row:last-child { border-bottom: none; }
        .own-header { font-weight: bold; color: #666; font-size: 9px; margin-bottom: 5px; }
        
        /* LIQUIDITY BAR */
        .liq-bar-container { width: 100%; height: 6px; background: #222; margin: 5px 0; display: flex; }
        .liq-locked { height: 100%; background: #444; }
        .liq-active { height: 100%; background: #00f0ff; }
        .liq-float { height: 100%; background: #00ff41; }
        
        /* NEWS & FOOTER */
        .news-item { font-size: 11px; border-left: 2px solid #333; padding-left: 8px; margin-bottom: 6px; color: #ddd; }
        .status-bar {
            position: fixed; bottom: 0; left: 0; width: 100%; background: #080808; border-top: 1px solid #333;
            padding: 3px 10px; display: flex; justify-content: space-between; font-family: 'Roboto Mono', monospace;
            font-size: 9px; color: #555; z-index: 999;
        }
        
        /* SCROLLBARS */
        ::-webkit-scrollbar { width: 4px; background: #000; }
        ::-webkit-scrollbar-thumb { background: #333; }
        </style>
    """, unsafe_allow_html=True)

inject_terminal_css()

# --- 3. STREET INTELLIGENCE ENGINE (The Brain) ---
class StreetIntelEngine:
    def __init__(self, main_ticker):
        self.ticker = main_ticker
        self.mode = "LIVE"
        self.data = {}
        
    def fetch(self):
        try:
            # 1. CORE MARKET DATA
            indices = {
                "S&P 500": "^GSPC", "NASDAQ": "^IXIC", "VIX": "^VIX", 
                "10Y YIELD": "^TNX", "DXY": "DX-Y.NYB", "BTC": "BTC-USD"
            }
            batch = list(indices.values()) + [self.ticker]
            raw = yf.download(batch, period="2d", progress=False)['Close']
            
            if raw.empty: raise Exception("No Data")
            
            self.data['mkt'] = {}
            for k, v in indices.items():
                if v in raw.columns:
                    curr, prev = raw[v].iloc[-1], raw[v].iloc[-2]
                    self.data['mkt'][k] = {"px": curr, "chg": ((curr-prev)/prev)*100}
            
            # 2. MAIN TICKER
            t = yf.Ticker(self.ticker)
            self.data['hist'] = t.history(period="1d", interval="5m")
            self.data['news'] = [n['title'] for n in t.news[:5]] if t.news else []
            
            # 3. GENERATE INSTITUTIONAL INTEL (Simulated for "Pro" feel)
            self._generate_ownership_dynamics()
            self._generate_liquidity_profile()
            self._generate_regime()
            
            self.mode = "ONLINE"
            
        except Exception:
            self.mode = "OFFLINE"
            self._generate_simulation()

    def _generate_ownership_dynamics(self):
        # This replaces the static "Whales" list with dynamic behavior
        # In a real app, this would come from 13F filings
        self.data['ownership'] = [
            {"name": "VANGUARD GROUP", "shares": "9.1%", "delta": "+0.0%", "action": "PASSIVE", "type": "b-passive"},
            {"name": "BLACKROCK INC", "shares": "7.9%", "delta": "+1.2%", "action": "ACCUM", "type": "b-anchor"},
            {"name": "RENTECH FUND", "shares": "2.1%", "delta": "+12%", "action": "AGGR BUY", "type": "b-hedge"},
            {"name": "STATE STREET", "shares": "4.1%", "delta": "-0.1%", "action": "HOLD", "type": "b-passive"},
            {"name": "CITADEL ADVISORS", "shares": "0.8%", "delta": "-5.4%", "action": "TRIM", "type": "b-hedge"},
        ]
        self.data['concentration'] = {
            "TOP_10_CONTROL": "38.6%",
            "CROWDING_SCORE": "HIGH (Z-Score 2.1)",
            "CONVICTION": "TACTICAL"
        }

    def _generate_liquidity_profile(self):
        # Simulates how much stock is "locked" vs "tradable"
        self.data['liquidity'] = {
            "LOCKED": 45, # % Passive/Insiders
            "ACTIVE": 35, # % Institutional Active
            "FLOAT": 20   # % Retail/High Freq
        }

    def _generate_regime(self):
        vix = self.data['mkt'].get("VIX", {}).get("px", 15)
        self.data['regime'] = "RISK-ON" if vix < 20 else "RISK-OFF"

    def _generate_simulation(self):
        # Fallback Data
        self.data['mkt'] = {k: {"px": 100, "chg": random.uniform(-2,2)} for k in ["S&P 500", "NASDAQ", "VIX", "10Y YIELD", "DXY", "BTC"]}
        self.data['news'] = ["API LIMIT REACHED - SIMULATING FEED", "INSTITUTIONAL REBALANCING DETECTED", "DARK POOL VOLUME ELEVATED"]
        dates = pd.date_range(end=datetime.now(), periods=50, freq="5min")
        self.data['hist'] = pd.DataFrame({"Close": 150 + np.random.randn(50).cumsum()}, index=dates)
        self._generate_ownership_dynamics()
        self._generate_liquidity_profile()
        self.data['regime'] = "NEUTRAL"

# --- 4. INITIALIZE ---
target_ticker = st.sidebar.text_input("SYMBOL", "NVDA").upper()
engine = StreetIntelEngine(target_ticker)
engine.fetch()

# --- 5. RENDER FUNCTIONS ---

def render_ownership_panel(data, concentration):
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header"><span class="panel-title">OWNERSHIP DYNAMICS</span><span class="caps">13F FLOW</span></div>', unsafe_allow_html=True)
    
    # Header Row
    st.markdown('<div class="own-row own-header"><span>HOLDER</span><span>POS %</span><span>Δ QOQ</span><span>BEHAVIOR</span></div>', unsafe_allow_html=True)
    
    for holder in data:
        # Color logic for Delta
        d_val = float(holder['delta'].strip('%'))
        d_col = "pos" if d_val > 0 else "neg" if d_val < 0 else "neu"
        
        st.markdown(f"""
            <div class="own-row">
                <span style="color:#ccc;">{holder['name']}</span>
                <span class="mono">{holder['shares']}</span>
                <span class="mono {d_col}">{holder['delta']}</span>
                <span><span class="badge {holder['type']}">{holder['action']}</span></span>
            </div>
        """, unsafe_allow_html=True)
        
    # Concentration Footer
    st.markdown(f"""
        <div style="margin-top:10px; border-top:1px dashed #333; padding-top:5px; font-size:10px; display:flex; justify-content:space-between;">
            <span style="color:#666;">CONCENTRATION RISK:</span>
            <span class="warn mono">{concentration['CROWDING_SCORE']}</span>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_liquidity_panel(liq):
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header"><span class="panel-title">LIQUIDITY PROFILE</span><span class="caps">FLOAT STRUCTURE</span></div>', unsafe_allow_html=True)
    
    # Visual Bar
    st.markdown(f"""
        <div class="liq-bar-container">
            <div class="liq-locked" style="width:{liq['LOCKED']}%;"></div>
            <div class="liq-active" style="width:{liq['ACTIVE']}%;"></div>
            <div class="liq-float" style="width:{liq['FLOAT']}%;"></div>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:9px; color:#666; margin-top:2px;">
            <span>LOCKED (PASSIVE) {liq['LOCKED']}%</span>
            <span>ACTIVE INST {liq['ACTIVE']}%</span>
            <span>TRADABLE {liq['FLOAT']}%</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style="margin-top:8px; font-size:10px; border-top:1px dashed #222; padding-top:4px;">
            <div style="display:flex; justify-content:space-between;">
                <span>TURNOVER VELOCITY</span><span class="accent mono">HIGH</span>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <span>FLOAT TIGHTNESS</span><span class="warn mono">RESTRICTED</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_chart(hist):
    st.markdown('<div class="panel" style="padding:0;">', unsafe_allow_html=True)
    fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'],
                                         increasing_line_color='#00ff41', decreasing_line_color='#ff3b3b')])
    fig.update_layout(template="plotly_dark", height=300, margin=dict(l=0,r=40,t=30,b=0),
                      paper_bgcolor='#0a0a0a', plot_bgcolor='#0a0a0a',
                      title=dict(text=f"// {target_ticker} PRICE ACTION", font=dict(color="#fff", size=10, family="Roboto Mono"), x=0.02),
                      xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_globals(mkt):
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header"><span class="panel-title">GLOBAL CROSS-ASSET</span></div>', unsafe_allow_html=True)
    for k, v in mkt.items():
        c = "pos" if v['chg'] >= 0 else "neg"
        st.markdown(f'<div class="own-row"><span style="color:#aaa">{k}</span><span></span><span></span><span class="{c} mono">{v["chg"]:+.2f}%</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 6. MAIN LAYOUT ---

# Ticker Tape
tape_html = '<div class="ticker-bar"><div class="ticker-content">'
for k, v in engine.data['mkt'].items():
    c = "pos" if v['chg'] >= 0 else "neg"
    tape_html += f'<span style="margin-right:25px;">{k} <span style="color:#eee">{v["px"]:,.2f}</span> <span class="{c}">{v["chg"]:+.2f}%</span></span>'
tape_html += '</div></div>'
st.markdown(tape_html, unsafe_allow_html=True)

# Grid: [ Markets (Small) ] [ Chart (Med) ] [ Ownership (Large) ]
c1, c2, c3 = st.columns([1, 2, 2])

with c1:
    render_globals(engine.data['mkt'])
    render_liquidity_panel(engine.data['liquidity'])

with c2:
    render_chart(engine.data['hist'])
    # News
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header"><span class="panel-title">NEWS WIRE</span></div>', unsafe_allow_html=True)
    for n in engine.data['news']:
        st.markdown(f'<div class="news-item">{n}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c3:
    render_ownership_panel(engine.data['ownership'], engine.data['concentration'])

# --- 7. FOOTER ---
now = datetime.now(pytz.timezone('US/Eastern')).strftime("%H:%M:%S")
st.markdown(f"""
    <div class="status-bar">
        <span>STATUS: <span style="color:{'#00ff41' if engine.mode=='ONLINE' else '#ff3b3b'}">{engine.mode}</span></span>
        <span>NY: {now}</span>
        <span>SOVEREIGN STREET INTELLIGENCE v4.2</span>
    </div>
""", unsafe_allow_html=True)

if engine.mode == "OFFLINE":
    time.sleep(1)
    st.markdown("<script>setTimeout(function(){window.location.reload();}, 60000);</script>", unsafe_allow_html=True)
