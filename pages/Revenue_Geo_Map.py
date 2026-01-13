import streamlit as st
import yfinance as yf
import plotly.express as px
import pandas as pd

st.set_page_config(layout="wide", page_title="GEO_REVENUE_2026")

# CYBERPUNK MAP STYLE
st.markdown("""
<style>
    [data-testid="stAppViewBlockContainer"] { padding-top: 1rem; background-color: #050505; }
    .geo-header { color: #00f0ff; font-family: 'Orbitron', sans-serif; letter-spacing: 2px; }
</style>
""", unsafe_allow_html=True)

ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)

st.markdown(f"<h1 class='geo-header'>// GLOBAL_EXPOSURE_MAP: {ticker}</h1>", unsafe_allow_html=True)

# 2. GEO-REVENUE SIMULATION (Mapping corporate footprint)
# In a production environment, this would pull from SEC Segment Reporting
data = {
    'Region': ['USA', 'China', 'Taiwan', 'Germany', 'Japan', 'Other'],
    'Revenue_Share': [45, 25, 15, 7, 5, 3] # Example weights for a Tech Giant
}
df_geo = pd.DataFrame(data)

# 3. THE MAP VISUAL
fig = px.choropleth(df_geo, 
                    locations="Region", 
                    locationmode='country names',
                    color="Revenue_Share",
                    hover_name="Region",
                    color_continuous_scale="Viridis",
                    template="plotly_dark")

fig.update_layout(
    geo=dict(showframe=False, showcoastlines=True, projection_type='equirectangular', bgcolor='rgba(0,0,0,0)'),
    margin=dict(l=0, r=0, t=0, b=0),
    height=600,
    coloraxis_showscale=False
)

st.plotly_chart(fig, use_container_width=True)

st.info(f"**STRATEGIC_INTEL:** {ticker} shows high concentration in the APAC region. Monitor USD/CNY exchange rates and South China Sea trade stability for supply chain risk.")
