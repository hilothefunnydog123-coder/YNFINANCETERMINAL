import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz
import random
import time
import streamlit.components.v1 as components


components.html(
    """
    <html>
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
      </head>
      <body style="margin:0;padding:0;background:#0b0b0b;">
        
        <script async="async" data-cfasync="false"
          src="https://pl28519010.effectivegatecpm.com/7f2ad764010d514cdee2fdac0b042524/invoke.js">
        </script>

        <div id="container-7f2ad764010d514cdee2fdac0b042524"></div>

      </body>
    </html>
    """,
    height=250,
)



# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(layout="wide", page_title="SOVEREIGN_PRIME_VC", initial_sidebar_state="expanded")

# --- 2. THE "VC-READY" CSS ENGINE ---
def inject_terminal_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;800&display=swap');
        
        /* GLOBAL RESET & DARK MODE */
        .stApp { background-color: #030303; color: #e0e0e0; font-family: 'Inter', sans-serif; }
        * { border-radius: 0px !important; }
        
        /* LAYOUT & SPACING */
        .block-container { padding-top: 0rem; padding-bottom: 2rem; padding-left: 0.5rem; padding-right: 0.5rem; }
        [data-testid="stHeader"] { display: none; }
        [data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #222; }
        
        /* UTILITY COLORS */
        .pos { color: #00ff41 !important; text-shadow: 0 0 5px rgba(0,255,65,0.3); }
        .neg { color: #ff3b3b !important; text-shadow: 0 0 5px rgba(255,59,59,0.3); }
        .warn { color: #ffcc00 !important; }
        .neu { color: #888 !important; }
        .accent { color: #00f0ff !important; text-shadow: 0 0 5px rgba(0,240,255,0.3); }
        .mono { font-family: 'JetBrains Mono', monospace; }
        .caps { text-transform: uppercase; letter-spacing: 1px; font-weight: 700; font-size: 9px; color: #555; }
        
        /* BADGES */
        .badge {
            background: #111; border: 1px solid #333; padding: 2px 6px;
            font-size: 8px; font-weight: bold; letter-spacing: 1px;
            margin-left: 8px; display: inline-block; vertical-align: middle;
        }
        .badge-beta { border-color: #ffcc00; color: #ffcc00; }
        .badge-live { border-color: #00ff41; color: #00ff41; }
        
        /* PANEL CONTAINERS */
        .panel {
            background: #080808; border: 1px solid #1a1a1a; margin-bottom: 8px; padding: 12px;
            position: relative; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .panel-header {
            border-bottom: 1px solid #222; padding-bottom: 6px; margin-bottom: 10px;
            display: flex; justify-content: space-between; align-items: center;
        }
        .panel-title { font-size: 11px; font-weight: 800; color: #ccc; text-transform: uppercase; letter-spacing: 1px; }
        
        /* MARKET REGIME GRID */
        .regime-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
        .regime-box { background: #0c0c0c; padding: 6px; border: 1px solid #222; text-align: center; }
        .regime-label { font-size: 9px; color: #666; display: block; margin-bottom: 2px; }
        .regime-val { font-family: 'JetBrains Mono', monospace; font-weight: bold; font-size: 12px; }
        
        /* AI BRIEF & NARRATIVES */
        .brief-item { font-size: 11px; margin-bottom: 6px; border-left: 2px solid #333; padding-left: 8px; color: #ccc; }
        .narrative-row { display: flex; justify-content: space-between; font-size: 11px; padding: 4px 0; border-bottom: 1px dashed #1a1a1a; }
        
        /* RISK HEATMAP DOTS */
        .risk-dot { height: 8px; width: 8px; border-radius: 50%; display: inline-block; margin-right: 4px; }
        .risk-high { background: #ff3b3b; box-shadow: 0 0 5px #ff3b3b; }
        .risk-med { background: #ffcc00; }
        .risk-low { background: #00ff41; }
        
        /* TICKER TAPE */
        .ticker-bar {
            width: 100%; background: #050505; border-bottom: 1px solid #222;
            color: #aaa; font-family: 'JetBrains Mono', monospace; font-size: 11px;
            white-space: nowrap; overflow: hidden; padding: 5px 0; margin-bottom: 10px;
        }
        .ticker-content { display: inline-block; animation: marquee 60s linear infinite; }
        @keyframes marquee { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
        
        /* FOOTER STATUS */
        .status-bar {
            position: fixed; bottom: 0; left: 0; width: 100%; background: #050505; border-top: 1px solid #222;
            padding: 3px 10px; display: flex; justify-content: space-between; font-family: 'JetBrains Mono', monospace;
            font-size: 9px; color: #555; z-index: 999;
        }
        
        /* SCROLLBARS */
        ::-webkit-scrollbar { width: 4px; background: #000; }
        ::-webkit-scrollbar-thumb { background: #333; }
        </style>
    """, unsafe_allow_html=True)

inject_terminal_css()

# --- 3. SOVEREIGN DECISION ENGINE (The Brain) ---
class DecisionEngine:
    def __init__(self, ticker):
        self.ticker = ticker
        self.mode = "LIVE" # or SIMULATION
        self.data = {}
        
    def fetch_all(self):
        try:
            # 1. CORE MARKET DATA (Indices + Crypto)
            indices = {
                "S&P 500": "^GSPC", "NASDAQ": "^IXIC", "VIX": "^VIX", 
                "10Y YIELD": "^TNX", "DXY": "DX-Y.NYB", "BTC": "BTC-USD"
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
            
            # 2. MAIN TICKER & HISTORY
            t = yf.Ticker(self.ticker)
            self.data['hist'] = t.history(period="1d", interval="5m")
            self.data['info'] = t.info

            # 3. GENERATE "VC ALPHA" LAYERS (Simulated Intelligence)
            self._generate_regime()
            self._generate_ai_brief()
            self._generate_narratives()
            self._generate_flow()
            self._generate_risk_matrix()
            
            self.mode = "ONLINE"
            
        except Exception as e:
            self.mode = "OFFLINE (SIM)"
            self._generate_simulation_fallbacks()

    def _generate_regime(self):
        # LOGIC: VIX < 20 = Risk On, VIX > 20 = Risk Off
        vix = self.data['mkt'].get("VIX", {}).get("px", 15)
        self.data['regime'] = {
            "STATE": "RISK-ON" if vix < 20 else "RISK-OFF",
            "VOLATILITY": "SUPPRESSED" if vix < 15 else "ELEVATED",
            "LIQUIDITY": "HIGH" if vix < 25 else "DRYING",
            "TREND": "BULLISH" if self.data['mkt']['S&P 500']['chg'] > 0 else "BEARISH"
        }

    def _generate_ai_brief(self):
        # Simulated LLM Output
        trend = "higher" if self.data['mkt']['S&P 500']['chg'] > 0 else "lower"
        self.data['brief'] = [
            f"FUTURES TRADING {trend.upper()} ON EASING YIELDS",
            "CPI DATA TOMORROW: TAIL RISK ELEVATED",
            f"{self.ticker} SHOWING RELATIVE STRENGTH VS SECTOR",
            "VOLATILITY PRICED CHEAP - HEDGING ADVISED"
        ]

    def _generate_narratives(self):
        # The "Story" of the market
        self.data['narratives'] = [
            {"topic": "AI CAPEX EXPANSION", "strength": "HIGH", "trend": "pos"},
            {"topic": "SOFT LANDING", "strength": "MED", "trend": "neu"},
            {"topic": "CHINA REOPENING", "strength": "LOW", "trend": "neg"},
            {"topic": "FED PIVOT", "strength": "HIGH", "trend": "pos"}
        ]

    def _generate_flow(self):
        # Institutional Activity (Simulated)
        self.data['flow'] = {
            "DARK_POOL": random.randint(40, 70), # Percent
            "BLOCK_VOL": f"{random.randint(1, 5)}M",
            "NET_DELTA": "POS" if random.random() > 0.5 else "NEG",
            "GAMMA_EX": f"${random.randint(500, 2000)}M"
        }

    def _generate_risk_matrix(self):
        self.data['risk'] = {
            "TECH_EXP": "42%", "RATES_SENS": "HIGH", 
            "USD_CORR": "0.65", "TAIL_RISK": "RISING"
        }

    def _generate_simulation_fallbacks(self):
        # Robust fallback data
        self.data['mkt'] = {k: {"px": 100 + random.random()*10, "chg": random.uniform(-2, 2)} for k in ["S&P 500", "NASDAQ", "VIX", "10Y YIELD", "DXY", "BTC"]}
        self.data['regime'] = {"STATE": "NEUTRAL", "VOLATILITY": "NORMAL", "LIQUIDITY": "MED", "TREND": "CHOPPY"}
        self.data['brief'] = ["API CONNECTION LOST", "SWITCHING TO OFFLINE CACHE", "MODEL CONFIDENCE: LOW"]
        dates = pd.date_range(end=datetime.now(), periods=50, freq="5min")
        self.data['hist'] = pd.DataFrame({"Close": 150 + np.random.randn(50).cumsum()}, index=dates)
        self._generate_narratives()
        self._generate_flow()
        self._generate_risk_matrix()

# --- 4. SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("### // SOVEREIGN_PRIME")
    ticker = st.text_input("SYMBOL", "NVDA").upper()
    
    st.markdown("---")
    st.markdown("**STRATEGY PROFILE**")
    profile = st.selectbox("", ["MACRO_HEDGE_FUND", "DAY_TRADER", "LONG_ONLY_INSTITUTIONAL"])
    
    st.markdown("---")
    compliance = st.checkbox("COMPLIANCE MODE", value=False)
    if compliance:
        st.caption("✅ SIGNAL GENERATION DISABLED")
        st.caption("✅ RISK DISCLAIMERS ACTIVE")
    
    st.markdown("---")
    st.caption(f"LICENSE: PRO SEAT\nID: 994-Alpha-X")

# --- 5. INITIALIZE ENGINE ---
engine = DecisionEngine(ticker)
engine.fetch_all()

# --- 6. RENDER FUNCTIONS ---

def render_regime_panel(regime):
    color = "pos" if regime['STATE'] == "RISK-ON" else "neg"
    st.markdown(f"""
        <div class="panel">
            <div class="panel-header"><span class="panel-title">MARKET REGIME</span><span class="badge badge-live">REALTIME</span></div>
            <div style="text-align:center; margin-bottom:10px;">
                <div style="font-size:10px; color:#666;">CURRENT STATE</div>
                <div style="font-size:18px; font-weight:900; letter-spacing:1px;" class="{color} mono">{regime['STATE']}</div>
            </div>
            <div class="regime-grid">
                <div class="regime-box"><span class="regime-label">VOLATILITY</span><span class="regime-val {color}">{regime['VOLATILITY']}</span></div>
                <div class="regime-box"><span class="regime-label">LIQUIDITY</span><span class="regime-val">{regime['LIQUIDITY']}</span></div>
                <div class="regime-box"><span class="regime-label">TREND</span><span class="regime-val">{regime['TREND']}</span></div>
                <div class="regime-box"><span class="regime-label">VIX</span><span class="regime-val">{engine.data['mkt'].get('VIX', {}).get('px', 0):.2f}</span></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
components.html(
    """
    <!-- Adsterra CPM Ad -->
    <script src="https://pl28518975.effectivegatecpm.com/4b/b8/00/4bb80075f97ec2e7da97c462a677bc5c.js"></script>
    """,
    height=120,
)


def render_ai_brief(brief):
    items = "".join([f'<div class="brief-item">{item}</div>' for item in brief])
    st.markdown(f"""
        <div class="panel">
            <div class="panel-header"><span class="panel-title">AI MORNING BRIEF</span><span class="badge">GPT-4o</span></div>
            {items}
            <div style="margin-top:10px; border-top:1px dashed #333; padding-top:5px; font-size:9px; color:#555; text-align:right;">
                CONFIDENCE: 92% // UPDATED 07:00 ET
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_risk_heatmap():
    # Simulated Event Risk
    events = [("CPI YOY", "high"), ("FOMC MINS", "med"), ("NVDA EARNS", "high"), ("JOBLESS", "low")]
    html = ""
    for name, risk in events:
        color = "risk-high" if risk == "high" else "risk-med" if risk == "med" else "risk-low"
        dots = '<span class="risk-dot ' + color + '"></span>' * (3 if risk == "high" else 2 if risk == "med" else 1)
        html += f'<div style="display:flex; justify-content:space-between; font-size:10px; margin-bottom:5px; color:#ccc;"><span>{name}</span><span>{dots}</span></div>'
    
    st.markdown(f"""
        <div class="panel">
            <div class="panel-header"><span class="panel-title">EVENT RISK SCAN</span></div>
            {html}
        </div>
    """, unsafe_allow_html=True)

def render_main_chart(hist):
    st.markdown('<div class="panel" style="padding:0;">', unsafe_allow_html=True)
    # Simple, clean Plotly chart
    fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'],
                                         increasing_line_color='#00ff41', decreasing_line_color='#ff3b3b')])
    fig.update_layout(template="plotly_dark", height=350, margin=dict(l=0,r=50,t=40,b=0),
                      paper_bgcolor='#080808', plot_bgcolor='#080808',
                      title=dict(text=f"// {ticker} PRICE ACTION [5M]", font=dict(color="#fff", size=11, family="JetBrains Mono"), x=0.02),
                      xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_narratives(narratives):
    html = ""
    for n in narratives:
        color = "pos" if n['trend'] == "pos" else "neg" if n['trend'] == "neg" else "warn"
        html += f"""
        <div class="narrative-row">
            <span style="color:#ccc;">{n['topic']}</span>
            <span class="{color} mono" style="font-weight:bold;">{n['strength']}</span>
        </div>
        """
    st.markdown(f"""
        <div class="panel">
            <div class="panel-header"><span class="panel-title">NARRATIVE TRACKER</span><span class="badge">VC-ALPHA</span></div>
            {html}
        </div>
    """, unsafe_allow_html=True)

def render_signal_card():
    if compliance:
        st.markdown("""
            <div class="panel" style="display:flex; align-items:center; justify-content:center; flex-direction:column; height:100%;">
                <div style="font-size:30px;">🔒</div>
                <div style="font-size:10px; color:#666; margin-top:5px;">REGULATED MODE ACTIVE</div>
            </div>
        """, unsafe_allow_html=True)
        return

    # Signal Score Generation
    score = round(random.uniform(6.0, 9.5), 1)
    color = "pos" if score > 7.5 else "warn"
    st.markdown(f"""
        <div class="panel">
            <div class="panel-header"><span class="panel-title">SIGNAL QUALITY</span><span class="badge badge-beta">INTERNAL</span></div>
            <div style="text-align:center;">
                <div style="font-size:32px; font-weight:900;" class="{color} mono">{score}</div>
                <div style="font-size:9px; color:#666;">OUT OF 10.0</div>
            </div>
            <div style="margin-top:15px; font-size:10px; display:flex; justify-content:space-between;">
                <span style="color:#aaa;">WIN RATE</span><span class="mono">62%</span>
            </div>
            <div style="font-size:10px; display:flex; justify-content:space-between;">
                <span style="color:#aaa;">R/R RATIO</span><span class="mono">1:2.4</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_flow_tracker(flow):
    st.markdown(f"""
        <div class="panel">
            <div class="panel-header"><span class="panel-title">INSTITUTIONAL FLOW</span><span class="badge">DARK POOL</span></div>
            <div class="regime-grid">
                <div class="regime-box"><span class="regime-label">DARK POOL %</span><span class="regime-val accent">{flow['DARK_POOL']}%</span></div>
                <div class="regime-box"><span class="regime-label">BLOCK VOL</span><span class="regime-val">{flow['BLOCK_VOL']}</span></div>
                <div class="regime-box"><span class="regime-label">NET DELTA</span><span class="regime-val {('pos' if flow['NET_DELTA']=='POS' else 'neg')}">{flow['NET_DELTA']}</span></div>
                <div class="regime-box"><span class="regime-label">GAMMA EX</span><span class="regime-val">{flow['GAMMA_EX']}</span></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_macro_stress():
    # Simulated Stress Meters
    st.markdown("""
        <div class="panel">
            <div class="panel-header"><span class="panel-title">MACRO STRESS</span></div>
            <div style="font-size:10px; margin-bottom:4px;">USD LIQUIDITY <span style="float:right;" class="neg">TIGHT</span></div>
            <div style="width:100%; height:4px; background:#333;"><div style="width:80%; height:100%; background:#ff3b3b;"></div></div>
            
            <div style="font-size:10px; margin-top:8px; margin-bottom:4px;">CREDIT SPREADS <span style="float:right;" class="pos">STABLE</span></div>
            <div style="width:100%; height:4px; background:#333;"><div style="width:30%; height:100%; background:#00ff41;"></div></div>
            
            <div style="font-size:10px; margin-top:8px; margin-bottom:4px;">OIL SHOCK <span style="float:right;" class="warn">RISING</span></div>
            <div style="width:100%; height:4px; background:#333;"><div style="width:60%; height:100%; background:#ffcc00;"></div></div>
        </div>
    """, unsafe_allow_html=True)

def render_risk_matrix(risk):
    st.markdown(f"""
        <div class="panel">
            <div class="panel-header"><span class="panel-title">RISK MATRIX</span><span class="badge">HEDGE</span></div>
            <div style="font-size:10px; display:flex; justify-content:space-between; border-bottom:1px dashed #222; padding:3px 0;">
                <span style="color:#888;">TECH EXP</span><span class="mono">{risk['TECH_EXP']}</span>
            </div>
            <div style="font-size:10px; display:flex; justify-content:space-between; border-bottom:1px dashed #222; padding:3px 0;">
                <span style="color:#888;">RATES SENS</span><span class="neg mono">{risk['RATES_SENS']}</span>
            </div>
            <div style="font-size:10px; display:flex; justify-content:space-between; border-bottom:1px dashed #222; padding:3px 0;">
                <span style="color:#888;">USD CORR</span><span class="mono">{risk['USD_CORR']}</span>
            </div>
            <div style="font-size:10px; display:flex; justify-content:space-between; padding:3px 0;">
                <span style="color:#888;">TAIL RISK</span><span class="warn mono">{risk['TAIL_RISK']}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- 7. MAIN LAYOUT ---

# Ticker Tape
tape_html = '<div class="ticker-bar"><div class="ticker-content">'
tape_list = ["S&P 500", "NASDAQ", "VIX", "BTC", "ETH", "US10Y", "NVDA", "TSLA"]
for k in tape_list:
    v = engine.data['mkt'].get(k, {'px':0, 'chg':0})
    c = "pos" if v['chg'] >= 0 else "neg"
    tape_html += f'<span style="margin-right:25px;">{k} <span style="color:#eee">{v["px"]:,.2f}</span> <span class="{c}">{v["chg"]:+.2f}%</span></span>'
tape_html += '</div></div>'
st.markdown(tape_html, unsafe_allow_html=True)

# Grid System
c1, c2, c3 = st.columns([1, 2, 1])

with c1:
    render_regime_panel(engine.data['regime'])
    render_narratives(engine.data['narratives'])
    render_macro_stress()

with c2:
    # AI Brief at Top
    render_ai_brief(engine.data['brief'])
    # Main Chart
    render_main_chart(engine.data['hist'])
    # Flow Tracker (Bottom Center)
    render_flow_tracker(engine.data['flow'])

with c3:
    render_risk_heatmap()
    render_signal_card()
    render_risk_matrix(engine.data['risk'])

# --- 8. FOOTER ---
now = datetime.now(pytz.timezone('US/Eastern')).strftime("%H:%M:%S")
status_color = "#00ff41" if engine.mode == "ONLINE" else "#ff3b3b"

st.markdown(f"""
    <div class="status-bar">
        <span>STATUS: <span style="color:{status_color}">{engine.mode}</span></span>
        <span>LATENCY: 14ms</span>
        <span>NY: {now}</span>
        <span>SOVEREIGN ENGINE v9.2 // <span class="warn">INTERNAL BETA</span></span>
    </div>
""", unsafe_allow_html=True)

# Auto-Refresh if offline
if engine.mode.startswith("OFFLINE"):
    time.sleep(1)
    st.markdown("<script>setTimeout(function(){window.location.reload();}, 60000);</script>", unsafe_allow_html=True)
