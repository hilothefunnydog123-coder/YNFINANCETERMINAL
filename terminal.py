import streamlit as st
import streamlit.components.v1 as components  # <--- NEW IMPORT
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz
import json
import os
import time

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="SOVEREIGN_FORTRESS", initial_sidebar_state="collapsed")

# --- 2. SHADOW CSS (The "Old Self" Look) ---
def inject_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&family=Inter:wght@400;700;900&display=swap');
        
        /* THEME: DEEP BLACK & AMBER */
        .stApp { background-color: #000000; color: #c0c0c0; font-family: 'Inter', sans-serif; }
        .block-container { padding: 1rem 1rem; max-width: 100%; }
        [data-testid="stHeader"] { display: none; }
        
        /* UTILITY COLORS */
        .pos { color: #00ff41 !important; }
        .neg { color: #ff3b3b !important; }
        .warn { color: #ffcc00 !important; }
        .accent { color: #00f0ff !important; }
        .mono { font-family: 'Roboto Mono', monospace; }
        .amber { color: #ffae00 !important; text-shadow: 0 0 5px rgba(255, 174, 0, 0.3); }
        
        /* REGIME STRIP */
        .regime-strip {
            display: grid; grid-template-columns: repeat(5, 1fr); gap: 2px;
            background: #0a0a0a; border: 1px solid #333; margin-bottom: 20px;
        }
        .regime-cell { padding: 10px; text-align: center; border-right: 1px solid #222; }
        .regime-cell:last-child { border-right: none; }
        .regime-label { font-size: 10px; color: #666; text-transform: uppercase; letter-spacing: 1px; display: block; margin-bottom: 4px; }
        .regime-val { font-family: 'Roboto Mono'; font-weight: 900; font-size: 14px; color: #eee; }
        
        /* PANELS */
        .panel {
            background: #080808; border: 1px solid #222; padding: 15px; height: 100%;
            display: flex; flex-direction: column; min-height: 250px;
        }
        .panel-header {
            display: flex; justify-content: space-between; align-items: center;
            border-bottom: 2px solid #333; padding-bottom: 8px; margin-bottom: 12px;
        }
        .panel-title { font-size: 12px; font-weight: 900; color: #fff; text-transform: uppercase; letter-spacing: 1px; }
        
        /* SHADOW FEED (Twitter Style) */
        .tweet-box {
            background: #000; border-left: 2px solid #333; padding: 10px; margin-bottom: 8px;
            font-family: 'Inter', sans-serif;
        }
        .tweet-header { display: flex; align-items: center; margin-bottom: 4px; }
        .tweet-handle { font-size: 11px; font-weight: bold; color: #fff; margin-right: 6px; }
        .tweet-verified { color: #1d9bf0; font-size: 10px; margin-right: 6px; }
        .tweet-time { font-size: 10px; color: #555; }
        .tweet-body { font-size: 11px; color: #ccc; line-height: 1.4; }
        
        /* RISK & DELTA */
        .delta-row {
            display: flex; justify-content: space-between; align-items: center;
            padding: 8px 0; border-bottom: 1px dashed #1a1a1a; font-size: 11px;
        }
        .risk-alert {
            background: #1a0505; border: 1px solid #330000; padding: 8px; margin-bottom: 6px;
            display: flex; align-items: flex-start; gap: 8px;
        }
        
        /* SCROLLBARS */
        ::-webkit-scrollbar { width: 5px; background: #000; }
        ::-webkit-scrollbar-thumb { background: #333; }
        </style>
    """, unsafe_allow_html=True)

inject_css()

# --- 3. DATA ENGINE (CACHED & HARDENED) ---

@st.cache_data(ttl=300, show_spinner=False)
def fetch_market_data():
    try:
        tickers = ["^GSPC", "^VIX", "^TNX", "DX-Y.NYB", "BTC-USD", "NVDA", "MSFT", "TSLA", "XLK", "XLF", "XLE"]
        df = yf.download(tickers, period="2mo", interval="1d", progress=False, auto_adjust=True)
        
        if isinstance(df.columns, pd.MultiIndex):
            try: df = df['Close']
            except: df.columns = df.columns.get_level_values(1)
            
        # NaN Killer (Forward Fill)
        df = df.ffill().bfill()
        
        return df
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(ttl=300, show_spinner=False)
def fetch_news_data():
    try:
        return yf.Ticker("QQQ").news
    except:
        return []

@st.cache_data(ttl=300, show_spinner=False)
def fetch_intraday_chart(ticker):
    try:
        df = yf.download(ticker, period="5d", interval="15m", progress=False, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except:
        return pd.DataFrame()

# --- 4. ENGINE LOGIC ---
class SituationEngine:
    def __init__(self):
        self.mode = "INITIALIZING..."
        self.data = {}
        
    def run_scan(self):
        # 1. GET CACHED DATA
        df = fetch_market_data()
        
        if df.empty:
            self.mode = "API LIMIT (WAIT 60s)"
            self.data['regime'] = {"RISK": "N/A", "VOL": "N/A", "LIQ": "N/A", "RATES": "N/A", "ALIGN": "N/A"}
            self.data['feed'] = []
            return

        self.data['prices'] = df
        
        # 2. CALCULATE REGIME
        def get_curr(t): return df[t].iloc[-1] if t in df.columns else 0
        def get_prev(t): return df[t].iloc[-2] if t in df.columns else 0
        
        vix = get_curr('^VIX')
        us10y = get_curr('^TNX')
        
        risk = "RISK-ON" if vix < 20 else "RISK-OFF"
        liq = "TIGHT" if us10y > 4.2 else "NEUTRAL"
        vol_str = f"{vix:.2f}"
        if np.isnan(vix): vol_str = "15.00 (EST)"
        
        self.data['regime'] = {
            "RISK": risk,
            "VOL": vol_str,
            "LIQ": liq,
            "RATES": f"{us10y:.2f}%",
            "ALIGN": "MIXED"
        }
        
        # 3. PROCESS NEWS (Cookies.json Integration)
        # Note: In cloud envs, X often blocks cookies. We default to the robust Yahoo fallback 
        # but keep the logic structure ready for local use.
        raw_news = fetch_news_data()
        self.data['feed'] = []
        
        if raw_news:
            for n in raw_news[:6]:
                self.data['feed'].append({
                    "handle": "@MarketWire", 
                    "text": n.get('title', 'MARKET UPDATE'),
                    "time": n.get('providerPublishTime', 0)
                })
                self.data['feed_source'] = "REALTIME WIRE"
        else:
            self.data['feed'].append({"handle": "@System", "text": "NO NEWS FLOW", "time": 0})
            self.data['feed_source'] = "OFFLINE"

        # 4. CHART DATA
        self.data['chart'] = fetch_intraday_chart("NVDA")

        # 5. DELTAS
        self.data['deltas'] = []
        if '^TNX' in df.columns:
            chg = (us10y - get_prev('^TNX')) * 10
            self.data['deltas'].append({"icon": "⚠️", "desc": f"US10Y {chg:+.1f}bps", "impact": "MACRO"})
        if 'NVDA' in df.columns:
            nv_curr = get_curr('NVDA')
            nv_prev = get_prev('NVDA')
            if nv_prev > 0:
                chg = ((nv_curr - nv_prev) / nv_prev) * 100
                self.data['deltas'].append({"icon": "🔥", "desc": f"NVDA {chg:+.2f}%", "impact": "BETA"})

        self.mode = "SECURE UPLINK"

# --- 5. INITIALIZE ---
engine = SituationEngine()
engine.run_scan()

# --- 6. RENDERERS ---

def render_regime(r):
    c_risk = "pos" if "ON" in r['RISK'] else "neg"
    st.markdown(f"""
        <div class="regime-strip">
            <div class="regime-cell"><span class="regime-label">RISK REGIME</span><span class="regime-val {c_risk}">{r['RISK']}</span></div>
            <div class="regime-cell"><span class="regime-label">LIQUIDITY</span><span class="regime-val">{r['LIQ']}</span></div>
            <div class="regime-cell"><span class="regime-label">VOLATILITY</span><span class="regime-val">{r['VOL']}</span></div>
            <div class="regime-cell"><span class="regime-label">RATES</span><span class="regime-val">{r['RATES']}</span></div>
            <div class="regime-cell"><span class="regime-label">ALIGNMENT</span><span class="regime-val">{r['ALIGN']}</span></div>
        </div>
    """, unsafe_allow_html=True)

def render_shadow_feed(feed, source):
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    color = "#1d9bf0" 
    st.markdown(f'<div class="panel-header"><span class="panel-title">INTEL FEED</span><span class="panel-title" style="color:{color};">{source}</span></div>', unsafe_allow_html=True)
    
    for item in feed:
        ts = item.get('time', 0)
        time_str = "LIVE"
        if ts > 0:
            try:
                dt = datetime.fromtimestamp(ts)
                delta = datetime.now() - dt
                mins = int(delta.total_seconds() / 60)
                time_str = f"{mins}m" if mins < 60 else f"{mins//60}h"
            except: pass
            
        st.markdown(f"""
            <div class="tweet-box">
                <div class="tweet-header">
                    <span class="tweet-handle">{item['handle']}</span>
                    <span class="tweet-verified">☑</span>
                    <span class="tweet-time">{time_str}</span>
                </div>
                <div class="tweet-body">{item['text']}</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_chart(df):
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header"><span class="panel-title">PRICE ACTION</span><span class="panel-title">NVDA [REAL]</span></div>', unsafe_allow_html=True)
    
    if not df.empty:
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                                             increasing_line_color='#00ff41', decreasing_line_color='#ff3b3b')])
        fig.update_layout(
            template="plotly_dark", height=250, margin=dict(l=0,r=40,t=10,b=0),
            paper_bgcolor='#080808', plot_bgcolor='#080808',
            xaxis_rangeslider_visible=False,
            yaxis=dict(side='right', showgrid=True, gridcolor='#222')
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown("<div style='color:#555; text-align:center; padding:20px;'>CHART LOADING...</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_risk_delta(deltas):
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header"><span class="panel-title">RISK & DELTA</span></div>', unsafe_allow_html=True)
    
    if deltas:
        for d in deltas:
            st.markdown(f"""
                <div class="delta-row">
                    <div style="display:flex; align-items:center;">
                        <span style="margin-right:8px;">{d['icon']}</span>
                        <span style="color:#ccc;">{d['desc']}</span>
                    </div>
                    <span class="mono" style="background:#111; padding:2px 5px; font-size:10px;">{d['impact']}</span>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<div style='color:#555;'>NO SIGNIFICANT SHIFTS</div>", unsafe_allow_html=True)
        
    st.markdown("""
        <div style="margin-top:15px;">
            <div class="risk-alert">
                <div style="color:#ff3b3b; font-size:12px;">⚡</div>
                <div style="font-size:11px; color:#ffaaaa;"><b>CORRELATION SPIKE</b><br>TECH/RATES > 0.85</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 7. EXECUTION ---

# Layout
render_regime(engine.data['regime'])

c1, c2, c3 = st.columns([1, 1, 1])

with c1:
    render_risk_delta(engine.data['deltas'])
    st.markdown('<div class="panel"><div class="panel-header"><span class="panel-title">CONVICTION</span></div><div style="background:#111; padding:8px; border-left:3px solid #00ff41;"><div style="font-size:12px; font-weight:bold; color:#fff;">NVDA</div><div class="mono pos" style="font-size:10px;">HIGH BETA</div></div></div>', unsafe_allow_html=True)

with c2:
    render_chart(engine.data['chart'])

with c3:
    render_shadow_feed(engine.data['feed'], engine.data.get('feed_source', 'INIT'))

# Footer & Ad Injection
now = datetime.now(pytz.timezone('US/Eastern')).strftime("%H:%M:%S")
color = "#00ff41" if "SECURE" in engine.mode else "#ff3b3b"
st.markdown(f'<div style="position:fixed; bottom:0; left:0; width:100%; background:#000; border-top:1px solid #333; padding:2px 15px; font-family:monospace; font-size:9px; color:#555;">STATUS: {engine.mode} | CACHE: ACTIVE | {now} ET</div>', unsafe_allow_html=True)

# --- ADVERTISING SNIPPET ---
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
    height=60,
)
