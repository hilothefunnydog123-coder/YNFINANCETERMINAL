import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 1. STYLE INJECTION
st.markdown("""
<style>
    .whales-card { background: rgba(0, 255, 65, 0.05); border-radius: 15px; padding: 20px; border: 1px solid #00ff41; }
    .comp-table { border-collapse: collapse; width: 100%; color: #fff; }
    .glow-text { color: #00ff41; text-shadow: 0 0 10px #00ff41; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)

st.markdown(f"<h1 class='glow-text'>// STREET_INTELLIGENCE: {ticker}</h1>", unsafe_allow_html=True)

# 2. SECTION 07: THE WHALES (Institutional Holders)
st.markdown("### // INSTITUTIONAL_LATTICE")
inst_holders = stock.institutional_holders

if inst_holders is not None and not inst_holders.empty:
    # Clean up column names for the "Majestic" look
    inst_holders.columns = ["HOLDER", "SHARES", "DATE_REPORTED", "OWNERSHIP_%", "VALUE"]
    st.dataframe(inst_holders.style.background_gradient(cmap='Greens', subset=['OWNERSHIP_%']), use_container_width=True)
else:
    st.warning("OFF-BOOK: No institutional data detected for this signal.")

# 3. SECTION 11: COMPETITOR LATTICE (Peer Valuation)
st.markdown("### // RELATIVE_VALUATION_MATRIX")
# We'll compare the Ticker against its sector peers
sector = stock.info.get('sector', 'Technology')
peers = ["NVDA", "AMD", "INTC", "TSM"] # You can automate this list later

peer_data = []
for p in peers:
    try:
        p_info = yf.Ticker(p).info
        peer_data.append({
            "TICKER": p,
            "P/E_RATIO": p_info.get('trailingPE', 0),
            "EV/EBITDA": p_info.get('enterpriseToEbitda', 0),
            "MARGIN": p_info.get('profitMargins', 0) * 100
        })
    except: continue

if peer_data:
    df_peers = pd.DataFrame(peer_data)
    c1, c2 = st.columns([1, 1])
    
    with c1:
        fig = px.bar(df_peers, x='TICKER', y='P/E_RATIO', title="P/E_MULTIPLES", template="plotly_dark", color_discrete_sequence=['#00ff41'])
        st.plotly_chart(fig, use_container_width=True)
    
    with c2:
        st.markdown("<div class='whales-card'>", unsafe_allow_html=True)
        st.markdown("**ORACLE_DECODE:**")
        st.write(f"In the {sector} sector, {ticker} is trading at a {'premium' if df_peers['P/E_RATIO'].iloc[0] > df_peers['P/E_RATIO'].mean() else 'discount'} compared to its peers.")
        st.markdown("</div>", unsafe_allow_html=True)
