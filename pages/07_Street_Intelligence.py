import streamlit as st
import yfinance as yf
import pandas as pd
def inject_stark_ui_v2():
    st.markdown("""
        <style>
        /* 1. STICKY HUD - FORCED TO TOP */
        [data-testid="stHeader"] {
            background: rgba(0,0,0,0.95) !important;
            border-bottom: 2px solid #00ffff !important;
            box-shadow: 0 0 20px #00ffff !important;
        }

        /* 2. THE SECTION CONTAINER (The "Jarvis Frame") */
        .stark-frame {
            position: relative !important;
            border: 1px solid rgba(0, 255, 255, 0.2) !important;
            background: linear-gradient(135deg, rgba(0,255,255,0.05) 0%, transparent 100%) !important;
            padding: 25px !important;
            margin: 20px 0 !important;
            border-radius: 0 20px 0 20px !important;
            overflow: hidden !important;
        }

        /* 3. NEON CORNER BRACKETS */
        .stark-frame::before {
            content: "";
            position: absolute;
            top: 0; left: 0; width: 30px; height: 30px;
            border-top: 4px solid #00ffff; border-left: 4px solid #00ffff;
        }
        .stark-frame::after {
            content: "";
            position: absolute;
            bottom: 0; right: 0; width: 30px; height: 30px;
            border-bottom: 4px solid #00ffff; border-right: 4px solid #00ffff;
        }

        /* 4. TECH-HEADER STYLING */
        .stark-header {
            color: #00ffff !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 1.2rem !important;
            letter-spacing: 6px !important;
            text-transform: uppercase !important;
            text-shadow: 0 0 15px #00ffff !important;
            margin-bottom: 15px !important;
            display: block !important;
        }

        /* 5. SCANNER LINE ANIMATION */
        .scanner {
            width: 100%;
            height: 2px;
            background: linear-gradient(90deg, transparent, #00ffff, transparent);
            position: absolute;
            top: 0; left: 0;
            animation: moveScan 4s infinite linear;
            opacity: 0.5;
        }

        @keyframes moveScan {
            0% { top: 0; }
            100% { top: 100%; }
        }
        </style>
    """, unsafe_allow_html=True)

# Run the injector
inject_stark_ui_v2()
# 1. LAYOUT LOCK
st.set_page_config(layout="wide", page_title="STREET_INTEL_v2")

# 2. STYLING ENGINE (Kept exactly as you liked)
st.markdown("""
<style>
    [data-testid="stAppViewBlockContainer"] { padding-top: 2rem; max-width: 100% !important; }
    .st-key-whale_card {
        background: rgba(0, 255, 65, 0.03);
        border: 1px solid rgba(0, 255, 65, 0.2);
        border-radius: 15px; padding: 20px; transition: 0.3s ease;
    }
    .metric-label { color: #888; font-family: monospace; font-size: 11px; text-transform: uppercase; }
    .metric-value { color: #fff; font-family: 'Courier New', Courier, monospace; font-weight: bold; font-size: 16px; }
</style>
""", unsafe_allow_html=True)

ticker = st.session_state.get('ticker', 'NVDA')
stock = yf.Ticker(ticker)

st.markdown(f"<h1 style='color:#00ff41; font-family:monospace;'>// STREET_INTEL: {ticker}</h1>", unsafe_allow_html=True)

def render_whale_section(df, title):
    st.markdown(f"<h3 style='color:#00ff41; margin-top:20px;'>// {title}</h3>", unsafe_allow_html=True)
    
    if df is not None and not df.empty:
        # --- THE FIX: DYNAMIC COLUMN DETECT ---
        # We hunt for the ownership column because names like 'pctHeld' or '% Out' change per ticker
        pct_col = next((c for c in df.columns if any(x in c.lower() for x in ['%', 'pct', 'out'])), None)
        
        cols_per_row = 4
        rows = [df.iloc[i:i + cols_per_row] for i in range(0, len(df), cols_per_row)]
        
        for row_df in rows:
            cols = st.columns(cols_per_row)
            for i, (_, item) in enumerate(row_df.iterrows()):
                with cols[i]:
                    with st.container(border=True):
                        name = item.get('Holder', 'N/A')
                        shares = f"{int(item.get('Shares', 0)):,}"
                        val = f"${int(item.get('Value', 0)):,}"
                        
                        # --- THE FIX: PERCENTAGE SCALING ---
                        raw_pct = item.get(pct_col, 0) if pct_col else 0
                        # If the value is a small decimal (e.g. 0.08), multiply by 100
                        pct = raw_pct * 100 if raw_pct < 1.0 else raw_pct
                        
                        st.markdown(f"<div style='color:#00ff41; font-weight:bold; font-size:18px; margin-bottom:10px;'>{name}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='metric-label'>Position</div><div class='metric-value'>{shares}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='metric-label'>Value</div><div class='metric-value'>{val}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='metric-label'>Ownership</div><div class='metric-value'>{pct:.2f}%</div>", unsafe_allow_html=True)
                        
                        # Show progress relative to a 10% max for visual impact
                        st.progress(min(pct / 10.0, 1.0) if pct > 0 else 0.0)
    else:
        st.info("SIGNAL_OFFLINE: No Whale data found.")

render_whale_section(stock.institutional_holders, "INSTITUTIONAL_WHALES")
render_whale_section(stock.mutualfund_holders, "MUTUAL_FUND_EXPOSURE")
