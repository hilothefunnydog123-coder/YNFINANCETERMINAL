import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="MONTE_CARLO_SIM")

st.markdown("""
<style>
    .sim-card { 
        background: linear-gradient(135deg, rgba(0,240,255,0.1) 0%, rgba(0,255,65,0.1) 100%);
        border: 1px solid #00f0ff; padding: 20px; border-radius: 20px;
    }
    .sim-stat { font-family: monospace; font-size: 28px; color: #00ff41; }
</style>
""", unsafe_allow_html=True)

ticker = st.session_state.get('ticker', 'NVDA')
df = yf.Ticker(ticker).history(period="1y")

st.markdown(f"<h1 style='color:#00f0ff; font-family:monospace;'>// MONTE_CARLO_PROJECTION: {ticker}</h1>", unsafe_allow_html=True)

# 1. MONTE CARLO MATH
returns = df['Close'].pct_change()
last_price = df['Close'].iloc[-1]
volatility = returns.std()
days = 252 # 1 Trading Year
simulations = 50 # Number of paths

# Create price paths
sim_df = pd.DataFrame()
for i in range(simulations):
    daily_returns = np.random.normal(returns.mean(), volatility, days)
    price_path = last_price * (1 + daily_returns).cumprod()
    sim_df[i] = price_path

# 2. THE VISUALIZER
fig = go.Figure()
for i in range(simulations):
    fig.add_trace(go.Scatter(y=sim_df[i], mode='lines', 
                             line=dict(width=1), 
                             opacity=0.3, 
                             showlegend=False,
                             hoverinfo='none'))

# Add the Median Path (Bold)
fig.add_trace(go.Scatter(y=sim_df.median(axis=1), mode='lines', 
                         line=dict(color='#00ff41', width=4), 
                         name='MEDIAN_EXPECTATION'))

fig.update_layout(template="plotly_dark", height=600, 
                  xaxis_title="TRADING_DAYS_OUT", yaxis_title="PROJECTED_PRICE",
                  margin=dict(l=0,r=0,t=0,b=0))

st.plotly_chart(fig, use_container_width=True)

# 3. STATISTICAL OUTCOMES
c1, c2 = st.columns(2)
with c1:
    st.markdown("<div class='sim-card'>", unsafe_allow_html=True)
    st.write("BULL_CASE (90th Percentile)")
    st.markdown(f"<div class='sim-stat'>${sim_df.iloc[-1].quantile(0.90):.2f}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='sim-card'>", unsafe_allow_html=True)
    st.write("BEAR_CASE (10th Percentile)")
    st.markdown(f"<div class='sim-stat' style='color:#ff4b4b;'>${sim_df.iloc[-1].quantile(0.10):.2f}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
