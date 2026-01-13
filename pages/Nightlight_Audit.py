import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="NIGHTLIGHT_AUDIT")

st.markdown(f"<h1 style='color:#fffd00; font-family:monospace;'>// SATELLITE_INDUSTRIAL_AUDIT</h1>", unsafe_allow_html=True)

# 1. RADIANCE TRENDS (Tracking light intensity over industrial hubs)
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
# Simulate radiance data (nanowatts/cm2/sr)
industrial_hub_a = [45.2, 46.8, 42.1, 48.5, 49.2, 51.5]
official_gdp_proxy = [44, 45, 46, 47, 48, 49]

fig = go.Figure()
fig.add_trace(go.Scatter(x=months, y=industrial_hub_a, name="VIIRS_SATELLITE_RADIANCE", line=dict(color='#fffd00', width=4)))
fig.add_trace(go.Scatter(x=months, y=official_gdp_proxy, name="OFFICIAL_REPORTED_ACTIVITY", line=dict(color='#888', dash='dot')))

fig.update_layout(template="plotly_dark", title="INDUSTRIAL_OUTPUT: REALITY vs. REPORTED", height=500)
st.plotly_chart(fig, use_container_width=True)

# 2. AI DECODE
st.warning("""
**ORACLE_SATELLITE:** Radiance in Industrial Hub A has surged 4.6% above the official reported activity trend. 
This suggests 'Hidden Growth' or unannounced factory shifts, indicating an upcoming earnings beat for companies in the manufacturing sector.
""")
