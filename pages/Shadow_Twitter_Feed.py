import streamlit as st
import pandas as pd
import asyncio
import json
import time
import pydeck as pdk
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from twikit import Client

# --- 1. CLOUD-READY BROWSER ENGINE ---
def get_headless_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/usr/bin/chromium" 
    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=options)

# --- 2. 𝕏-TERMINAL STYLING ---
st.markdown("""
<style>
    .tweet-container {
        background-color: #000000;
        border: 1px solid #2f3336;
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 12px;
    }
    .tweet-header {
        color: #e7e9ea;
        font-weight: bold;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 4px;
    }
    .tweet-content {
        color: #e7e9ea;
        font-size: 15px;
        line-height: 1.4;
    }
    .map-border {
        border: 1px solid #00ffff;
        border-radius: 8px;
        padding: 2px;
        background: #000;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. THE ACTUAL WORLD MAP (FIXED) ---
def render_live_world_map():
    # Example Vessel Data (Using floats for coordinates)
    vessels = pd.DataFrame([
        {"name": "VLCC_ARABIA", "lat": 25.1, "lon": 55.2, "status": "Laden"},
        {"name": "NORDIC_STAR", "lat": 1.2, "lon": 103.8, "status": "Transit"},
        {"name": "GULF_RUNNER", "lat": 26.5, "lon": 50.3, "status": "Underway"},
        {"name": "ATLANTIC_ACE", "lat": 40.7, "lon": -74.0, "status": "Moored"},
        {"name": "PACIFIC_PRIDE", "lat": 34.0, "lon": 139.0, "status": "Laden"}
    ])

    # VIEW STATE: Centered on global trade routes
    view_state = pdk.ViewState(
        latitude=15.0, 
        longitude=30.0, 
        zoom=1.2, 
        pitch=40
    )

    # GLOWING DATA LAYER
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=vessels,
        get_position="[lon, lat]",
        get_color="[0, 255, 255, 200]", # Cyan Glow
        get_radius=200000,
        pickable=True,
    )

    # MAP DECK: Using 'CartoDB.DarkMatter' (No API key needed for basic world view)
    deck = pdk.Deck(
        map_style=pdk.map_styles.CARTO_DARK, # This forces the land/ocean to show
        initial_view_state=view_state,
        layers=[layer],
        tooltip={"text": "{name}\nStatus: {status}"}
    )
    
    st.pydeck_chart(deck)

# --- 4. DATA ENGINES ---
async def get_shadow_tweets():
    client = Client('en-US')
    try:
        with open('cookies.json', 'r') as f:
            raw = json.load(f)
        formatted = {c['name']: c['value'] for c in raw} if isinstance(raw, list) else raw
        client.set_cookies(formatted) 
        tweets = await client.search_tweet('$OIL OR $NVDA filter:verified', 'Latest', count=8)
        return [{"User": t.user.name, "Handle": t.user.screen_name, "Text": t.text} for t in tweets]
    except Exception as e:
        return [{"User": "ERROR", "Handle": "system", "Text": str(e)}]

def scrape_301_exchanges():
    driver = get_headless_driver()
    try:
        driver.get("https://finance.yahoo.com/markets/world-indices/")
        time.sleep(8) # Wait for live prices
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        rows = soup.select('table tbody tr')
        return [{"Symbol": r.select('td')[0].text, "Price": r.select('td')[2].text} for r in rows if len(r.select('td')) > 2]
    finally:
        driver.quit()

# --- MAIN UI ---
st.set_page_config(layout="wide", page_title="YN_COMMAND")
st.title("🛰️ YN GLOBAL SURVEILLANCE")

tab1, tab2, tab3 = st.tabs(["📊 MARKETS", "🌍 LIVE_AIS_MAP", "𝕏 INTEL"])

with tab1:
    if st.button("SYNC_301_EXCHANGES"):
        data = scrape_301_exchanges()
        st.table(pd.DataFrame(data))

with tab2:
    st.subheader("Global Crude AIS Surveillance")
    st.markdown('<div class="map-border">', unsafe_allow_html=True)
    render_live_world_map() # This now renders land/water
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown("### 𝕏 Intelligence Stream")
    if st.button("RUN_SHADOW_SCAN"):
        feed = asyncio.run(get_shadow_tweets())
        for post in feed:
            st.markdown(f"""
            <div class="tweet-container">
                <div class="tweet-header">𝕏 {post['User']} <span style="color:#71767b; font-weight:normal;">@{post['Handle']}</span></div>
                <div class="tweet-content">{post['Text']}</div>
            </div>
            """, unsafe_allow_html=True)
