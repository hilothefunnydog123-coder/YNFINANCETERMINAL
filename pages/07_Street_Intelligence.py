import streamlit as st
import yfinance as yf
import pandas as pd

# 1. THE LAYOUT LOCK (CRITICAL: Must be the first Streamlit command)
st.set_page_config(layout="wide", page_title="STREET_INTEL_2026")

# 2. THE GLOBAL WIDTH OVERRIDE
st.markdown("""
<style>
    /* Remove Streamlit's default padding and max-width constraints */
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 1rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 100% !important; 
    }
    
    /* Grid Engine: minmax(350px, 1fr) ensures cards NEVER shrink below 350px */
    .whale-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
        gap: 25px;
        width: 100%;
        margin-top: 20px;
    }
    
    .whale-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 255, 65, 0.2);
        padding: 24px;
        border-radius: 18px;
        backdrop-filter: blur(15px);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    
    .whale-card:hover { 
        border-color: #00ff41; 
        transform: translateY(-5px); 
        background: rgba(0, 255, 65, 0.05);
    }
    
    .inst-name { color: #00ff41; font-size: 1.25rem; font-weight: 800; margin-bottom: 12px; height: 55px; overflow: hidden; line-height: 1.3; }
    .stat-row { display: flex; justify-content: space-between; margin-bottom: 8px; font-family: monospace; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 4px; }
    .label { color: #666; font-size: 0.75rem; text-transform: uppercase; }
    .value { color: #fff; font-size: 0.95rem; font-weight: 600; }
    
    .bar-bg { background: rgba(255,255,255,0.1); height: 8px; border-radius: 4px; margin-top: 15px; }
    .bar-fill { background: #00ff41; height: 100%; border-radius: 4px; box-shadow: 0 0 12px #00ff41; }
</style>
""", unsafe_allow_html=True)

ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)

def render_whale_cards(df, title):
    st.markdown(f"<h2 style='color:#00ff41; padding-left: 5px; border-left: 4px solid #00ff41;'> &nbsp; // {title}</h2>", unsafe_allow_html=True)
    if df is not None and not df.empty:
        # Dynamic Mapping for 2026 yfinance structures
        df = df.rename(columns={"Holder": "H", "Shares": "S", "% Out": "P", "Value": "V", "pctHeld": "P", "Position": "S"})
        
        html = "<div class='whale-grid'>"
        for _, row in df.iterrows():
            name = row.get('H', 'N/A')
            shares = f"{int(row.get('S', 0)):,}" if row.get('S') else "0"
            value = f"${int(row.get('V', 0)):,}" if row.get('V') else "$0"
            
            # Smart Percentage Logic: Handles both 0.09 and 9.0 formats
            raw_p = row.get('P', 0)
            percent = (raw_p * 100) if raw_p < 1 else raw_p
            
            html += f"""
            <div class='whale-card'>
                <div class='inst-name'>{name}</div>
                <div class='stat-row'><span class='label'>SHARES</span><span class='value'>{shares}</span></div>
                <div class='stat-row'><span class='label'>VALUATION</span><span class='value'>{value}</span></div>
                <div class='stat-row'><span class='label'>STAKE</span><span class='value'>{percent:.2f}%</span></div>
                <div class='bar-bg'><div class='bar-fill' style='width: {min(percent * 8, 100)}%;'></div></div>
            </div>
            """
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.info("SIGNAL_OFFLINE: No institutional data detected.")

# FINAL EXECUTION
render_whale_cards(stock.institutional_holders, "INSTITUTIONAL_WHALES")
render_whale_cards(stock.mutualfund_holders, "MUTUAL_FUND_EXPOSURE")
