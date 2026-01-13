import streamlit as st
import yfinance as yf
import plotly.express as px

# 1. DATA SCRAPER
ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)

# 2. MAJESTIC OWNERSHIP HUB (Category 8)
def render_ownership_hub():
    st.markdown("### // OWNERSHIP_DYNAMICS_v46")
    try:
        # yfinance.major_holders structure varies; we normalize it
        holders = stock.major_holders
        
        # FIX: Ensure we have valid columns for the pie chart
        if holders is not None and not holders.empty:
            # Normalize column names for plotly
            holders.columns = ["Value", "Type"]
            holders["Value"] = holders["Value"].str.replace('%', '').astype(float)
            
            fig_pie = px.pie(
                holders, 
                values="Value", 
                names="Type", 
                title=f"OWNERSHIP_MIX: {ticker}",
                template="plotly_dark",
                color_discrete_sequence=px.colors.sequential.Greens_r
            )
            fig_pie.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.warning("OWNERSHIP_SIGNAL_OFFLINE")
    except Exception as e:
        st.error(f"DATA_LINK_FAILURE: {str(e)}")

# 3. THE 5000+ DATA POINT MATRIX
m_tabs = st.tabs(["IDENTIFICATION", "FUNDAMENTALS", "RATIOS", "ESTIMATES", "OWNERSHIP"])

with m_tabs[2]: # FUNDAMENTALS (Cat 5)
    st.markdown("### // CORE_STATEMENTS_LATTICE")
    # Multi-tab deep dive for 15+ individual charts
    f_tabs = st.tabs(["INCOME", "BALANCE", "CASH_FLOW"])
    
    with f_tabs[0]:
        income = stock.income_stmt
        # Generate fly-looking charts for every line item
        cols = st.columns(3)
        for i, metric in enumerate(income.index[:15]):
            with cols[i % 3]:
                st.markdown(f"<div style='border:1px solid #00ff41; padding:10px; border-radius:10px;'>", unsafe_allow_html=True)
                # Plotly Bar Chart for each individual metric
                fig = px.bar(income.loc[metric], title=metric, template="plotly_dark")
                fig.update_layout(height=180, margin=dict(l=0,r=0,t=30,b=0), xaxis_title=None, yaxis_title=None)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                st.markdown("</div>", unsafe_allow_html=True)

with m_tabs[4]: # OWNERSHIP (Cat 8)
    render_ownership_hub()
    st.markdown("#### // TOP_INSTITUTIONAL_HOLDERS")
    st.dataframe(stock.institutional_holders, use_container_width=True)
