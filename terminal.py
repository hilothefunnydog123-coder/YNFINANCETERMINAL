import streamlit as st
import pandas as pd
import asyncio
import json
import yfinance as yf
from twikit import Client
from streamlit_autorefresh import st_autorefresh
import os
import streamlit.components.v1 as components
import requests
import random
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(
    layout="wide",
    page_title="YN_COMMAND TERMINAL",
    initial_sidebar_state="collapsed"
)

# Auto-refresh every 60 seconds
st_autorefresh(interval=60000, key="refresh")

# ---------------- MODERN STYLE ----------------
st.markdown("""
<style>
    /* IMPORT FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');

    /* GLOBAL RESET */
    html, body, [class*="css"] {
        background-color: #0b0c10; /* Deep Carbon */
        color: #c5c6c7;
        font-family: 'Inter', sans-serif;
    }
    
    /* REMOVE DEFAULT STREAMLIT PADDING */
    .block-container { 
        padding-top: 1rem; 
        padding-bottom: 5rem; 
        max-width: 95rem;
    }
    
    [data-testid="stHeader"] { display: none; }
    
    /* --- GLASSMORPHISM CARDS --- */
    .glass-card {
        background: rgba(31, 40, 51, 0.4);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 24px -1px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        border-color: rgba(102, 252, 241, 0.3);
        box-shadow: 0 8px 32px -4px rgba(0, 0, 0, 0.4);
        transform: translateY(-2px);
    }

    /* --- TYPOGRAPHY --- */
    .header-title {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 32px;
        background: linear-gradient(90deg, #fff, #66fcf1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
    }
    .section-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 14px;
        color: #66fcf1;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        opacity: 0.8;
    }
    .section-title::before {
        content: '';
        display: inline-block;
        width: 8px;
        height: 8px;
        background: #66fcf1;
        border-radius: 50%;
        margin-right: 10px;
        box-shadow: 0 0 8px #66fcf1;
    }

    /* --- HUD METRICS --- */
    .hud-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 15px;
        margin-bottom: 25px;
    }
    .metric-box {
        background: rgba(255,255,255,0.03);
        border-radius: 8px;
        padding: 12px;
        text-align: left;
        border-left: 2px solid rgba(255,255,255,0.1);
        transition: border-left 0.3s;
    }
    .metric-box:hover { border-left: 2px solid #66fcf1; }
    .metric-label { font-size: 10px; color: #8892b0; font-weight: 600; text-transform: uppercase; }
    .metric-value { font-family: 'JetBrains Mono', monospace; font-size: 16px; color: #fff; margin-top: 4px; }
    .metric-delta { font-size: 11px; font-weight: bold; margin-top: 2px; }
    .pos { color: #45a29e; } /* Muted Teal */
    .neg { color: #ef476f; } /* Muted Red */

    /* --- FEED & LISTS --- */
    .feed-item {
        border-bottom: 1px solid rgba(255,255,255,0.05);
        padding: 15px 0;
    }
    .feed-item:last-child { border-bottom: none; }
    
    .rank-row {
        display: flex; align-items: center; justify-content: space-between;
        padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.03);
    }
    
    /* ANIMATED BARS */
    .rank-bar-bg { 
        flex-grow: 1; 
        height: 6px; 
        background: rgba(255,255,255,0.05); 
        border-radius: 3px; 
        margin: 0 15px; 
        overflow: hidden;
    }
    .rank-bar-fill { 
        height: 100%; 
        border-radius: 3px; 
        transition: width 1s cubic-bezier(0.1, 0.7, 1.0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# ---------------- ADS (TOP) ----------------
components.html(
    """
    <div style="display:flex; justify-content:center; margin:10px 0;">
        <script>
          atOptions = {
            'key' : 'b70ce887becced7c033579163064d6b4',
            'format' : 'iframe',
            'height' : 60,
            'width' : 468,
            'params' : {}
          };
        </script>
        <script src="https://www.highperformanceformat.com/b70ce887becced7c033579163064d6b4/invoke.js"></script>
    </div>
    """,
    height=70,
)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("### // TARGET SELECTOR")
    ticker = st.text_input("SYMBOL", "NVDA").upper()
    st.caption("SYSTEM: ONLINE")

# ---------------- DATA ENGINE ----------------

@st.cache_data(ttl=60)
def fetch_global_scan():
    """Fetches global market context indices."""
    symbols = {
        "ES_FUT": "ES=F", "NQ_FUT": "NQ=F", "10Y_YIELD": "^TNX", 
        "VIX": "^VIX", "DXY": "DX-Y.NYB", "OIL": "CL=F", 
        "GOLD": "GC=F", "EURO": "EURUSD=X", "BTC": "BTC-USD", "ETH": "ETH-USD"
    }
    data = {}
    try:
        tickers_list = list(symbols.values())
        df = yf.download(tickers_list, period="5d", interval="1d", progress=False)
        
        # Handle MultiIndex if present
        closes = df['Close'] if 'Close' in df else df
        
        for k, v in symbols.items():
            try:
                if isinstance(closes.columns, pd.MultiIndex):
                     # If multi-index, we need to find the column that matches
                     series = closes[v]
                elif v in closes.columns:
                     series = closes[v]
                else:
                    data[k] = {"price": "N/A", "chg": 0.0}
                    continue

                series = series.dropna()
                if len(series) < 2:
                    data[k] = {"price": "N/A", "chg": 0.0}
                    continue

                curr = series.iloc[-1]
                prev = series.iloc[-2]
                
                # Safety check for scalar values
                if isinstance(curr, pd.Series): curr = curr.iloc[0]
                if isinstance(prev, pd.Series): prev = prev.iloc[0]

                chg = ((curr - prev) / prev) * 100
                fmt = f"{curr:,.0f}" if "BTC" in k or "ETH" in k else f"{curr:,.2f}"
                data[k] = {"price": fmt, "chg": chg}
            except:
                data[k] = {"price": "ERR", "chg": 0.0}
    except:
        data = {k: {"price": "OFFLINE", "chg": 0.0} for k in symbols}
    return data

@st.cache_data(ttl=300)
def get_alpha_ranks():
    """Fetches momentum ranker for key tickers."""
    targets = ["NVDA", "TSLA", "AMD", "META", "AMZN", "MSFT", "GOOGL", "AAPL", "NFLX", "PLTR", "COIN", "MSTR", "SMCI", "AVGO", "COST"]
    try:
        # Fetching 2 days is enough for % change and faster
        df = yf.download(targets, period="5d", interval="1d", progress=False)['Close']
        
        # Flatten MultiIndex if necessary
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(1)
        
        ranks = []
        for t in targets:
            if t in df.columns:
                series = df[t].dropna()
                if len(series) >= 2:
                    curr = series.iloc[-1]
                    prev = series.iloc[-2]
                    chg = ((curr - prev) / prev) * 100
                    # Simple scoring: Magnitude of change
                    ranks.append({"sym": t, "chg": chg, "score": abs(chg)})
        return sorted(ranks, key=lambda x: x['score'], reverse=True)
    except Exception as e:
        return []

# ---------------- HEADER ----------------
c_head_1, c_head_2 = st.columns([3, 1])
with c_head_1:
    st.markdown('<div class="header-title">COMMAND // CENTER</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#8892b0; font-size:14px;">REAL-TIME MARKET SURVEILLANCE & SOCIAL SENTIMENT</div>', unsafe_allow_html=True)

with c_head_2:
    st.markdown(f"""
    <div style="text-align:right; font-family:'JetBrains Mono'; font-size:12px; color:#66fcf1;">
        {datetime.now().strftime('%H:%M:%S UTC')}<br>
        <span style="color:#45a29e;">● SYSTEM OPTIMAL</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---") 

# ---------------- HUD GRID ----------------
scan_data = fetch_global_scan()
hud_html = '<div class="hud-container">'

for k, v in scan_data.items():
    color = "pos" if v['chg'] >= 0 else "neg"
    arrow = "▲" if v['chg'] >= 0 else "▼"
    hud_html += f"""
    <div class="metric-box">
        <div class="metric-label">{k}</div>
        <div class="metric-value">{v['price']}</div>
        <div class="metric-delta {color}">{arrow} {v['chg']:.2f}%</div>
    </div>
    """
hud_html += "</div>"
st.markdown(hud_html, unsafe_allow_html=True)

# ---------------- MAIN DASHBOARD ----------------
col_main, col_side = st.columns([2.2, 1])

# --- LEFT COLUMN: CHART & RANKER ---
with col_main:
    # 1. CHART SECTION
    st.markdown("""
    <div class="glass-card">
        <div class="section-title">ASSET INTELLIGENCE</div>
    """, unsafe_allow_html=True)
    
    html_chart = f"""
    <div class="tradingview-widget-container" style="height:500px;width:100%">
      <div id="tradingview_widget" style="height:100%;width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
      "autosize": true, "symbol": "{ticker}", "interval": "15", "timezone": "Etc/UTC",
      "theme": "dark", "style": "1", "locale": "en", "enable_publishing": false,
      "backgroundColor": "rgba(11, 12, 16, 1)", 
      "gridColor": "rgba(255, 255, 255, 0.05)",
      "hide_top_toolbar": false, 
      "studies": ["RSI@tv-basicstudies"],
      "container_id": "tradingview_widget"
      }});
      </script>
    </div>
    </div>
    """
    components.html(html_chart, height=520)

    # 2. RANKER SECTION
    st.markdown("""
    <div class="glass-card">
        <div class="section-title">MOMENTUM SCANNERS</div>
    """, unsafe_allow_html=True)
    
    ranks = get_alpha_ranks()
    
    if not ranks:
        st.caption("Initializing Scanner...")
    else:
        for i, r in enumerate(ranks[:8]):
            # Cap width at 100%, scale factor 20
            width = min(abs(r['chg']) * 20, 100)
            color = "#45a29e" if r['chg'] > 0 else "#ef476f"
            
            st.markdown(f"""
            <div class="rank-row">
                <div style="width:40px; font-family:'JetBrains Mono'; color:#666;">0{i+1}</div>
                <div style="width:60px; font-weight:700; color:#fff;">{r['sym']}</div>
                <div class="rank-bar-bg">
                    <div class="rank-bar-fill" style="width:{width}%; background:{color}; box-shadow: 0 0 10px {color}40;"></div>
                </div>
                <div style="width:70px; text-align:right; font-family:'JetBrains Mono'; color:{color};">{r['chg']:+.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown("</div>", unsafe_allow_html=True)

# --- RIGHT COLUMN: INTEL FEED ---
with col_side:
    st.markdown("""
    <div class="glass-card">
        <div class="section-title">LIVE WIRE</div>
    """, unsafe_allow_html=True)
    
    # --- FEED LOGIC (TRIPLE REDUNDANCY) ---
    def fetch_yahoo_news(symbol):
        try:
            news = yf.Ticker(symbol).news
            tweets = []
            handles = ["@MarketWire", "@Bloomberg", "@Reuters", "@CNBC", "@WSJ"]
            for i, n in enumerate(news[:10]):
                tweets.append({
                    "user": {"name": handles[i%5], "screen_name": handles[i%5].replace("@","")},
                    "text": n['title'],
                    "source": "News Wire"
                })
            return tweets
        except: return []

    def fetch_stocktwits(symbol):
        url = f"https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json"
        try:
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            if r.status_code == 200:
                data = r.json()
                tweets = []
                for msg in data['messages'][:10]:
                    tweets.append({
                        "user": {"name": msg['user']['username'], "screen_name": msg['user']['username'], "profile_image_url_https": msg['user']['avatar_url']},
                        "text": msg['body'],
                        "source": "Stocktwits"
                    })
                return tweets
            return []
        except: return []

    async def get_feed():
        # A. Try X (Cookies)
        try:
            if os.path.exists("cookies.json"):
                client = Client("en-US")
                with open("cookies.json", "r") as f:
                    raw = json.load(f)
                
                # Robust cookie parsing
                if isinstance(raw, list):
                    cookies = {c['name']: c['value'] for c in raw}
                else:
                    cookies = raw
                
                client.set_cookies(cookies)
                return await client.search_tweet(f"${ticker} filter:verified", "Latest", count=10)
        except: pass
        
        # B. Try Stocktwits
        st_data = fetch_stocktwits(ticker)
        if st_data: return st_data
        
        # C. Try Yahoo
        return fetch_yahoo_news(ticker)

    # EXECUTE FEED
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        feed_data = loop.run_until_complete(get_feed())
        
        for item in feed_data[:8]: 
            # Normalize Data
            if isinstance(item, dict):
                name = item['user']['name']
                handle = item['user']['screen_name']
                text = item['text']
                img = item['user'].get('profile_image_url_https', '')
            else:
                name = item.user.name
                handle = item.user.screen_name
                text = item.text
                img = ""

            avatar = f'<img src="{img}" style="width:32px; height:32px; border-radius:50%;">' if img else '<div style="width:32px; height:32px; background:#333; border-radius:50%;"></div>'

            st.markdown(f"""
            <div class="feed-item">
                <div style="display:flex; align-items:center; margin-bottom:8px;">
                    {avatar}
                    <div style="margin-left:10px; line-height:1.2;">
                        <div style="font-size:13px; font-weight:700; color:#fff;">{name}</div>
                        <div style="font-size:11px; color:#666;">@{handle}</div>
                    </div>
                </div>
                <div style="font-size:13px; color:#ccc; line-height:1.4;">{text}</div>
            </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        st.warning(f"Feed System Error: {e}")

    # VERTICAL AD
    components.html(
        """
        <div style="display:flex; justify-content:center; margin-top:20px;">
            <script>
              atOptions = {
                'key' : '914d023d74077cbb3c33063328e01c7f',
                'format' : 'iframe',
                'height' : 300,
                'width' : 160,
                'params' : {}
              };
            </script>
            <script src="https://www.highperformanceformat.com/914d023d74077cbb3c33063328e01c7f/invoke.js"></script>
        </div>
        """,
        height=320,
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- BOTTOM AD ----------------
components.html(
    """
    <div style="text-align:center;">
        <script async="async" data-cfasync="false" src="https://pl28519010.effectivegatecpm.com/7f2ad764010d514cdee2fdac0b042524/invoke.js"></script>
        <div id="container-7f2ad764010d514cdee2fdac0b042524"></div>
    </div>
    """,
    height=100,
)
