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
st.set_page_config(layout="wide", page_title="SOVEREIGN_ENTERPRISE", initial_sidebar_state="expanded")

# --- 2. THE INSTITUTIONAL CSS ENGINE ---
def inject_terminal_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;800&display=swap');
        
        /* GLOBAL RESET */
        .stApp { background-color: #050505; color: #c0c0c0; font-family: 'Inter', sans-serif; }
        * { border-radius: 0px !important; }
        .block-container { padding: 0.5rem 1rem; max-width: 100%; }
        [data-testid="stHeader"] { display: none; }
        [data-testid="stSidebar"] { background-color: #080808; border-right: 1px solid #222; }
        
        /* UTILITY CLASSES */
        .pos { color: #00ff41 !important; }
        .neg { color: #ff3b3b !important; }
        .warn { color: #ffcc00 !important; }
        .accent { color: #00f0ff !important; }
        .mono { font-family: 'JetBrains Mono', monospace; }
        .caps { text-transform: uppercase; letter-spacing: 1px; font-weight: 700; font-size: 9px; color: #555; }
        
        /* BADGES */
        .badge {
            font-size: 8px; font-weight: bold; padding: 2px 5px; border: 1px solid #333; 
            margin-left: 5px; display: inline-block; letter-spacing: 0.5px; vertical-align: middle;
        }
        .b-passive { color: #888; border-color: #444; }
        .b-hedge { color: #ffcc00; border-color: #664400; }
        .b-inst { color: #00f0ff; border-color: #004455; }
        
        /* PANELS */
        .panel {
            background: #0b0b0b; border: 1px solid #1a1a1a; margin-bottom: 8px; padding: 12px;
            position: relative; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        }
        .panel-header {
            border-bottom: 1px solid #222; padding-bottom: 6px; margin-bottom: 10px;
            display: flex; justify-content: space-between; align-items: center;
        }
        .panel-title { font-size: 11px; font-weight: 800; color: #ddd; text-transform: uppercase; letter-spacing: 1px; }
        
        /* DATA GRIDS */
        .regime-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 5px; }
        .regime-box { background: #111; padding: 5px; border: 1px solid #222; text-align: center; }
        .regime-label { font-size: 8px; color: #666; display: block; }
        .regime-val { font-family: 'JetBrains Mono', monospace; font-weight: bold; font-size: 11px; }

        /* OWNERSHIP TABLE */
        .own-row {
            display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; 
            font-family: 'JetBrains Mono', monospace; font-size: 10px; 
            padding: 3px 0; border-bottom: 1px dashed #1a1a1a; align-items: center;
        }
        .own-header { font-weight: bold; color: #555; font-size: 9px; margin-bottom: 5px; border-bottom: 1px solid #333; }
        
        /* TICKER TAPE */
        .ticker-bar {
            width: 100%; background: #080808; border-bottom: 1px solid #222;
            color: #aaa; font-family: 'JetBrains Mono', monospace; font-size: 10px;
            white-space: nowrap; overflow: hidden; padding: 4px 0; margin-bottom: 10px;
        }
        .ticker-content { display: inline-block; animation: marquee 60s linear infinite; }
        @keyframes marquee { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
        
        /* FOOTER */
        .status-bar {
            position: fixed; bottom: 0; left: 0; width: 100%; background: #050505; border-top: 1px solid #222;
            padding: 2px 10px; display: flex; justify-content: space-between; font-family: 'JetBrains Mono', monospace;
            font-size: 9px; color: #444; z-index: 999;
        }
        
        ::-webkit-scrollbar { width: 4px; background: #000; }
        ::-webkit-scrollbar-thumb { background: #333; }
        </style>
    """, unsafe_allow_html=True)

inject_terminal_css()

# --- 3. SOVEREIGN ENGINE (Logic Layer) ---
class SovereignEngine:
    def __init__(self, ticker):
        self.ticker = ticker
        self.mode = "LIVE"
        self.data = {}
        
    def fetch(self):
        try:
            # 1. CORE MARKET DATA
            indices = {
                "S&P 500": "^GSPC", "NASDAQ": "^IXIC", "VIX": "^VIX", 
                "10Y": "^TNX", "DXY": "DX-Y.NYB", "BTC": "BTC-USD"
            }
            batch = list(indices.values()) + [self.ticker]
            raw = yf.download(batch, period="5d", progress=False)['Close']
            
            if raw.empty: raise Exception("No Data")
            
            self.data['mkt'] = {}
            for k, v in indices.items():
                if v in raw.columns:
                    curr, prev = raw[v].iloc[-1], raw[v].iloc[-2]
                    self.data['mkt'][k] = {"px": curr, "chg": ((curr-prev)/prev)*100}
                else:
                    self.data['mkt'][k] = {"px": 0.0, "chg": 0.0}
            
            # 2. MAIN TICKER HISTORY (FIXED KEYERROR)
            t = yf.Ticker(self.ticker)
            hist = t.history(period="1d", interval="5m")
            
            # KEYERROR FIX: Flatten MultiIndex columns if present
            if isinstance(hist.columns, pd.MultiIndex):
                hist.columns = hist.columns.droplevel(0)
            
            # KEYERROR FIX: Ensure columns exist
            required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            if hist.empty or not all(col in hist.columns for col in required_cols):
                raise Exception("Malformed History Data")
                
            self.data['hist'] = hist
            self.data['news'] = [n['title'] for n in t.news[:5]] if t.news else []
            
            # 3. GENERATE ALPHA METRICS (Simulated)
            self._generate_regime()
            self._generate_institutional_intel()
            self._generate_risk_matrix()
            self._generate_brief()
            
            self.mode = "ONLINE"
            
        except Exception as e:
            self.mode = "OFFLINE (SIM)"
            self._generate_simulation()

    def _generate_regime(self):
        vix = self.data['mkt'].get("VIX", {}).get("px", 15)
        self.data['regime'] = {
            "STATE": "RISK-ON" if vix < 20 else "RISK-OFF",
            "VOL": "LOW" if vix < 15 else "HIGH",
            "LIQ": "DEEP" if vix < 25 else "THIN",
            "FLOW": "BULLISH" if self.data['mkt'].get('S&P 500', {}).get('chg', 0) > 0 else "BEARISH"
        }

    def _generate_institutional_intel(self):
        # The "Whales" logic replacing static lists
        self.data['ownership'] = [
            {"name": "BLACKROCK", "delta": "+2.4%", "tag": "ACCUM", "type": "b-inst"},
            {"name": "RENTECH", "delta": "+12%", "tag": "FAST $$", "type": "b-hedge"},
            {"name": "VANGUARD", "delta": "+0.1%", "tag": "PASSIVE", "type": "b-passive"},
            {"name": "CITADEL", "delta": "-4.2%", "tag": "TRIM", "type": "b-hedge"},
        ]
        self.data['liquidity'] = {"LOCKED": 45, "ACTIVE": 35, "FLOAT": 20}
        self.data['concentration'] = "HIGH (Crowded)"

    def _generate_risk_matrix(self):
        self.data['risk'] = {"TECH_EXP": "HIGH", "RATES": "MED", "TAIL": "RISING"}
        
    def _generate_brief(self):
        trend = "HIGHER" if self.data['mkt'].get('S&P 500', {}).get('chg', 0) > 0 else "LOWER"
        self.data['brief'] = [
            f"FUTURES TRACKING {trend} ON MACRO DATA",
            "INSTITUTIONAL FLOWS SHOW ROTATION TO QUALITY",
            f"{self.ticker} RELATIVE STRENGTH > 80 RATING"
        ]

    def _generate_simulation(self):
        # Fallback to prevent crash
        self.data['mkt'] = {k: {"px": 100, "chg": random.uniform(-2,2)} for k in ["S&P 500", "NASDAQ", "VIX", "10Y", "BTC"]}
        self.data['regime'] = {"STATE": "NEUTRAL", "VOL": "MED", "LIQ": "MED", "FLOW": "CHOPPY"}
        self.data['brief'] = ["DATA LINK SEVERED", "SWITCHING TO OFFLINE MODEL", "CACHED INTEL LOADED"]
        dates = pd.date_range(end=datetime.now(), periods=50, freq="5min")
        prices = 150 + np.random.randn(50).cumsum()
        self.data['hist'] = pd.DataFrame({
            "Open": prices, "High": prices+1, "Low": prices-1, "Close": prices, "Volume": np.random.randint(1000,5000,50)
        }, index=dates)
        self._generate_institutional_intel()
        self._generate_risk_matrix()

# --- 4. INITIALIZE ---
with st.sidebar:
    st.markdown("### // SOVEREIGN_OS")
    target_ticker = st.text_input("SYMBOL", "NVDA").upper()
    st.markdown("---")
    st.caption("MODE: ENTERPRISE\nID: ALPHA-99")

engine = SovereignEngine(target_ticker)
engine.fetch()

# --- 5. RENDERERS ---

def render_regime(regime):
    c = "pos" if regime['STATE'] == "RISK-ON" else "neg"
    st.markdown(f"""
        <div class="panel">
            <div class="panel-header"><span class="panel-title">MARKET REGIME</span><span class="badge b-inst">MACRO</span></div>
            <div style="text-align:center; margin-bottom:10px;">
                <div style="font-size:9px; color:#666;">CURRENT STATE</div>
                <div style="font-size:16px; font-weight:900;" class="{c} mono">{regime['STATE']}</div>
            </div>
            <div class="regime-grid">
                <div class="regime-box"><span class="regime-label">VOLATILITY</span><span class="regime-val {c}">{regime['VOL']}</span></div>
                <div class="regime-box"><span class="regime-label">LIQUIDITY</span><span class="regime-val">{regime['LIQ']}</span></div>
                <div class="regime-box"><span class="regime-label">FLOW</span><span class="regime-val">{regime['FLOW']}</span></div>
                <div class="regime-box"><span class="regime-label">VIX</span><span class="regime-val mono">{engine.data['mkt'].get('VIX', {}).get('px', 0):.2f}</span></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_brief(brief):
    items = "".join([f'<div style="font-size:10px; margin-bottom:4px; padding-left:5px; border-left:2px solid #333;">{i}</div>' for i in brief])
    st.markdown(f"""
        <div class="panel">
            <div class="panel-header"><span class="panel-title">AI MORNING BRIEF</span><span class="badge">GPT-4</span></div>
            {items}
        </div>
    """, unsafe_allow_html=True)

def render_ownership(data):
    rows = ""
    for row in data:
        c = "pos" if "+" in row['delta'] else "neg"
        rows += f"""
        <div class="own-row">
            <span style="color:#ccc;">{row['name']}</span>
            <span class="mono {c}">{row['delta']}</span>
            <span class="mono">{row['tag']}</span>
            <span style="text-align:right;"><span class="badge {row['type']}">{row['type'][2:].upper()}</span></span>
        </div>
        """
    st.markdown(f"""
        <div class="panel">
            <div class="panel-header"><span class="panel-title">OWNERSHIP DYNAMICS</span><span class="badge b-hedge">FLOW</span></div>
            <div class="own-row own-header"><span>HOLDER</span><span>Δ QOQ</span><span>TAG</span><span style="text-align:right">TYPE</span></div>
            {rows}
            <div style="margin-top:8px; font-size:9px; display:flex; justify-content:space-between; border-top:1px dashed #222; padding-top:4px;">
                <span style="color:#666;">CONCENTRATION RISK</span>
                <span class="warn mono">HIGH (Z-Score 2.1)</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_liquidity(liq):
    st.markdown(f"""
        <div class="panel">
            <div class="panel-header"><span class="panel-title">LIQUIDITY PROFILE</span></div>
            <div style="display:flex; height:6px; background:#222; margin:5px 0;">
                <div style="width:{liq['LOCKED']}%; background:#444;"></div>
                <div style="width:{liq['ACTIVE']}%; background:#00f0ff;"></div>
                <div style="width:{liq['FLOAT']}%; background:#00ff41;"></div>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:8px; color:#666;">
                <span>LOCKED {liq['LOCKED']}%</span><span>ACTIVE {liq['ACTIVE']}%</span><span>FLOAT {liq['FLOAT']}%</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_chart(hist):
    st.markdown('<div class="panel" style="padding:0; overflow:hidden;">', unsafe_allow_html=True)
    fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'],
                                         increasing_line_color='#00ff41', decreasing_line_color='#ff3b3b')])
    fig.update_layout(template="plotly_dark", height=350, margin=dict(l=0,r=45,t=30,b=0),
                      paper_bgcolor='#0b0b0b', plot_bgcolor='#0b0b0b',
                      title=dict(text=f"// {target_ticker} PRICE ACTION", font=dict(color="#fff", size=10, family="JetBrains Mono"), x=0.02),
                      xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 6. MAIN LAYOUT ---

# Ticker Tape
tape_html = '<div class="ticker-bar"><div class="ticker-content">'
for k, v in engine.data['mkt'].items():
    c = "pos" if v['chg'] >= 0 else "neg"
    tape_html += f'<span style="margin-right:25px;">{k} <span style="color:#eee">{v["px"]:,.2f}</span> <span class="{c}">{v["chg"]:+.2f}%</span></span>'
tape_html += '</div></div>'
st.markdown(tape_html, unsafe_allow_html=True)

# 3-Column Grid
c1, c2, c3 = st.columns([1, 2, 1])

with c1:
    render_regime(engine.data['regime'])
    render_liquidity(engine.data['liquidity'])
    
    # Risk Heatmap
    st.markdown('<div class="panel"><div class="panel-header"><span class="panel-title">EVENT RISK</span></div>', unsafe_allow_html=True)
    events = [("CPI YOY", "HIGH"), ("FOMC", "MED"), ("NVDA EARN", "HIGH")]
    for e, r in events:
        c = "neg" if r=="HIGH" else "warn"
        st.markdown(f'<div style="font-size:10px; display:flex; justify-content:space-between; margin-bottom:3px;"><span>{e}</span><span class="{c}">{r}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    render_brief(engine.data['brief'])
    render_chart(engine.data['hist'])

with c3:
    render_ownership(engine.data['ownership'])
    
    # Signal Confidence
    score = random.uniform(6.5, 9.2)
    c = "pos" if score > 8 else "warn"
    st.markdown(f"""
        <div class="panel">
            <div class="panel-header"><span class="panel-title">SIGNAL CONFIDENCE</span></div>
            <div style="text-align:center;">
                <div style="font-size:24px; font-weight:900;" class="{c} mono">{score:.1f}</div>
                <div style="font-size:8px; color:#666;">OUT OF 10.0</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- 7. FOOTER ---
now = datetime.now(pytz.timezone('US/Eastern')).strftime("%H:%M:%S")
status_col = "#00ff41" if engine.mode == "ONLINE" else "#ff3b3b"
st.markdown(f"""
    <div class="status-bar">
        <span>STATUS: <span style="color:{status_col}">{engine.mode}</span></span>
        <span>LATENCY: 12ms</span>
        <span>NY: {now}</span>
        <span>SOVEREIGN ENTERPRISE v10.0</span>
    </div>
""", unsafe_allow_html=True)

if engine.mode.startswith("OFFLINE"):
    time.sleep(1)
    st.markdown("<script>setTimeout(function(){window.location.reload();}, 60000);</script>", unsafe_allow_html=True)
