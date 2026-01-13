import streamlit as st
import yfinance as yf
import pandas as pd

# 1. THE LAYOUT LOCK (Must be at the very top)
st.set_page_config(layout="wide", page_title="STREET_INTEL_2026")

# 2. THE ANTI-SQUISH CSS
st.markdown("""
<style>
    /* Force container to use maximum width */
    .block-container { padding-top: 1rem; max-width: 95% !important; }
    
    .whale-grid {
        display: grid;
        /* repeat(auto-fill, minmax(350px, 1fr)) is the key: it forces a minimum width */
        grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
        gap: 25px;
        width: 100%;
        margin-top: 20px;
    }
    .whale-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 255, 65, 0.2);
        padding: 22px;
        border-radius: 18px;
        backdrop-filter: blur(12px);
        transition: transform 0.3s ease;
    }
    .whale-card:hover { border-color: #00ff41; transform: translateY(-5px); }
    .inst-name { color: #00ff41; font-size: 1.3rem; font-weight: 800; margin-bottom: 12px; height: 50px; overflow: hidden; }
    .stat-row { display: flex; justify-content: space-between; margin-bottom: 6px; font-family: monospace; }
    .label { color: #666; font-size: 0.8rem; }
    .value { color: #fff; font-size: 0.95rem; }
    
    /* Progress Bar logic */
    .bar-bg { background: rgba(255,255,255,0.05); height: 8px; border-radius: 4px; margin-top: 15px; }
    .bar-fill { background: #00ff41; height: 100%; border-radius: 4px; box-shadow: 0 0 10px #00ff41; }
</style>
""", unsafe_allow_html=True)

ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)

def render_whale_cards(df, title):
    st.markdown(f"<h2 style='color:#00ff41;'>// {title}</h2>", unsafe_allow_html=True)
    if df is not None and not df.empty:
        # Dynamic Data Sanitization
        df = df.rename(columns={"Holder": "H", "Shares": "S", "% Out": "P", "Value": "V", "pctHeld": "P"})
        
        html = "<div class='whale-grid'>"
        for _, row in df.iterrows():
            name = row.get('H', 'N/A')
            shares = f"{row.get('S', 0):,}"
            value = f"${row.get('V', 0):,}"
            
            # 2026 Percentage Fix: Decimal vs Whole Number detection
            raw_p = row.get('P', 0)
            percent = (raw_p * 100) if raw_p < 1 else raw_p
            
            html += f"""
            <div class='whale-card'>
                <div class='inst-name'>{name}</div>
                <div class='stat-row'><span class='label'>POSITION</span><span class='value'>{shares}</span></div>
                <div class='stat-row'><span class='label'>MARKET_VAL</span><span class='value'>{value}</span></div>
                <div class='stat-row'><span class='label'>OWNERSHIP</span><span class='value'>{percent:.2f}%</span></div>
                <div class='bar-bg'><div class='bar-fill' style='width: {min(percent * 8, 100)}%;'></div></div>
            </div>
            """
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.info("DATA_REDACTED: No signals found.")

# RENDER COMMANDS
render_whale_cards(stock.institutional_holders, "INSTITUTIONAL_WHALES")
render_whale_cards(stock.mutualfund_holders, "MUTUAL_FUND_EXPOSURE")
