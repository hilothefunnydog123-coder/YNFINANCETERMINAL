import streamlit as st
import streamlit.components.v1 as components
def apply_majestic_theme():
    st.markdown("""
        <style>
        /* Global Background & Text */
        .stApp { background-color: #0d0d0d; color: #ffffff; }
        
        /* Glassmorphism Metric Cards */
        [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(0, 255, 65, 0.2);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 0 15px rgba(0, 255, 65, 0.05);
        }
        
        /* Neon Glow Titles */
        .terminal-header {
            color: #00ff41;
            text-shadow: 0 0 10px #00ff41;
            font-family: 'Courier New', monospace;
            border-bottom: 2px solid #00ff41;
            padding-bottom: 10px;
        }

        /* Cyberpunk Divider */
        hr { border: 0; height: 1px; background: linear-gradient(to right, #00ff41, transparent); }
        </style>
    """, unsafe_allow_html=True)

apply_majestic_theme()
# 1. SESSION SAFETY
if 'ticker' not in st.session_state:
    st.session_state.ticker = "NVDA"

ticker = st.session_state.ticker

# 2. MAJESTIC HEADER
st.markdown(f"<h1 style='color: #00ff41;'>// LIVE_MARKET_STREAM: {ticker}</h1>", unsafe_allow_html=True)

# 3. TRADINGVIEW WIDGET ENGINE
# We use f-strings to inject the symbol directly into the JS code.
tradingview_html = f"""
<div class="tradingview-widget-container" style="height:600px;width:100%">
  <div id="tradingview_chart" style="height:100%;width:100%"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({{
    "autosize": true,
    "symbol": "{ticker}",
    "interval": "D",
    "timezone": "Etc/UTC",
    "theme": "dark",
    "style": "1",
    "locale": "en",
    "toolbar_bg": "#f1f3f6",
    "enable_publishing": false,
    "hide_side_toolbar": false,
    "allow_symbol_change": true,
    "container_id": "tradingview_chart"
  }});
  </script>
</div>
"""

# 4. RENDER THE COMPONENT
# We set a slightly larger height to avoid the "cut-off" bug common in Streamlit.
components.html(tradingview_html, height=620, scrolling=False)

st.markdown("---")
st.caption("SYSTEM_NOTE: TradingView charts are rendered client-side for zero-latency performance.")
