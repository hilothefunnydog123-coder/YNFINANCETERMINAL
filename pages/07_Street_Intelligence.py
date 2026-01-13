import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 1. MAJESTIC TERMINAL STYLING
st.set_page_config(layout="wide", page_title="STREET_INTEL_v2026")
st.markdown("""
<style>
    .section-card {
        background: rgba(0, 255, 65, 0.02);
        border: 1px solid rgba(0, 255, 65, 0.2);
        padding: 25px; border-radius: 20px;
        margin-bottom: 30px;
    }
    .glow-header { color: #00ff41; text-shadow: 0 0 10px #00ff41; letter-spacing: 2px; }
    .whale-label { color: #888; font-family: monospace; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)

st.markdown(f" <h1 class='glow-header'>// STREET_INTELLIGENCE: {ticker}</h1>", unsafe_allow_html=True)

# 2. THE WHALE TRACKER (Defensive Logic)
def render_holder_matrix(df, title):
    st.markdown(f"### // {title}")
    if df is not None and not df.empty:
        # 2026 Defensive Column Mapping
        mapping = {
            "Holder": "INSTITUTION", "Shares": "POSITION", 
            "Date Reported": "AS_OF", "% Out": "OWNERSHIP_%", "Value": "MARKET_VAL"
        }
        df = df.rename(columns=mapping)
        
        # Format percentages if they exist
        pct_col = next((c for c in df.columns if "OWNERSHIP" in c or "%" in c), None)
        if pct_col:
            st.dataframe(df.style.background_gradient(cmap='Greens', subset=[pct_col]), use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)
    else:
        st.info(f"SIGNAL_OFFLINE: {title} data redacted by provider.")

c1, c2 = st.columns(2)
with c1:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    render_holder_matrix(stock.institutional_holders, "INSTITUTIONAL_WHALES")
    st.markdown("</div>", unsafe_allow_html=True)
with c2:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    render_holder_matrix(stock.mutualfund_holders, "MUTUAL_FUND_EXPOSURE")
    st.markdown("</div>", unsafe_allow_html=True)

# 3. COMPETITOR LATTICE (Relative Valuation)
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.markdown("### // RELATIVE_VALUATION_LATTICE")

# Dynamic Peer Discovery
sector = stock.info.get('sector', 'Technology')
# 2026 Manual Peer Fallback (Real-time sector scraping is slow, so we use a curated set)
peers = ["NVDA", "AMD", "INTC", "TSM", "AVGO"] if "Semiconductor" in stock.info.get('industry', '') else [ticker, "AAPL", "MSFT", "GOOGL"]

peer_stats = []
with st.spinner("DECODING_PEER_SIGNALS..."):
    for p in peers:
        try:
            p_tick = yf.Ticker(p).info
            peer_stats.append({
                "TICKER": p,
                "P/E": p_tick.get('trailingPE', 0),
                "EV/EBITDA": p_tick.get('enterpriseToEbitda', 0),
                "MAR_PROFIT": p_tick.get('profitMargins', 0) * 100,
                "REV_GROWTH": p_tick.get('revenueGrowth', 0) * 100
            })
        except: continue

if peer_stats:
    comp_df = pd.DataFrame(peer_stats)
    
    col_a, col_b = st.columns([2, 1])
    with col_a:
        # P/E vs Growth Comparison
        fig = px.scatter(comp_df, x="P/E", y="REV_GROWTH", text="TICKER", 
                         size="MAR_PROFIT", color="TICKER",
                         title="PE_RATIO vs REVENUE_GROWTH (Size = Profit Margin)",
                         template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_traces(textposition='top center')
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        st.markdown("<br><br>", unsafe_allow_html=True)
        avg_pe = comp_df['P/E'].mean()
        curr_pe = comp_df[comp_df['TICKER'] == ticker]['P/E'].values[0]
        diff = ((curr_pe / avg_pe) - 1) * 100
        
        st.metric("SECTOR_AVG_P/E", f"{avg_pe:.2f}")
        st.metric("VALUATION_DELTA", f"{diff:.1f}%", delta=f"{diff:.1f}%", delta_color="inverse")
        st.markdown(f"<p class='whale-label'>DECODE: {ticker} is trading at a {abs(diff):.1f}% {'premium' if diff > 0 else 'discount'} to the peer average.</p>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
