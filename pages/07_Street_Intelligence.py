import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import pytz

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="STREET_INTEL_LIVE", initial_sidebar_state="collapsed")

# --- 2. CSS ENGINE (Amber Dossier Theme) ---
def inject_dossier_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&family=Inter:wght@400;600;800&display=swap');
        
        .stApp { background-color: #050505; color: #d0d0d0; font-family: 'Inter', sans-serif; }
        * { border-radius: 0px !important; }
        .block-container { padding: 1rem 1.5rem; max-width: 100%; }
        [data-testid="stHeader"] { display: none; }
        
        /* COLORS */
        .pos { color: #00ff41 !important; }
        .neg { color: #ff3b3b !important; }
        .warn { color: #ffcc00 !important; }
        .amber { color: #ffae00 !important; text-shadow: 0 0 8px rgba(255, 174, 0, 0.25); }
        .mono { font-family: 'Roboto Mono', monospace; }
        
        /* PANELS */
        .panel {
            background: #0b0b0b; border: 1px solid #222; margin-bottom: 12px; padding: 12px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5); position: relative; min-height: 150px;
        }
        .panel-header {
            border-bottom: 1px solid #333; padding-bottom: 6px; margin-bottom: 10px;
            display: flex; justify-content: space-between; align-items: center;
        }
        .panel-title { font-size: 11px; font-weight: 800; color: #ffae00; text-transform: uppercase; letter-spacing: 1px; }
        
        /* DATA GRIDS */
        .own-row {
            display: grid; grid-template-columns: 3fr 1fr 1fr; 
            font-family: 'Roboto Mono', monospace; font-size: 10px; 
            padding: 5px 0; border-bottom: 1px dashed #1a1a1a; align-items: center;
        }
        .own-header { font-weight: bold; color: #555; font-size: 9px; border-bottom: 1px solid #333; padding-bottom: 5px; margin-bottom: 5px; }
        
        .cp-bar-bg { width: 100%; background: #1a1a1a; height: 4px; margin: 4px 0; }
        .cp-bar-fill { height: 100%; }
        
        .header-main { font-size: 20px; font-weight: 900; letter-spacing: 2px; color: #fff; text-transform: uppercase; }
        .header-sub { font-size: 10px; color: #ffae00; font-family: 'Roboto Mono'; letter-spacing: 1px; }
        
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

# --- 3. REAL DATA ENGINE ---
class RealIntelEngine:
    def __init__(self, ticker):
        self.ticker = ticker
        self.mode = "CONNECTING..."
        self.data = {}
        
    def fetch(self):
        try:
            t = yf.Ticker(self.ticker)
            
            # 1. PRICE HISTORY (Real)
            hist = t.history(period="1mo", interval="1d") 
            intra = t.history(period="1d", interval="5m")
            
            # FLATTEN COLUMNS (Critical Fix for MultiIndex Error)
            if isinstance(hist.columns, pd.MultiIndex): hist.columns = hist.columns.get_level_values(0)
            if isinstance(intra.columns, pd.MultiIndex): intra.columns = intra.columns.get_level_values(0)
            
            # Fallback for empty intraday (e.g. weekend)
            if intra.empty: intra = hist.tail(5)
            
            if hist.empty: 
                self.mode = "NO DATA FOUND"
                return

            self.data['hist'] = hist
            self.data['intra'] = intra
            
            # 2. FUNDAMENTAL DATA (Real)
            self.data['info'] = t.info
            try:
                self.data['holders'] = t.institutional_holders
            except:
                self.data['holders'] = None
            
            # 3. DERIVED METRICS (Real Math)
            self._calc_real_flow()
            self._calc_real_regime()
            self._calc_real_liquidity()
            self._format_ownership()
            self._generate_real_narrative()
            
            self.mode = "LIVE UPLINK"
            
        except Exception as e:
            self.mode = f"API ERROR: {str(e)}"

    def _calc_real_flow(self):
        # Buy/Sell Pressure based on Candle Color * Volume
        df = self.data['intra'].copy()
        df['BuyVol'] = np.where(df['Close'] > df['Open'], df['Volume'], 0)
        df['SellVol'] = np.where(df['Close'] < df['Open'], df['Volume'], 0)
        
        total = df['Volume'].sum() or 1
        buy_pct = (df['BuyVol'].sum() / total) * 100
        sell_pct = (df['SellVol'].sum() / total) * 100
        
        # Normalize
        if buy_pct + sell_pct > 0:
            norm = 100 / (buy_pct + sell_pct)
            buy_pct *= norm
            sell_pct *= norm
            
        self.data['flow'] = {
            "BUY": buy_pct, 
            "SELL": sell_pct, 
            "NET": "ACCUM" if buy_pct > sell_pct else "DISTRIB"
        }

    def _calc_real_regime(self):
        # RSI & Trend from Real Price
        df = self.data['hist']
        close = df['Close']
        
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs)).iloc[-1]
        if np.isnan(rsi): rsi = 50
        
        sma20 = close.rolling(20).mean().iloc[-1]
        if np.isnan(sma20): sma20 = close.mean()
        
        regime = "NEUTRAL"
        if close.iloc[-1] > sma20: regime = "BULLISH TREND"
        elif close.iloc[-1] < sma20: regime = "BEARISH TREND"
        if rsi > 70: regime = "OVERBOUGHT"
        elif rsi < 30: regime = "OVERSOLD"
        
        self.data['regime_stats'] = {
            "RSI": rsi, "SMA20": sma20, "STATE": regime,
            "BETA": self.data['info'].get('beta', 'N/A'),
            "SHORT": self.data['info'].get('shortRatio', 'N/A')
        }

    def _calc_real_liquidity(self):
        shares = self.data['info'].get('sharesOutstanding', 1)
        float_shares = self.data['info'].get('floatShares', 1)
        
        if shares and float_shares:
            locked_pct = ((shares - float_shares) / shares) * 100
        else:
            locked_pct = 0
        
        locked_pct = max(0, min(100, locked_pct))
        self.data['liq'] = {"LOCKED": round(locked_pct, 1), "FLOAT": round(100 - locked_pct, 1)}

    def _format_ownership(self):
        # Prepare Real 13F Table
        holders_list = []
        if self.data['holders'] is not None and not self.data['holders'].empty:
            holders_list = self.data['holders'].head(5).to_dict('records')
        else:
            # Fallback to Aggregate Stats if 13F list unavailable
            inst_pct = self.data['info'].get('heldPercentInstitutions', 0) * 100
            insider_pct = self.data['info'].get('heldPercentInsiders', 0) * 100
            holders_list = [
                {"Holder": "INSTITUTIONAL TOTAL", "Shares": f"{inst_pct:.1f}%", "Date Reported": "AGGREGATE"},
                {"Holder": "INSIDER TOTAL", "Shares": f"{insider_pct:.1f}%", "Date Reported": "AGGREGATE"}
            ]
        self.data['top_holders'] = holders_list

    def _generate_real_narrative(self):
        info = self.data['info']
        stats = self.data['regime_stats']
        
        rec = info.get('recommendationKey', 'N/A').upper().replace("_", " ")
        target = info.get('targetMeanPrice', 'N/A')
        curr = self.data['hist']['Close'].iloc[-1]
        
        upside_str = ""
        if isinstance(target, (int, float)):
            upside = ((target - curr) / curr) * 100
            upside_str = f"ANALYST TARGET (${target}) IMPLIES {upside:.1f}% UPSIDE."
            
        self.data['narrative_text'] = f"""
        STREET CONSENSUS IS <b>{rec}</b>. {upside_str}
        TECHNICAL STATE IS <b>{stats['STATE']}</b> (RSI {stats['RSI']:.1f}).
        BETA PROFILE: {stats['BETA']} (MARKET SENSITIVITY).
        """

# --- 4. RENDER UI ---
with st.sidebar:
    st.markdown("### // INTEL_DESK")
    target = st.text_input("TICKER", "NVDA").upper()

engine = RealIntelEngine(target)
engine.fetch()

if "API ERROR" in engine.mode or engine.mode == "NO DATA FOUND":
    st.error(f"CONNECTION FAILURE: {engine.mode}")
else:
    # Header
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(f'<div class="header-main">{target} // LIVE DOSSIER</div>', unsafe_allow_html=True)
        st.markdown('<div class="header-sub">REAL-TIME DATA ONLY • NO SIMULATION</div>', unsafe_allow_html=True)
    with c2:
        regime = engine.data['regime_stats']['STATE']
        color = "#00ff41" if "BULL" in regime else "#ff3b3b" if "BEAR" in regime else "#ffae00"
        st.markdown(f'<div style="text-align:right; font-family:monospace; color:{color}; border:1px solid {color}; padding:5px;">REGIME: {regime}</div>', unsafe_allow_html=True)
    st.markdown("---")

    # Main Grid
    c1, c2 = st.columns([1, 2])
    
    with c1:
        # Liquidity
        liq = engine.data['liq']
        st.markdown('<div class="panel"><div class="panel-header"><span class="panel-title">FLOAT STRUCTURE</span></div>', unsafe_allow_html=True)
        st.markdown(f"""
            <div style="display:flex; height:8px; width:100%; background:#222; margin-bottom:5px;">
                <div style="width:{liq['LOCKED']}%; background:#444;"></div>
                <div style="width:{liq['FLOAT']}%; background:#00ff41;"></div>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:8px; color:#666;">
                <span>LOCKED/INSIDERS: {liq['LOCKED']}%</span><span>PUBLIC FLOAT: {liq['FLOAT']}%</span>
            </div>
        </div>""", unsafe_allow_html=True)
        
        # Flow
        flow = engine.data['flow']
        st.markdown('<div class="panel"><div class="panel-header"><span class="panel-title">VOLUME PRESSURE</span><span class="panel-meta">REAL FLOW</span></div>', unsafe_allow_html=True)
        st.markdown(f"""
            <div style="font-size:10px; margin-bottom:5px; display:flex; justify-content:space-between;">
                <span>BUYING PRESSURE</span><span class="pos mono">{flow['BUY']:.1f}%</span>
            </div>
            <div class="cp-bar-bg"><div class="cp-bar-fill" style="width:{flow['BUY']}%; background:#00ff41;"></div></div>
            <div style="font-size:10px; margin-top:10px; margin-bottom:5px; display:flex; justify-content:space-between;">
                <span>SELLING PRESSURE</span><span class="neg mono">{flow['SELL']:.1f}%</span>
            </div>
            <div class="cp-bar-bg"><div class="cp-bar-fill" style="width:{flow['SELL']}%; background:#ff3b3b;"></div></div>
            <div style="margin-top:15px; border-top:1px dashed #333; padding-top:10px; text-align:center;">
                <span style="font-size:9px; color:#666;">NET FLOW STATE</span>
                <div style="font-size:16px; font-weight:bold; color:#fff;">{flow['NET']}</div>
            </div>
        </div>""", unsafe_allow_html=True)
        
        # Narrative
        st.markdown('<div class="panel"><div class="panel-header"><span class="panel-title">TECHNICAL NARRATIVE</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="narrative-text">{engine.data["narrative_text"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        # Ownership
        st.markdown('<div class="panel"><div class="panel-header"><span class="panel-title">INSTITUTIONAL HOLDERS</span><span class="panel-meta">13F / AGGREGATE</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="own-row own-header"><span>ENTITY</span><span>SHARES / %</span><span>REPORTED</span></div>', unsafe_allow_html=True)
        for h in engine.data['top_holders']:
            name = h.get('Holder', 'N/A')
            shares = h.get('Shares', 0)
            if isinstance(shares, (int, float)) and shares > 1e6: share_str = f"{shares/1e6:.1f}M"
            else: share_str = str(shares)
            date = h.get('Date Reported', 'N/A')
            if isinstance(date, (pd.Timestamp, datetime)): date = date.strftime('%Y-%m-%d')
            st.markdown(f'<div class="own-row"><span style="color:#ddd; font-weight:600;">{name}</span><span class="mono amber">{share_str}</span><span class="mono muted">{date}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Chart
        st.markdown('<div class="panel"><div class="panel-header"><span class="panel-title">PRICE ACTION</span><span class="panel-meta">1 MONTH</span></div>', unsafe_allow_html=True)
        fig = go.Figure(data=[go.Candlestick(x=engine.data['hist'].index, open=engine.data['hist']['Open'], high=engine.data['hist']['High'], low=engine.data['hist']['Low'], close=engine.data['hist']['Close'], increasing_line_color='#ffae00', decreasing_line_color='#333')])
        fig.update_layout(template="plotly_dark", height=250, margin=dict(l=0,r=40,t=10,b=0), paper_bgcolor='#0b0b0b', plot_bgcolor='#0b0b0b', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Footer
now = datetime.now(pytz.timezone('US/Eastern')).strftime("%H:%M:%S")
color = "#00ff41" if engine.mode == "LIVE UPLINK" else "#ff3b3b"
st.markdown(f'<div class="status-bar"><span>STATUS: <span style="color:{color}">{engine.mode}</span></span><span>NY: {now} ET</span></div>', unsafe_allow_html=True)
