import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. LAYOUT & STYLE
st.set_page_config(layout="wide", page_title="ANALYST_ORACLE_2026")

st.markdown("""
<style>
    [data-testid="stAppViewBlockContainer"] { padding-top: 2rem; max-width: 100% !important; }
    .estimate-card { background: rgba(0, 255, 65, 0.03); border: 1px solid rgba(0, 255, 65, 0.2); 
                     padding: 25px; border-radius: 20px; text-align: center; }
    .target-val { font-size: 2.5rem; font-weight: 800; color: #00ff41; margin: 10px 0; }
    .upside-label { font-family: monospace; font-size: 1.1rem; color: #888; }
</style>
""", unsafe_allow_html=True)

ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)
info = stock.info

st.markdown(f"<h1 style='color:#00ff41; font-family:monospace;'>// ANALYST_ORACLE: {ticker}</h1>", unsafe_allow_html=True)

# 2. DATA EXTRACTION
# We pull the mean, high, and low targets from the ticker.info dictionary
current_price = info.get('currentPrice', 0)
target_mean = info.get('targetMeanPrice', 0)
target_high = info.get('targetHighPrice', 0)
target_low = info.get('targetLowPrice', 0)
recommendation = info.get('recommendationKey', 'N/A').upper()

# 3. UPSIDE CALCULATION
upside = ((target_mean / current_price) - 1) * 100 if current_price > 0 else 0

# --- VISUALIZATION: THE CONSENSUS GAUGE ---
c1, c2 = st.columns([1, 1])

with c1:
    st.markdown("<div class='estimate-card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='upside-label'>12M_TARGET_CONCENSUS</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='target-val'>${target_mean:,.2f}</div>", unsafe_allow_html=True)
    
    # Delta indicator
    color = "#00ff41" if upside > 0 else "#ff4b4b"
    st.markdown(f"<div style='color:{color}; font-weight:bold; font-size:1.5rem;'>{upside:+.2f}% UPSIDE</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Historical Recommendations Table
    st.markdown("### // RECENT_FIRM_RATINGS")
    recs = stock.recommendations
    if recs is not None and not recs.empty:
        # Show top 10 most recent
        st.dataframe(recs.tail(10).sort_index(ascending=False), use_container_width=True)
    else:
        st.info("DATA_REDACTED: No recent firm ratings available.")

with c2:
    # Target Range Visualizer
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode = "gauge+number",
        value = current_price,
        title = {'text': "PRICE_VS_TARGET_RANGE", 'font': {'color': "#00ff41"}},
        gauge = {
            'axis': {'range': [target_low * 0.9, target_high * 1.1], 'tickcolor': "#00ff41"},
            'bar': {'color': "#00ff41"},
            'bgcolor': "rgba(0,0,0,0)",
            'steps': [
                {'range': [target_low, target_mean], 'color': "rgba(0, 255, 65, 0.1)"},
                {'range': [target_mean, target_high], 'color': "rgba(0, 255, 65, 0.2)"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': target_mean
            }
        }
    ))
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
    
    # Recommendation Summary
    st.markdown(f"""
    <div style='background:rgba(255,255,255,0.05); padding:20px; border-radius:15px; border-left: 5px solid #00ff41;'>
        <h4 style='margin:0; color:#888;'>OFFICIAL_SIGNAL</h4>
        <div style='font-size:2rem; font-weight:bold; color:#fff;'>{recommendation}</div>
        <p style='color:#bbb; margin-top:10px;'> Consensus target reflects an average of institutional forecasts. 
        A rating of <b>{recommendation}</b> indicates the current collective sentiment across major research desks.</p>
    </div>
    """, unsafe_allow_html=True)
