import streamlit as st
import yfinance as yf

# 1. GLOBAL TERMINAL STYLING
st.markdown("""
<style>
    .reportview-container { background: #0d0d0d; }
    /* Majestic Glass Card */
    .data-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 255, 65, 0.2);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.1);
    }
    .card-header {
        color: #00f0ff;
        font-family: 'Courier New', monospace;
        letter-spacing: 2px;
        font-weight: bold;
        margin-bottom: 15px;
        border-bottom: 1px solid #333;
    }
    .data-label { color: #888; font-size: 12px; text-transform: uppercase; }
    .data-value { color: #ffffff; font-size: 18px; font-family: 'Courier New', monospace; font-weight: bold; }
    .glow-green { color: #00ff41; text-shadow: 0 0 10px #00ff41; }
</style>
""", unsafe_allow_html=True)

# 2. DATA INITIALIZATION
ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)
info = stock.info

st.markdown(f"<h1 class='glow-green'>// FINANCIAL_INTELLIGENCE_MTX: {ticker}</h1>", unsafe_allow_html=True)

# --- HUB 1: ANALYST FORECASTS & ESTIMATES (Category 7) ---
st.markdown("<div class='data-card'>", unsafe_allow_html=True)
st.markdown("<div class='card-header'>// ANALYST_TARGETS_v46</div>", unsafe_allow_html=True)
f1, f2, f3, f4 = st.columns(4)

target = info.get('targetMedianPrice', 0)
current = info.get('currentPrice', 1)
upside = ((target / current) - 1) * 100 if target else 0

with f1: st.metric("EST_VALUE", f"${target}", delta=f"{upside:.2f}%")
with f2: st.metric("CONSENSUS", info.get('recommendationKey', 'N/A').upper())
with f3: st.metric("ANALYST_COUNT", info.get('numberOfAnalystOpinions', '0'))
with f4: st.metric("PE_RATIO", f"{info.get('trailingPE', 0):.2f}")
st.markdown("</div>", unsafe_allow_html=True)

# --- HUB 2: CORE MATRICES (Category 5 & 6) ---
st.markdown("<p class='stat-header'>// FINANCIAL_BENTO_GRID</p>", unsafe_allow_html=True)

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("<div class='data-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-header'>INCOME_DYNAMICS</div>", unsafe_allow_html=True)
    # Mapping your specific list points
    st.markdown(f"<span class='data-label'>Total Revenue</span><br><span class='data-value'>${info.get('totalRevenue', 0):,}</span>", unsafe_allow_html=True)
    st.markdown(f"<p><span class='data-label'>Gross Profit</span><br><span class='data-value'>${info.get('grossProfits', 0):,}</span></p>", unsafe_allow_html=True)
    st.markdown(f"<p><span class='data-label'>EBITDA</span><br><span class='data-value'>${info.get('ebitda', 0):,}</span></p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_b:
    st.markdown("<div class='data-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-header'>BALANCE_STRENGTH</div>", unsafe_allow_html=True)
    st.markdown(f"<span class='data-label'>Cash on Hand</span><br><span class='data-value'>${info.get('totalCash', 0):,}</span>", unsafe_allow_html=True)
    st.markdown(f"<p><span class='data-label'>Total Debt</span><br><span class='data-value'>${info.get('totalDebt', 0):,}</span></p>", unsafe_allow_html=True)
    st.markdown(f"<p><span class='data-label'>Quick Ratio</span><br><span class='data-value'>{info.get('quickRatio', 'N/A')}</span></p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- HUB 3: OWNERSHIP & FLOW (Category 8) ---
st.markdown("<div class='data-card'>", unsafe_allow_html=True)
st.markdown("<div class='card-header'>OWNERSHIP_STRUCTURE</div>", unsafe_allow_html=True)
o1, o2, o3 = st.columns(3)
o1.write(f"**Institutional:** {info.get('heldPercentInstitutions', 0)*100:.2f}%")
o2.write(f"**Insiders:** {info.get('heldPercentInsiders', 0)*100:.2f}%")
o3.write(f"**Short % Float:** {info.get('shortPercentOfFloat', 0)*100:.2f}%")
st.markdown("</div>", unsafe_allow_html=True)
