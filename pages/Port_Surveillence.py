import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="PORT_SURVEILLANCE_2026")

# CYBER-MARITIME UI
st.markdown("""
<style>
    .port-stat-card {
        background: rgba(0, 240, 255, 0.05);
        border-left: 5px solid #00f0ff;
        padding: 20px; border-radius: 10px; margin-bottom: 20px;
    }
    .glitch-blue { color: #00f0ff; font-family: monospace; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

ticker = st.session_state.get('ticker', 'NVDA')
st.markdown(f"<h1 class='glitch-blue'>// PORT_SURVEILLANCE: GLOBAL_LOGISTICS_FLOW</h1>", unsafe_allow_html=True)

# 1. AIS DATA SIMULATION (In production, use MarineTraffic or Datalastic API)
# Moored: Unloading | Anchored: Waiting
port_data = {
    'Port': ['Shanghai', 'Long Beach', 'Rotterdam', 'Singapore'],
    'Moored': [450, 120, 210, 380],
    'Anchored': [15, 38, 5, 12]
}
df_ports = pd.DataFrame(port_data)
df_ports['Congestion_Index'] = (df_ports['Anchored'] / df_ports['Moored']) * 100

# 2. THE CONGESTION MONITOR
c1, c2 = st.columns([2, 1])

with c1:
    fig = px.bar(df_ports, x='Port', y='Congestion_Index', 
                 title="PORT_CONGESTION_SKEW (%)",
                 template="plotly_dark", color='Congestion_Index',
                 color_continuous_scale='Bluered')
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.markdown("<div class='port-stat-card'>", unsafe_allow_html=True)
    st.markdown("### // SUPPLY_CHAIN_ALERT")
    lb_congestion = df_ports.loc[df_ports['Port'] == 'Long Beach', 'Congestion_Index'].values[0]
    if lb_congestion > 15:
        st.error(f"CRITICAL: Long Beach Congestion at {lb_congestion:.1f}%. High risk for US retail imports.")
    else:
        st.success("STABLE: Global maritime flow operating within nominal ranges.")
    st.markdown("</div>", unsafe_allow_html=True)
