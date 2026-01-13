import streamlit as st
import yfinance as yf
import pandas as pd

# 1. STYLE ENGINE
def apply_market_style():
    st.markdown("""
        <style>
        .market-card {
            background: rgba(0, 255, 65, 0.05);
            border: 1px solid rgba(0, 255, 65, 0.2);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        .ticker-label { color: #00f0ff; font-size: 10px; font-weight: bold; }
        .price-label { color: #ffffff; font-size: 18px; font-family: 'Courier New', monospace; }
        </style>
    """, unsafe_allow_html=True)

apply_market_style()

# 2. DATA REGISTRY (Categories 13 & 14)
# Using standard Yahoo Finance tickers for futures and spot rates
FX_TICKERS = {"EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X", "USD/CAD": "CAD=X"}
COMM_TICKERS = {"Gold": "GC=F", "Crude Oil": "CL=F", "Natural Gas": "NG=F", "Silver": "SI=F"}

@st.cache_data(ttl=300)
def fetch_global_assets(ticker_map):
    results = {}
    for name, ticker in ticker_map.items():
        try:
            data = yf.Ticker(ticker).history(period="1d")
            if not data.empty:
                last_price = data['Close'].iloc[-1]
                prev_price = data['Open'].iloc[-1]
                pct_change = ((last_price - prev_price) / prev_price) * 100
                results[name] = {"price": last_price, "change": pct_change}
        except:
            results[name] = {"price": 0, "change": 0}
    return results

# 3. RENDER WORKSPACE
st.markdown("<h1 style='color: #00ff41; border-bottom: 2px solid #00ff41;'>// GLOBAL_MARKET_PULSE</h1>", unsafe_allow_html=True)

col_fx, col_comm = st.columns(2)

# --- CATEGORY 13: FX DATA ---
with col_fx:
    st.markdown("### 💱 FX_SPOT_RATES")
    fx_data = fetch_global_assets(FX_TICKERS)
    for name, vals in fx_data.items():
        color = "#00ff41" if vals['change'] >= 0 else "#ff4b4b"
        st.markdown(f"""
            <div class="market-card">
                <span class="ticker-label">{name}</span><br>
                <span class="price-label">{vals['price']:.4f}</span>
                <span style="color: {color}; font-size: 12px; margin-left: 10px;">{vals['change']:+.2f}%</span>
            </div>
        """, unsafe_allow_html=True)

# --- CATEGORY 14: COMMODITIES DATA ---
with col_comm:
    st.markdown("### 🛢️ COMMODITY_FUTURES")
    comm_data = fetch_global_assets(COMM_TICKERS)
    for name, vals in comm_data.items():
        color = "#00ff41" if vals['change'] >= 0 else "#ff4b4b"
        st.markdown(f"""
            <div class="market-card">
                <span class="ticker-label">{name.upper()}</span><br>
                <span class="price-label">${vals['price']:.2f}</span>
                <span style="color: {color}; font-size: 12px; margin-left: 10px;">{vals['change']:+.2f}%</span>
            </div>
        """, unsafe_allow_html=True)

st.markdown("---")
# Insert the TradingView chart here...
