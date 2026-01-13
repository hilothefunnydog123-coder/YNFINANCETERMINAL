import streamlit as st
import yfinance as yf
import pandas as pd

# 1. MAJESTIC CARD STYLING
st.markdown("""
<style>
    .whale-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 20px;
        padding: 20px 0;
    }
    .whale-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 255, 65, 0.2);
        border-radius: 15px;
        padding: 20px;
        transition: 0.3s;
        backdrop-filter: blur(10px);
    }
    .whale-card:hover {
        border-color: #00ff41;
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 255, 65, 0.1);
    }
    .institution-name { color: #00ff41; font-family: 'Playfair Display', serif; font-size: 1.2rem; font-weight: bold; margin-bottom: 10px; }
    .metric-row { display: flex; justify-content: space-between; margin-bottom: 5px; font-family: monospace; }
    .label { color: #888; font-size: 0.8rem; }
    .value { color: #fff; font-size: 0.9rem; font-weight: bold; }
    
    /* Progress Bar for Ownership */
    .progress-bg { background: rgba(255, 255, 255, 0.1); height: 6px; border-radius: 3px; margin-top: 10px; overflow: hidden; }
    .progress-fill { background: #00ff41; height: 100%; border-radius: 3px; box-shadow: 0 0 10px #00ff41; }
</style>
""", unsafe_allow_html=True)

ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)

def render_whale_cards(df, title):
    st.markdown(f"<h2 style='color:#00ff41; text-shadow: 0 0 10px #00ff41;'>// {title}</h2>", unsafe_allow_html=True)
    if df is not None and not df.empty:
        # Dynamic Clean-up
        df = df.rename(columns={"Holder": "H", "Shares": "S", "% Out": "P", "Value": "V"})
        
        # Start Grid
        html_code = "<div class='whale-grid'>"
        
        for index, row in df.iterrows():
            name = row.get('H', 'UNKNOWN_ENTITY')
            shares = f"{row.get('S', 0):,}"
            value = f"${row.get('V', 0):,}"
            percent = row.get('P', 0) * 100 # Convert to percentage
            
            html_code += f"""
            <div class='whale-card'>
                <div class='institution-name'>{name}</div>
                <div class='metric-row'>
                    <span class='label'>SHARES</span>
                    <span class='value'>{shares}</span>
                </div>
                <div class='metric-row'>
                    <span class='label'>VALUE</span>
                    <span class='value'>{value}</span>
                </div>
                <div class='metric-row'>
                    <span class='label'>OWNERSHIP</span>
                    <span class='value'>{percent:.2f}%</span>
                </div>
                <div class='progress-bg'>
                    <div class='progress-fill' style='width: {min(percent * 10, 100)}%;'></div>
                </div>
            </div>
            """
        html_code += "</div>"
        st.markdown(html_code, unsafe_allow_html=True)
    else:
        st.info("SIGNAL_LOST: No whale data detected.")

# Execute Renders
render_whale_cards(stock.institutional_holders, "INSTITUTIONAL_WHALES")
render_whale_cards(stock.mutualfund_holders, "MUTUAL_FUND_EXPOSURE")
