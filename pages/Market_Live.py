import streamlit as st
import streamlit.components.v1 as components

# 1. Header Hub
st.markdown(f"<h1 style='color:#00ff41; text-shadow:0 0 10px #00ff41;'>// MARKET_LIVE_HUB: {st.session_state.ticker}</h1>", unsafe_allow_html=True)

# 2. TradingView Widget (Category 2 & 3)
# We inject the ticker directly into the JS embed code
tv_chart = f"""
<div class="tradingview-widget-container" style="height:600px;width:100%">
  <div id="tradingview_chart"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({{
    "autosize": true, "symbol": "{st.session_state.ticker}", "interval": "D",
    "timezone": "Etc/UTC", "theme": "dark", "style": "1",
    "locale": "en", "enable_publishing": false, "allow_symbol_change": true,
    "container_id": "tradingview_chart"
  }});
  </script>
</div>
"""
components.html(tv_chart, height=610)

# 3. Inter-market Data (Cat 13 & 14)
st.markdown("### // GLOBAL_CORRELATIONS")
c1, c2, c3 = st.columns(3)
with c1: st.metric("EUR/USD", "1.0842", "-0.0012")
with c2: st.metric("GOLD_FUTURES", "$2,034.10", "+12.40")
with c3: st.metric("CRUDE_OIL", "$78.14", "-1.04")
