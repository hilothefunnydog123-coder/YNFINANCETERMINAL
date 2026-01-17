import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
def inject_stark_ui_v2():
    st.markdown("""
        <style>
        /* 1. STICKY HUD - FORCED TO TOP */
        [data-testid="stHeader"] {
            background: rgba(0,0,0,0.95) !important;
            border-bottom: 2px solid #00ffff !important;
            box-shadow: 0 0 20px #00ffff !important;
        }

        /* 2. THE SECTION CONTAINER (The "Jarvis Frame") */
        .stark-frame {
            position: relative !important;
            border: 1px solid rgba(0, 255, 255, 0.2) !important;
            background: linear-gradient(135deg, rgba(0,255,255,0.05) 0%, transparent 100%) !important;
            padding: 25px !important;
            margin: 20px 0 !important;
            border-radius: 0 20px 0 20px !important;
            overflow: hidden !important;
        }

        /* 3. NEON CORNER BRACKETS */
        .stark-frame::before {
            content: "";
            position: absolute;
            top: 0; left: 0; width: 30px; height: 30px;
            border-top: 4px solid #00ffff; border-left: 4px solid #00ffff;
        }
        .stark-frame::after {
            content: "";
            position: absolute;
            bottom: 0; right: 0; width: 30px; height: 30px;
            border-bottom: 4px solid #00ffff; border-right: 4px solid #00ffff;
        }

        /* 4. TECH-HEADER STYLING */
        .stark-header {
            color: #00ffff !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 1.2rem !important;
            letter-spacing: 6px !important;
            text-transform: uppercase !important;
            text-shadow: 0 0 15px #00ffff !important;
            margin-bottom: 15px !important;
            display: block !important;
        }

        /* 5. SCANNER LINE ANIMATION */
        .scanner {
            width: 100%;
            height: 2px;
            background: linear-gradient(90deg, transparent, #00ffff, transparent);
            position: absolute;
            top: 0; left: 0;
            animation: moveScan 4s infinite linear;
            opacity: 0.5;
        }

        @keyframes moveScan {
            0% { top: 0; }
            100% { top: 100%; }
        }
        </style>
    """, unsafe_allow_html=True)

# Run the injector
inject_stark_ui_v2()
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
