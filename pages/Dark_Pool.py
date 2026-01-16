import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import streamlit as st

# --- INITIALIZE SESSION STATE ---
# This prevents the AttributeError by ensuring 'ticker' exists
if 'ticker' not in st.session_state:
    st.session_state.ticker = "NVDA"  # Set your preferred default ticker

def get_real_dark_pool_ratio(ticker):
    """
    Scrapes live institutional 'Off-Exchange' volume ratios.
    This replaces the 'preset' data with actual market fingerprints.
    """
    try:
        # We target a high-traffic dashboard that displays public FINRA reports
        url = f"https://chartexchange.com/symbol/nasdaq-{ticker.lower()}/stats/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        
        # We look for the 'Off-Exchange' or 'Dark Pool' table row
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Logic to find the specific percentage in the HTML
        # Usually found in a <td> element following the label 'Off-Exchange'
        tables = pd.read_html(response.text)
        for df in tables:
            if 'Venue' in df.columns and 'Volume' in df.columns:
                off_exchange = df[df['Venue'].str.contains('Off-Exchange', na=False)]
                if not off_exchange.empty:
                    # Returns the actual % from the live table
                    return off_exchange['Percent'].values[0]
        return "N/A"
    except Exception as e:
        return "SYNC_ERROR"

# --- HUD Implementation ---
st.markdown(f"### 🌑 INSTITUTIONAL_SHADOW_FLOW: {st.session_state.ticker}")
dp_ratio = get_real_dark_pool_ratio(st.session_state.ticker)

col1, col2 = st.columns([1, 2])
with col1:
    st.metric("DARK_POOL_RATIO", f"{dp_ratio}", delta="LIVE_FINRA_FEED")
    if "N/A" not in str(dp_ratio) and float(str(dp_ratio).replace('%','')) > 45:
        st.warning("⚠️ CRITICAL_SIGNAL: Institutional 'Hidden' Buying Detected")
with col2:
    st.info("Direct intercept from FINRA/TRF Reporting. This represents trades executed away from public lit exchanges.")
