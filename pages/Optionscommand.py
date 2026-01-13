import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 1. LAYOUT & STYLE
st.set_page_config(layout="wide", page_title="OPTIONS_COMMAND_2026")

st.markdown("""
<style>
    [data-testid="stAppViewBlockContainer"] { padding-top: 2rem; max-width: 100% !important; }
    .options-metric-card { 
        background: rgba(0, 255, 65, 0.03); border: 1px solid rgba(0, 255, 65, 0.2); 
        padding: 20px; border-radius: 15px; margin-bottom: 20px;
    }
    .glitch-label { font-family: monospace; color: #00ff41; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)

st.markdown(f"<h1 style='color:#00ff41; font-family:monospace;'>// OPTIONS_COMMAND: {ticker}</h1>", unsafe_allow_html=True)

# 2. SELECT EXPIRATION CYCLE
expirations = stock.options
if expirations:
    selected_date = st.selectbox("SELECT_EXPIRATION_DATE", expirations)
    
    with st.spinner("DECODING_OPTION_CHAIN..."):
        # Fetch the chain for the selected date
        chain = stock.option_chain(selected_date)
        calls = chain.calls
        puts = chain.puts

    # 3. OPEN INTEREST HEATMAP
    # We sort by Open Interest to show the most important "Battleground" strikes first
    top_calls = calls.sort_values("openInterest", ascending=False).head(15)
    top_puts = puts.sort_values("openInterest", ascending=False).head(15)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("<div class='options-metric-card'><span class='glitch-label'>CALL_SIDE_DOMINANCE (OI)</span></div>", unsafe_allow_html=True)
        fig_calls = px.bar(top_calls, x="strike", y="openInterest", 
                           title="TOP_CALL_STRIKES_BY_OPEN_INTEREST",
                           template="plotly_dark", color_discrete_sequence=['#00ff41'])
        st.plotly_chart(fig_calls, use_container_width=True)

    with c2:
        st.markdown("<div class='options-metric-card'><span class='glitch-label'>PUT_SIDE_PROTECTION (OI)</span></div>", unsafe_allow_html=True)
        fig_puts = px.bar(top_puts, x="strike", y="openInterest", 
                          title="TOP_PUT_STRIKES_BY_OPEN_INTEREST",
                          template="plotly_dark", color_discrete_sequence=['#ff4b4b'])
        st.plotly_chart(fig_puts, use_container_width=True)

    # 4. VOLATILITY SKEW & LIQUIDITY TABLE
    st.markdown("### // DEEP_CHAIN_ANALYSIS")
    
    # Combine and add a 'Type' flag for a unified view
    calls['Type'] = 'CALL'
    puts['Type'] = 'PUT'
    combined = pd.concat([calls, puts])
    
    # Sorting by Volume to show where the current action is happening
    liquid_strikes = combined.sort_values("volume", ascending=False).head(20)
    
    st.dataframe(
        liquid_strikes[['Type', 'strike', 'lastPrice', 'change', 'percentChange', 'volume', 'openInterest', 'impliedVolatility']]
        .style.background_gradient(cmap='Greens', subset=['volume', 'openInterest'])
        .format({'impliedVolatility': '{:.2%}', 'percentChange': '{:+.2f}%'}),
        use_container_width=True
    )

    # 5. AI ORACLE INSIGHT
    st.markdown(f"""
    <div style='background:rgba(0, 255, 65, 0.05); padding:20px; border-radius:15px; border-left: 5px solid #00ff41;'>
        <b style='color:#00ff41;'>ORACLE_INSIGHT:</b> Analysis of the {selected_date} chain shows high Open Interest concentration at the 
        <b>${top_calls['strike'].iloc[0]}</b> Call and <b>${top_puts['strike'].iloc[0]}</b> Put levels. These are your primary 
        resistance and support 'magnets' for this expiration cycle.
    </div>
    """, unsafe_allow_html=True)

else:
    st.warning("SIGNAL_LOST: No options data available for this ticker.")
