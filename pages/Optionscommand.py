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
</style>
""", unsafe_allow_html=True)

ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)

st.markdown(f"<h1 style='color:#00ff41; font-family:monospace;'>// OPTIONS_COMMAND: {ticker}</h1>", unsafe_allow_html=True)

# 2. SELECT EXPIRATION
expirations = stock.options
if expirations:
    selected_date = st.selectbox("SELECT_EXPIRATION_DATE", expirations)
    
    with st.spinner("DECODING_OPTION_CHAIN..."):
        chain = stock.option_chain(selected_date)
        calls, puts = chain.calls, chain.puts

    # 3. OPEN INTEREST VISUALIZER
    top_calls = calls.sort_values("openInterest", ascending=False).head(15)
    top_puts = puts.sort_values("openInterest", ascending=False).head(15)

    c1, c2 = st.columns(2)
    with c1:
        fig_calls = px.bar(top_calls, x="strike", y="openInterest", title="TOP_CALL_STRIKES",
                           template="plotly_dark", color_discrete_sequence=['#00ff41'])
        st.plotly_chart(fig_calls, use_container_width=True)
    with c2:
        fig_puts = px.bar(top_puts, x="strike", y="openInterest", title="TOP_PUT_STRIKES",
                          template="plotly_dark", color_discrete_sequence=['#ff4b4b'])
        st.plotly_chart(fig_puts, use_container_width=True)

    # 4. THE FIX: STYLING WITHOUT MATPLOTLIB
    st.markdown("### // DEEP_CHAIN_ANALYSIS")
    calls['Type'], puts['Type'] = 'CALL', 'PUT'
    combined = pd.concat([calls, puts])
    liquid_strikes = combined.sort_values("volume", ascending=False).head(20)

    # We use column_config to create bars instead of background gradients
    st.data_editor(
        liquid_strikes[['Type', 'strike', 'lastPrice', 'change', 'percentChange', 'volume', 'openInterest', 'impliedVolatility']],
        column_config={
            "volume": st.column_config.ProgressColumn("VOLUME_FLOW", format="%d", min_value=0, max_value=int(liquid_strikes['volume'].max())),
            "openInterest": st.column_config.ProgressColumn("OPEN_INT", format="%d", min_value=0, max_value=int(liquid_strikes['openInterest'].max())),
            "impliedVolatility": st.column_config.NumberColumn("IV", format="%.2f%%"),
            "percentChange": st.column_config.NumberColumn("CHG%", format="%.2f%%")
        },
        use_container_width=True,
        disabled=True, # Keeps it looking like a dataframe
        hide_index=True
    )

    # 5. ORACLE INSIGHT
    st.info(f"ORACLE_INSIGHT: The {selected_date} chain shows maximum friction at ${top_calls['strike'].iloc[0]} (Calls) and ${top_puts['strike'].iloc[0]} (Puts).")
else:
    st.warning("SIGNAL_LOST: No options found.")
