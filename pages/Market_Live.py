import streamlit as st
import streamlit.components.v1 as components

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
