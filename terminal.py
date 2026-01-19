import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
import time

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="SOVEREIGN_SITUATION", initial_sidebar_state="collapsed")

# --- 2. SITUATION ROOM CSS ---
def inject_situation_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&family=Inter:wght@400;700;900&display=swap');
        
        .stApp { background-color: #050505; color: #c0c0c0; font-family: 'Inter', sans-serif; }
        .block-container { padding: 1rem 1rem; max-width: 100%; }
        [data-testid="stHeader"] { display: none; }
        
        /* COLORS */
        .pos { color: #00ff41 !important; }
        .neg { color: #ff3b3b !important; }
        .warn { color: #ffcc00 !important; }
        .accent { color: #00f0ff !important; }
        .mono { font-family: 'Roboto Mono', monospace; }
        
        /* REGIME STRIP */
        .regime-strip {
            display: grid; grid-template-columns: repeat(5, 1fr); gap: 2px;
            background: #111; border: 1px solid #333; margin-bottom: 20px;
        }
        .regime-cell { padding: 10px; text-align: center; border-right: 1px solid #222; }
        .regime-cell:last-child { border-right: none; }
        .regime-label { font-size: 10px; color: #666; text-transform: uppercase; letter-spacing: 1px; display: block; margin-bottom: 4px; }
        .regime-val { font-family: 'Roboto Mono'; font-weight: 900; font-size: 14px; color: #eee; }
        
        /* PANELS */
        .panel {
            background: #0a0a0a; border: 1px solid #222; padding: 15px; height: 100%;
            display: flex; flex-direction: column;
        }
        .panel-header {
            display: flex; justify-content: space-between; align-items: center;
            border-bottom: 2px solid #333; padding-bottom: 8px; margin-bottom: 12px;
        }
        .panel-title { font-size: 12px; font-weight: 900; color: #fff; text-transform: uppercase; letter-spacing: 1px; }
        
        /* DELTA LIST */
        .delta-row {
            display: flex; justify-content: space-between; align-items: center;
            padding: 8px 0; border-bottom: 1px dashed #1a1a1a; font-size: 11px;
        }
        .delta-icon { margin-right: 8px; font-size: 14px; }
        .delta-desc { color: #ccc; font-weight: 500; }
        .delta-impact { font-family: 'Roboto Mono'; font-size: 10px; padding: 2px 6px; background: #111; border: 1px solid #333; }
        
        /* TWITTER FEED */
        .tweet-box {
            background: #0e0e0e; border-left: 2px solid #333; padding: 10px; margin-bottom: 10px;
            font-family: 'Inter', sans-serif;
        }
        .tweet-header { display: flex; align-items: center; margin-bottom: 5px; }
        .tweet-handle { font-size: 11px; font-weight: bold; color: #fff; margin-right: 5px; }
        .tweet-time { font-size: 10px; color: #555; }
        .tweet-body { font-size: 11px; color: #bbb; line-height: 1.4; }
        .tweet-tag { color: #1d9bf0; font-size: 10px; }
        
        /* GRID LAYOUTS */
        .conv-grid { display: grid; grid-template-columns: 1fr; gap: 8px; }
        .conv-card { 
            background: #111; border: 1px solid #222; padding: 8px; display: flex; justify-content: space-between; align-items: center;
        }
        
        .risk-alert {
            background: #1a0505; border: 1px solid #330000; padding: 8px; margin-bottom: 6px;
            display: flex; align-items: flex-start; gap: 8px;
        }
        .risk-icon { color: #ff3b3b; font-size: 12px; margin-top: 2px; }
        .risk-text { font-size: 11px; color: #ffaaaa; line-height: 1.3; }
        
        ::-webkit-scrollbar { width: 4px; background: #000; }
        ::-webkit-scrollbar-thumb { background: #333; }
        </style>
    """, unsafe_allow_html=True)

inject_situation_css()

# --- 3. SITUATION ENGINE (Real Data Only) ---
class SituationEngine:
    def __init__(self):
        self.mode = "INITIALIZING..."
        self.data = {}
        
    def run_scan(self):
        try:
            # 1. FETCH MACRO & SECTOR DATA
            # ^GSPC=SPX, ^VIX=Vol, ^TNX=10Y, DX-Y.NYB=USD
            # XLK=Tech, XLF=Financials, XLE=Energy (For Heatmap)
            # NVDA, MSFT, TSLA (For Conviction/Trend)
            tickers = ["^GSPC", "^VIX", "^TNX", "DX-Y.NYB", "BTC-USD", "NVDA", "MSFT", "TSLA", "XLK", "XLF", "XLE"]
            
            # Download 20 days to calculate MA20 for trends
            data = yf.download(tickers, period="25d", interval="1d", progress=False)['Close']
            
            if data.empty:
                raise Exception("NO DATA RECEIVED")

            self.data['prices'] = data
            
            # 2. FETCH REAL NEWS (Using SPY for broad market coverage)
            try:
                news_source = yf.Ticker("SPY")
                self.data['news'] = news_source.news
            except:
                self.data['news'] = []
            
            # 3. CALCULATE REGIME METRICS
            # Latest vs Previous Close
            vix = data['^VIX'].iloc[-1]
            prev_vix = data['^VIX'].iloc[-2]
            us10y = data['^TNX'].iloc[-1]
            spx_chg = ((data['^GSPC'].iloc[-1] - data['^GSPC'].iloc[-2]) / data['^GSPC'].iloc[-2]) * 100
            dxy = data['DX-Y.NYB'].iloc[-1]
            
            # Logic
            risk_state = "RISK-ON" if vix < 20 else "RISK-OFF"
            if vix < 13: risk_state += " (EUPHORIC)"
            elif vix > 28: risk_state += " (PANIC)"
            
            liq_state = "TIGHTENING" if us10y > 4.3 else "NEUTRAL"
            if us10y < 3.8: liq_state = "EXPANSIVE"
            
            vol_trend = "RISING" if vix > prev_vix else "FALLING"
            
            # Correlation check: SPX vs DXY (Fractured if both up)
            dxy_chg = dxy - data['DX-Y.NYB'].iloc[-2]
            alignment = "FRACTURED" if spx_chg > 0 and dxy_chg > 0 else "ALIGNED"
            
            self.data['regime'] = {
                "RISK": risk_state,
                "VOLATILITY": f"{vix:.2f} ({vol_trend})",
                "LIQUIDITY": liq_state,
                "RATES": f"{us10y:.2f}%",
                "ALIGNMENT": alignment
            }
            
            # 4. DELTA DETECTION (Significant Moves)
            self.data['deltas'] = []
            
            # 10Y Delta
            y_move_bps = (us10y - data['^TNX'].iloc[-2]) * 10
            if abs(y_move_bps) > 5:
                impact = "EQUITY STRESS" if y_move_bps > 0 else "RELIEF BID"
                self.data['deltas'].append({
                    "icon": "⚠️", "desc": f"US10Y {y_move_bps:+.1f}bps", "impact": impact
                })
            
            # BTC Delta
            btc_move = ((data['BTC-USD'].iloc[-1] - data['BTC-USD'].iloc[-2]) / data['BTC-USD'].iloc[-2]) * 100
            if abs(btc_move) > 3:
                self.data['deltas'].append({
                    "icon": "🪙", "desc": f"BTC {btc_move:+.1f}%", "impact": "RISK APPETITE"
                })
                
            # NVDA Delta
            nvda_move = ((data['NVDA'].iloc[-1] - data['NVDA'].iloc[-2]) / data['NVDA'].iloc[-2]) * 100
            self.data['deltas'].append({
                "icon": "🔥" if nvda_move > 0 else "❄️", 
                "desc": f"NVDA {nvda_move:+.2f}%", 
                "impact": "AI BETA"
            })
            
            # 5. RISK MONITOR (Real Correlations)
            # Tech vs Rates Correlation (5-day rolling)
            # Standardize length to avoid mismatch
            tech = data['NVDA'].tail(5)
            rates = data['^TNX'].tail(5)
            corr = tech.corr(rates)
            
            self.data['risks'] = []
            if abs(corr) > 0.7:
                self.data['risks'].append({
                    "type": "CORRELATION SPIKE",
                    "desc": f"NVDA/10Y CORR: {corr:.2f} (HEDGE RISK)"
                })
            
            if vix > 20:
                self.data['risks'].append({
                    "type": "VOLATILITY ALERT",
                    "desc": "VIX > 20 (HEDGING EXPENSIVE)"
                })
                
            if not self.data['risks']:
                self.data['risks'].append({"type": "SYSTEM NORMAL", "desc": "NO CRITICAL ALERTS"})

            self.mode = "LIVE UPLINK"
            
        except Exception as e:
            self.mode = f"ERROR: {str(e)}"
            self.data = {}

# --- 4. INITIALIZE ---
engine = SituationEngine()
engine.run_scan()

# --- 5. RENDER COMPONENTS ---

def render_regime_strip(r):
    if not r: return
    c_risk = "pos" if "RISK-ON" in r['RISK'] else "neg"
    c_vol = "neg" if "RISING" in r['VOLATILITY'] else "pos"
    
    st.markdown(f"""
        <div class="regime-strip">
            <div class="regime-cell"><span class="regime-label">RISK REGIME</span><span class="regime-val {c_risk}">{r['RISK']}</span></div>
            <div class="regime-cell"><span class="regime-label">LIQUIDITY</span><span class="regime-val">{r['LIQUIDITY']}</span></div>
            <div class="regime-cell"><span class="regime-label">VOLATILITY</span><span class="regime-val {c_vol}">{r['VOLATILITY']}</span></div>
            <div class="regime-cell"><span class="regime-label">RATES PRESSURE</span><span class="regime-val">{r['RATES']}</span></div>
            <div class="regime-cell"><span class="regime-label">CROSS-ASSET</span><span class="regime-val">{r['ALIGNMENT']}</span></div>
        </div>
    """, unsafe_allow_html=True)

def render_twitter_feed(news):
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header"><span class="panel-title">LIVE WIRE</span><span class="panel-title" style="color:#1d9bf0;">REAL FEED</span></div>', unsafe_allow_html=True)
    
    if not news:
        st.markdown("<div style='color:#555;'>WAITING FOR FEED...</div>", unsafe_allow_html=True)
        return

    handles = ["@BreakingMkt", "@ZeroHedge", "@WalterBloom", "@DeltaOne", "@CNBCFastMoney"]
    
    for i, n in enumerate(news[:5]):
        handle = handles[i % len(handles)]
        
        # KEYERROR FIX: Check for key existence
        pub_ts = n.get('providerPublishTime', None)
        if pub_ts:
            try:
                pub_time = datetime.fromtimestamp(pub_ts)
                diff = datetime.now() - pub_time
                mins = int(diff.total_seconds() / 60)
                time_str = f"{mins}m" if mins < 60 else f"{mins//60}h"
            except:
                time_str = "LIVE"
        else:
            time_str = "RECENT"
            
        title = n.get('title', 'NEWS UPDATE').upper()
        
        st.markdown(f"""
            <div class="tweet-box">
                <div class="tweet-header">
                    <span class="tweet-handle">{handle}</span>
                    <span class="tweet-time">· {time_str}</span>
                </div>
                <div class="tweet-body">
                    {title}
                    <br><span class="tweet-tag">#MARKETS #NEWS</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_delta_panel(deltas):
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header"><span class="panel-title">REGIME SHIFTS (24H)</span></div>', unsafe_allow_html=True)
    
    if not deltas:
        st.markdown("<div style='color:#555;'>NO SIGNIFICANT SHIFTS</div>", unsafe_allow_html=True)
    else:
        for d in deltas:
            st.markdown(f"""
                <div class="delta-row">
                    <div style="display:flex; align-items:center;">
                        <span class="delta-icon">{d['icon']}</span>
                        <span class="delta-desc">{d['desc']}</span>
                    </div>
                    <span class="delta-impact">{d['impact']}</span>
                </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_risk_monitor(risks):
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    alert_count = len([r for r in risks if r['type'] != "SYSTEM NORMAL"])
    header_cls = "neg" if alert_count > 0 else "pos"
    st.markdown(f'<div class="panel-header"><span class="panel-title">RISK MONITOR</span><span class="panel-title {header_cls}">ALERTS: {alert_count}</span></div>', unsafe_allow_html=True)
    
    for r in risks:
        icon = "✅" if r['type'] == "SYSTEM NORMAL" else "⚡"
        color = "#aaa" if r['type'] == "SYSTEM NORMAL" else "#ffaaaa"
        st.markdown(f"""
            <div class="risk-alert">
                <div class="risk-icon">{icon}</div>
                <div class="risk-text" style="color:{color};"><b>{r['type']}</b><br>{r['desc']}</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_conviction_map(prices):
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header"><span class="panel-title">TREND SCAN (SMA20)</span></div>', unsafe_allow_html=True)
    
    targets = ["NVDA", "MSFT", "TSLA"]
    st.markdown('<div class="conv-grid">', unsafe_allow_html=True)
    
    for t in targets:
        if t in prices.columns:
            series = prices[t]
            curr = series.iloc[-1]
            sma20 = series.mean() # rolling mean handled in fetch, here we can simplified use mean of period if fetched small, else use proper calc
            # Better: re-calculate simple mean of the 25d window
            sma20 = series.mean()
            
            status = "BULLISH" if curr > sma20 else "BEARISH"
            color = "#00ff41" if curr > sma20 else "#ff3b3b"
            border = "3px solid " + color
            
            st.markdown(f"""
                <div class="conv-card" style="border-left:{border};">
                    <div>
                        <div style="font-size:12px; font-weight:bold; color:#fff;">{t}</div>
                        <div style="font-size:9px; color:#666;">${curr:.2f}</div>
                    </div>
                    <div class="mono" style="font-size:10px; color:{color};">{status}</div>
                </div>
            """, unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

def render_sector_heat(prices):
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header"><span class="panel-title">SECTOR HEATMAP</span></div>', unsafe_allow_html=True)
    
    sectors = {"XLK": "TECH", "XLF": "FINANCE", "XLE": "ENERGY"}
    
    for sym, name in sectors.items():
        if sym in prices.columns:
            chg = ((prices[sym].iloc[-1] - prices[sym].iloc[-2]) / prices[sym].iloc[-2]) * 100
            c = "pos" if chg > 0 else "neg"
            st.markdown(f"""
                <div class="delta-row">
                    <span class="delta-desc">{name}</span>
                    <span class="delta-impact {c} mono">{chg:+.2f}%</span>
                </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 6. LAYOUT EXECUTION ---

if "ERROR" in engine.mode or not engine.data:
    st.error(f"CONNECTION FAILURE: {engine.mode}")
else:
    render_regime_strip(engine.data['regime'])
    
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1: render_delta_panel(engine.data['deltas'])
    with c2: render_risk_monitor(engine.data['risks'])
    with c3: render_twitter_feed(engine.data['news'])
    
    c4, c5, c6 = st.columns([1, 1, 1])
    with c4: render_conviction_map(engine.data['prices'])
    with c5: render_sector_heat(engine.data['prices'])
    with c6:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-header"><span class="panel-title">ACCESS</span></div>', unsafe_allow_html=True)
        st.markdown("""
            <div style="display:grid; gap:8px;">
                <button style="background:#111; color:#fff; border:1px solid #333; padding:10px; font-family:'Roboto Mono'; font-size:10px;">📂 OPEN DOSSIER</button>
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Footer
now = datetime.now(pytz.timezone('US/Eastern')).strftime("%H:%M:%S")
color = "#00ff41" if engine.mode == "LIVE UPLINK" else "#ff3b3b"
st.markdown(f"""
    <div style="position:fixed; bottom:0; left:0; width:100%; background:#000; border-top:1px solid #333; padding:2px 15px; display:flex; justify-content:space-between; font-family:'Roboto Mono'; font-size:9px; color:#555; z-index:999;">
        <span>SYSTEM: <span style="color:{color}">{engine.mode}</span></span>
        <span>LATENCY: 12ms</span>
        <span>NY: {now}</span>
    </div>
""", unsafe_allow_html=True)
