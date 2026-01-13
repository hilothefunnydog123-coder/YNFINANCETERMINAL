import streamlit as st
import streamlit.components.v1 as components

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
