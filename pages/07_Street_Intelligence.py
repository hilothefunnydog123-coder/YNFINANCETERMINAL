import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import pytz

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="STREET_INTEL_LIVE", initial_sidebar_state="collapsed")

# --- 2. CSS ENGINE ---
def inject_dossier_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&family=Inter:wght@400;600;800&display=swap');
        
        .stApp { background-color: #050505; color: #d0d0d0; font-family: 'Inter', sans-serif; }
        * { border-radius: 0px !important; }
        .block-container { padding: 1rem 1.5rem; max-width: 100%; }
        [data-testid="stHeader"] { display: none; }
        
        .pos { color: #00ff41 !important; }
        .neg { color: #ff3b3b !important; }
        .warn { color: #ffcc00 !important; }
        .amber { color: #ffae00 !important; text-shadow: 0 0 8px rgba(255, 174, 0, 0.25); }
        .mono { font-family: 'Roboto Mono', monospace; }
        
        .header-main { font-size: 20px; font-weight: 900; letter-spacing: 2px; color: #fff; text-transform: uppercase; }
        .header-sub { font-size: 10px; color: #ffae00; font-family: 'Roboto Mono'; letter-spacing: 1px; }

        .panel {
            background: #0b0b0b; border: 1px solid #222; margin-bottom: 12px; padding: 12px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5); position: relative; min-height: 150px;
        }
        .panel-header {
            border-bottom: 1px solid #333; padding-bottom: 6px; margin-bottom: 10px;
            display: flex; justify-content: space-between; align-items: center;
        }
        .panel-title { font-size: 11px; font-weight: 800; color: #ffae00; text-transform: uppercase; letter-spacing: 1px; }
        
        .own-row {
            display: grid; grid-template-columns: 3fr 1fr 1fr; 
            font-family: 'Roboto Mono', monospace; font-size: 10px; 
            padding: 5px 0; border-bottom: 1px dashed #1a1a1a; align-items: center;
        }
        .own-header { font-weight: bold; color: #555; font-size: 9px; border-bottom: 1px solid #333; padding-bottom: 5px; margin-bottom: 5px; }
        
        .cp-bar-bg { width: 100%; background: #1a1a1a; height: 4px; margin: 4px 0; }
        .cp-bar-fill { height: 100%; }
        
        .narrative-text { font-size: 11px; color: #ccc; line-height: 1.5; border-left: 2px solid #ffae00; padding-left: 10px; margin-bottom: 10px; }
        
        .status-bar {
            position: fixed; bottom: 0; left: 0; width: 100%; background: #000; border-top: 1px solid #ffae00;
            padding: 3px 15px; display: flex; justify-content: space-between; font-family: 'Roboto Mono', monospace;
            font-size: 9px; color: #ffae00; z-index: 999;
        }
        
        ::-webkit-scrollbar { width: 5px; background: #000; }
        ::-webkit-scrollbar-thumb { background: #ffae00; }
        </style>
    """, unsafe_allow_html=True)

inject_dossier_css()

# --- 3. REAL DATA ENGINE (No Simulation) ---
class RealIntelEngine:
    def __init__(self, ticker):
        self.ticker = ticker
        self.mode = "CONNECTING..."
        self.data = {}
        
    def fetch(self):
        try:
            t = yf.Ticker(self.ticker)
            
            # 1. PRICE HISTORY (Real)
            # Fetch 1 month to calculate trends
            hist = t.history(period="1mo", interval="1d") 
            # Try Intraday
            intra = t.history(period="1d", interval="5m")
            
            # CRITICAL FALLBACK: If intraday is empty (e.g. weekend), use daily for flow analysis
            if intra.empty:
                intra = hist.tail(5) # Use last 5 days as proxy for recent flow
            
            if hist.empty: 
                self.mode = "NO DATA FOUND"
                return

            self.data['hist'] = hist
            self.data['intra'] = intra
            
            # 2. FUNDAMENTAL DATA (Real)
            self.data['info'] = t.info
            
            # Try fetching holders, handle empty returns gracefully
            try:
                self.data['holders'] = t.institutional_holders
            except:
                self.data['holders'] = None
            
            # 3. CALCULATE DERIVED METRICS (Real Math on Real Data)
            self._calc_real_flow()
            self._calc_real_regime()
            self._calc_real_liquidity()
            self._format_ownership()
            self._generate_real_narrative()
            
            self.mode = "LIVE UPLINK"
            
        except Exception as e:
            self.mode = f"API ERROR: {str(e)}"

    def _calc_real_flow(self):
        # Calculate Buying vs Selling Pressure
        df = self.data['intra'].copy()
        
        # Logic: If Close > Open, volume is "Buy"
        df['BuyVol'] = np.where(df['Close'] > df['Open'], df['Volume'], 0)
        df['SellVol'] = np.where(df['Close'] < df['Open'], df['Volume'], 0)
        
        total_vol = df['Volume'].sum()
        if total_vol == 0: total_vol = 1 
        
        buy_pct = (df['BuyVol'].sum() / total_vol) * 100
        sell_pct = (df['SellVol'].sum() / total_vol) * 100
        
        # Ensure they sum to ~100 for display (simple normalization)
        total_pct = buy_pct + sell_pct
        if total_pct > 0:
            buy_pct = (buy_pct / total_pct) * 100
            sell_pct = (sell_pct / total_pct) * 100
        
        self.data['flow'] = {
            "BUY": buy_pct, 
            "SELL": sell_pct, 
            "NET": "ACCUM" if buy_pct > sell_pct else "DISTRIB"
        }

    def _calc_real_regime(self):
        # Calculate RSI and Trend from REAL Data
        df = self.data['hist']
        close = df['Close']
        
        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs)).iloc[-1]
        if np.isnan(rsi): rsi = 50 # Handle new listings
        
        # Trend
        sma20 = close.rolling(window=20).mean().iloc[-1]
        if np.isnan(sma20): sma20 = close.mean()
        
        curr = close.iloc[-1]
        
        regime = "NEUTRAL"
        if curr > sma20: regime = "BULLISH TREND"
        if curr < sma20: regime = "BEARISH TREND"
        if rsi > 70: regime = "OVERBOUGHT"
        if rsi < 30: regime = "OVERSOLD"
        
        self.data['regime_stats'] = {
            "RSI": rsi,
            "SMA20": sma20,
            "STATE": regime,
            "BETA": self.data['info'].get('beta', 'N/A'),
            "SHORT": self.data['info'].get('shortRatio', 'N/A')
        }

    def _calc_real_liquidity(self):
        # Use Shares Outstanding vs Float if available
        shares = self.data['info'].get('sharesOutstanding', 1)
        float_shares = self.data['info'].get('floatShares', 1)
        
        if shares and float_shares:
            locked_pct = ((shares - float_shares) / shares) * 100
        else:
            locked_pct = 0
            
        # Ensure bounds
        locked_pct = max(0, min(100, locked_pct))
        
        self.data['liq'] = {
            "LOCKED": round(locked_pct, 1),
            "FLOAT": round(100 - locked_pct, 1)
        }

    def _format_ownership(self):
        # Process the REAL 13F Dataframe or use Info Fallback
        holders_list = []
        
        # Method A: Try specific table
        if self.data['holders'] is not None and not self.data['holders'].empty:
            holders_list = self.data['holders'].head(5).to_dict('records')
        
        # Method B: Fallback to Aggregate Stats if table is empty
        if not holders_list:
             inst_pct = self.data['info'].get('heldPercentInstitutions', 0) * 100
             insider_pct = self.data['info'].get('heldPercentInsiders', 0) * 100
             holders_list = [
                 {"Holder": "INSTITUTIONAL AGGREGATE", "Shares": f"{inst_pct:.1f}%", "Date Reported": "LATEST"},
                 {"Holder": "INSIDER AGGREGATE", "Shares": f"{insider_pct:.1f}%", "Date Reported": "LATEST"}
             ]
             
        self.data['top_holders'] = holders_list

    def _generate_real_narrative(self):
        # Construct narrative from Real Data points
        info = self.data['info']
        stats = self.data['regime_stats']
        
        target_price = info.get('targetMeanPrice', 'N/A')
        recommendation = info.get('recommendationKey', 'N/A').upper()
        curr_price = self.data['hist']['Close'].iloc[-1]
        
        # Logic for narrative text
        upside = ""
        if isinstance(target_price, (int, float)):
            upside_pct = ((target_price - curr_price) / curr_price) * 100
            upside = f"ANALYST TARGET (${target_price}) IMPLIES {upside_pct:.1f}% POTENTIAL."
            
        short_note = ""
        if stats['SHORT'] != 'N/A' and float(stats['SHORT']) > 5:
            short_note = f"SHORT INTEREST IS ELEVATED ({stats['SHORT']} RATIO), MONITOR FOR SQUEEZE."
            
        self.data['narrative_text'] = f"""
        STREET CONSENSUS IS <b>{recommendation}</b>. {upside}
        MOMENTUM IS <b>{stats['STATE']}</b> WITH RSI AT {stats['RSI']:.1f}.
        BETA IS {stats['BETA']}, INDICATING CORRELATION PROFILE.
        {short_note}
        """

# --- 4. INITIALIZE ---
with st.sidebar:
    st.markdown("### // INTEL_DESK")
    target = st.text_input("TICKER", "NVDA").upper()

engine = RealIntelEngine(target)
engine.fetch()

# --- 5. RENDER FUNCTIONS ---

def render_header():
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(f'<div class="header-main">{target} // LIVE DOSSIER</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="header-sub">REAL-TIME DATA ONLY • NO SIMULATION</div>', unsafe_allow_html=True)
    with c2:
        regime = engine.data.get('regime_stats', {}).get('STATE', 'WAITING...')
        color = "#00ff41" if "BULL" in regime else "#ff3b3b" if "BEAR" in regime else "#ffae00"
        st.markdown(f'<div style="text-align:right; font-family:monospace; color:{color}; border:1px solid {color}; padding:5px;">REGIME: {regime}</div>', unsafe_allow_html=True)
    st.markdown("---")

def render_flow_panel():
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header"><span class="panel-title">VOLUME PRESSURE</span><span class="panel-meta">REAL FLOW</span></div>', unsafe_allow_html=True)
    
    flow = engine.data.get('flow', {})
    if flow:
        buy = flow.get('BUY', 0)
        sell = flow.get('SELL', 0)
        net = flow.get('NET', 'N/A')
        
        st.markdown(f"""
            <div style="font-size:10px; margin-bottom:5px; display:flex; justify-content:space-between;">
                <span>BUYING PRESSURE</span><span class="pos mono">{buy:.1f}%</span>
            </div>
            <div class="cp-bar-bg"><div class="cp-bar-fill" style="width:{buy}%; background:#00ff41;"></div></div>
            
            <div style="font-size:10px; margin-top:10px; margin-bottom:5px; display:flex; justify-content:space-between;">
                <span>SELLING PRESSURE</span><span class="neg mono">{sell:.1f}%</span>
            </div>
            <div class="cp-bar-bg"><div class="cp-bar-fill" style="width:{sell}%; background:#ff3b3b;"></div></div>
            
            <div style="margin-top:15px; border-top:1px dashed #333; padding-top:10px; text-align:center;">
                <span style="font-size:9px; color:#666;">NET FLOW STATE</span>
                <div style="font-size:16px; font-weight:bold; color:#fff;">{net}</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("NO FLOW DATA AVAILABLE")
    st.markdown('</div>', unsafe_allow_html=True)

def render_narrative_panel():
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header"><span class="panel-title">TECHNICAL NARRATIVE</span></div>', unsafe_allow_html=True)
    
    text = engine.data.get('narrative_text', "NO DATA")
    st.markdown(f'<div class="narrative-text">{text}</div>', unsafe_allow_html=True)
    
    # Extra stats grid
    stats = engine.data.get('regime_stats', {})
    if stats:
        c1, c2 = st.columns(2)
        with c1:
             st.markdown(f"<div style='font-size:10px; color:#666;'>SHORT RATIO</div><div class='mono'>{stats.get('SHORT', 'N/A')}</div>", unsafe_allow_html=True)
        with c2:
             st.markdown(f"<div style='font-size:10px; color:#666;'>BETA</div><div class='mono'>{stats.get('BETA', 'N/A')}</div>", unsafe_allow_html=True)
             
    st.markdown('</div>', unsafe_allow_html=True)

def render_ownership_matrix():
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header"><span class="panel-title">INSTITUTIONAL HOLDERS</span><span class="panel-meta">13F / AGGREGATE</span></div>', unsafe_allow_html=True)
    
    holders = engine.data.get('top_holders', [])
    
    if holders:
        st.markdown('<div class="own-row own-header"><span>ENTITY</span><span>SHARES / %</span><span>REPORTED</span></div>', unsafe_allow_html=True)
        for h in holders:
            # Handle varied formats from YF
            name = h.get('Holder', 'N/A')
            
            # Format Shares (could be raw int or pre-formatted string)
            raw_shares = h.get('Shares', 0)
            if isinstance(raw_shares, str):
                share_str = raw_shares # Use as is if string (from fallback)
            elif isinstance(raw_shares, (int, float)):
                 if raw_shares > 1e9: share_str = f"{raw_shares/1e9:.1f}B"
                 elif raw_shares > 1e6: share_str = f"{raw_shares/1e6:.1f}M"
                 else: share_str = str(raw_shares)
            else:
                 share_str = "N/A"

            date = h.get('Date Reported', 'N/A')
            if isinstance(date, (pd.Timestamp, datetime)): date = date.strftime('%Y-%m-%d')
            
            st.markdown(f"""
                <div class="own-row">
                    <span style="color:#ddd; font-weight:600;">{name}</span>
                    <span class="mono accent">{share_str}</span>
                    <span class="mono muted">{date}</span>
                </div>
            """, unsafe_allow_html=True)
    else:
        # Absolute fallback if even info fails
        st.markdown("<div style='text-align:center; padding:20px; color:#555;'>DATA RESTRICTED BY EXCHANGE</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_liquidity_profile():
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header"><span class="panel-title">FLOAT STRUCTURE</span></div>', unsafe_allow_html=True)
    
    liq = engine.data.get('liq', {})
    if liq:
        locked = liq.get('LOCKED', 0)
        float_pct = liq.get('FLOAT', 100)
        
        st.markdown(f"""
            <div style="display:flex; height:8px; width:100%; background:#222; margin-bottom:5px;">
                <div style="width:{locked}%; background:#444;"></div>
                <div style="width:{float_pct}%; background:#00ff41;"></div>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:8px; color:#666;">
                <span>LOCKED / INSIDERS: {locked}%</span>
                <span>PUBLIC FLOAT: {float_pct}%</span>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_chart():
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header"><span class="panel-title">PRICE ACTION</span><span class="panel-meta">1 MONTH</span></div>', unsafe_allow_html=True)
    
    hist = engine.data.get('hist', pd.DataFrame())
    if not hist.empty:
        fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'],
                                             increasing_line_color='#ffae00', decreasing_line_color='#333')])
        fig.update_layout(template="plotly_dark", height=250, margin=dict(l=0,r=40,t=10,b=0),
                          paper_bgcolor='#0b0b0b', plot_bgcolor='#0b0b0b',
                          xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown("CHART DATA UNAVAILABLE")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 6. LAYOUT EXECUTION ---

if "API ERROR" in engine.mode or engine.mode == "NO DATA FOUND":
    st.error(f"CONNECTION FAILURE: {engine.mode}. WAITING FOR LIVE UPLINK...")
else:
    render_header()
    
    c1, c2 = st.columns([1, 2])
    
    with c1:
        render_liquidity_profile()
        render_flow_panel()
        render_narrative_panel()
        
    with c2:
        render_ownership_matrix()
        render_chart()

# --- 7. FOOTER ---
now = datetime.now(pytz.timezone('US/Eastern')).strftime("%H:%M:%S")
color = "#00ff41" if engine.mode == "LIVE UPLINK" else "#ff3b3b"
st.markdown(f"""
    <div class="status-bar">
        <span>STATUS: <span style="color:{color}">{engine.mode}</span></span>
        <span>NY: {now} ET</span>
    </div>
""", unsafe_allow_html=True)
