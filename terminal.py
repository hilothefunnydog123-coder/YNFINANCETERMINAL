import streamlit as st
import pandas as pd
import plotly.express as px

# 1. SETUP & PROFESSIONAL THEMING
st.set_page_config(
    page_title="SOVEREIGN_TERMINAL_v46",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed" # Hide sidebar for a sleek landing
)

# Majestic CSS Injection
st.markdown("""
    <style>
    /* Glassmorphism Card Effect */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(5px);
    }
    /* Institutional Glow Text */
    .glow-text {
        color: #00ff41;
        text-shadow: 0 0 10px #00ff41;
        font-family: 'Courier New', monospace;
    }
    /* Smooth Navigation Hover */
    .stButton>button {
        transition: all 0.3s ease;
        border-radius: 20px;
    }
    .stButton>button:hover {
        background-color: #00ff41 !important;
        color: black !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. HEADER & PULSE INDICATOR
c1, c2 = st.columns([3, 1])
with c1:
    st.markdown("<h1 class='glow-text'>// SOVEREIGN_V46_IDENT_CORE</h1>", unsafe_allow_html=True)
    st.caption("ACTIVE_SESSION: SECURE_BRIDGE_STABLE_2026")
with c2:
    st.markdown("""
        <div style="text-align: right; padding-top: 20px;">
            <span style="color: #00ff41; font-size: 10px;">● SYSTEM_ONLINE</span><br>
            <span style="color: #666; font-size: 10px;">LATENCY: 12ms</span>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# 3. MAJESTIC HUB (Category 1 & 20)
# We use st.columns for high-density metrics
m1, m2, m3, m4 = st.columns(4)

# Dynamic Placeholder Data
m1.metric("ACTIVE_SYMBOL", st.session_state.get('ticker', 'NVDA'), delta="T-10")
m2.metric("SIGNAL_STRENGTH", "98.4%", delta="2.1%")
m3.metric("MARKET_SENTIMENT", "BULLISH", delta="NEUTRAL", delta_color="off")
m4.metric("AI_CONFIDENCE", "HIGH", help="Confidence score from Gemini 2.0 Analysis")

# 4. STARTUP-LEVEL NAVIGATION MENU
st.markdown("### // COMMAND_CENTER")
nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

with nav_col1:
    if st.button("📈 MARKET_LIVE", use_container_width=True):
        st.switch_page("pages/Market_Live.py")
with nav_col2:
    if st.button("📊 FINANCIALS", use_container_width=True):
        st.switch_page("pages/Financials.py")
with nav_col3:
    if st.button("📰 MACRO_PULSE", use_container_width=True):
        st.switch_page("pages/Macro_News.py")
with nav_col4:
    if st.button("⚙️ CONFIG", use_container_width=True):
        st.info("System Configuration Locked.")

# 5. VISUAL INTELLIGENCE (Category 1)
# Placing a background diagram for technical context
st.markdown("---")
st.write("Current Global Cycle Placement:")


# Placeholder Chart for Professional Look
df = pd.DataFrame({'Time': range(10), 'Value': [1, 3, 2, 4, 3, 5, 4, 7, 6, 8]})
fig = px.line(df, x='Time', y='Value', template="plotly_dark")
fig.update_traces(line_color='#00ff41', line_width=3)
fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig, use_container_width=True)

st.markdown("<p style='text-align: center; color: #444;'>END_OF_LINE</p>", unsafe_allow_html=True)
