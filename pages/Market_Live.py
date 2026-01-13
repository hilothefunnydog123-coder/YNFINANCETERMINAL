import streamlit as st
import streamlit.components.v1 as components
def inject_terminal_css():
    st.markdown("""
        <style>
        /* Main Background */
        .stApp { background-color: #050505; color: #e0e0e0; }
        
        /* Majestic Glass Card */
        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(0, 255, 65, 0.2);
            padding: 15px; border-radius: 10px;
            backdrop-filter: blur(10px);
            box-shadow: 0 0 15px rgba(0, 255, 65, 0.05);
        }
        
        /* Techy Typography */
        h1, h2, h3 { font-family: 'Courier New', monospace; color: #00ff41 !important; text-shadow: 0 0 8px #00ff41; }
        .stTabs [data-baseweb="tab-list"] { gap: 10px; }
        .stTabs [data-baseweb="tab"] {
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 5px 5px 0 0; padding: 10px 20px; color: #888;
        }
        .stTabs [aria-selected="true"] { background-color: rgba(0, 255, 65, 0.1) !important; color: #00ff41 !important; border-bottom: 2px solid #00ff41 !important; }
        </style>
    """, unsafe_allow_html=True)

# Essential for all pages
if 'ticker' not in st.session_state:
    st.session_state.ticker = "NVDA"

st.markdown(f"<h1 style='color: #00ff41;'>// MARKET_LIVE: {st.session_state.ticker}</h1>", unsafe_allow_html=True)

# THE TRADINGVIEW FULL-SCREEN WIDGET
tv_chart_html = f"""
<div class="tradingview-widget-container" style="height:800px; width:100%;">
  <div id="tradingview_full" style="height:100%; width:100%;"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({{
    "autosize": true,
    "symbol": "{st.session_state.ticker}",
    "interval": "D",
    "timezone": "Etc/UTC",
    "theme": "dark",
    "style": "1",
    "locale": "en",
    "enable_publishing": false,
    "hide_side_toolbar": false,
    "allow_symbol_change": true,
    "container_id": "tradingview_full"
  }});
  </script>
</div>
"""

# Rendering with a large height to prevent "cutting off"
components.html(tv_chart_html, height=800)
