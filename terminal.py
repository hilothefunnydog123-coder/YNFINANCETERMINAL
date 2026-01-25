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
        padding-top: 2rem; 
        padding-bottom: 5rem; 
        max-width: 95rem;
    }
    
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
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
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
    .metric-label { font-size: 11px; color: #8892b0; font-weight: 600; text-transform: uppercase; }
    .metric-value { font-family: 'JetBrains Mono', monospace; font-size: 18px; color: #fff; margin-top: 4px; }
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
    .rank-bar-bg { flex-grow: 1; height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; margin: 0 15px; }
    .rank-bar-fill { height: 100%; border-radius: 2px; position: relative; }
    
</style>
""", unsafe_allow_html=True)

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

# ---------------- HUD GRID (REFACTORED) ----------------
# We construct a single HTML block for the top metrics to ensure perfect grid alignment
# instead of using st.columns which can get messy.

scan_data = fetch_global_scan() # Ensure this function from your original code is active
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

# ---------------- MAIN LAYOUT ----------------
col_main, col_side = st.columns([2.2, 1])

# --- LEFT: CHART & RANKER ---
with col_main:
    # CHART SECTION
    st.markdown("""
    <div class="glass-card">
        <div class="section-title">ASSET INTELLIGENCE</div>
    """, unsafe_allow_html=True)
    
    # Note: Updated background color in widget to match theme
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

    # RANKER SECTION
    st.markdown("""
    <div class="glass-card">
        <div class="section-title">MOMENTUM SCANNERS</div>
    """, unsafe_allow_html=True)
    
    ranks = get_alpha_ranks() # Ensure this function is active
    
    for i, r in enumerate(ranks[:8]):
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

# --- RIGHT: FEED ---
with col_side:
    st.markdown("""
    <div class="glass-card">
        <div class="section-title">LIVE WIRE</div>
    """, unsafe_allow_html=True)
    
    # We use a container height to make it scrollable if needed, or just list them
    # Reuse your existing async feed logic here
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        feed_data = loop.run_until_complete(get_feed())
        
        for item in feed_data[:8]: # Limit to 8 items for clean UI
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
        st.warning("Feed Offline")
        
    st.markdown("</div>", unsafe_allow_html=True)
