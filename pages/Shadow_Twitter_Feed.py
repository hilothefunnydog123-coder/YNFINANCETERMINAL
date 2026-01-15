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

# --- 1. GHOST ENGINE SETUP ---
def get_headless_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/usr/bin/chromium" 
    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=options)

# --- 2. CUSTOM X UI & TERMINAL STYLING ---
st.markdown("""
<style>
    /* X Tweet Template Styling */
    .tweet-container {
        background-color: #000000;
        border: 1px solid #2f3336;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .tweet-header {
        color: #e7e9ea;
        font-weight: bold;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .tweet-content {
        color: #e7e9ea;
        margin-top: 5px;
        font-size: 15px;
        line-height: 1.5;
    }
    .x-logo {
        font-size: 20px;
        font-weight: bold;
        color: white;
    }
    /* Map Container */
    .map-frame {
        border: 2px solid #00ffff;
        border-radius: 15px;
        padding: 5px;
        background: #000;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. HIGH-TECH WORLD MAP (PyDeck) ---
def render_tech_map():
    # Glowing data for global tankers (Lat/Lon MUST be floats)
    vessels = pd.DataFrame([
        {"name": "VLCC_ARABIA", "lat": 25.1, "lon": 55.2, "status": "Laden"},
        {"name": "NORDIC_STAR", "lat": 1.2, "lon": 103.8, "status": "Transit"},
        {"name": "GULF_EXPLORER", "lat": 26.5, "lon": 50.3, "status": "Underway"},
        {"name": "ATLANTIC_ACE", "lat": 40.7, "lon": -74.0, "status": "Moored"},
        {"name": "PACIFIC_PRIDE", "lat": 34.0, "lon": 139.0, "status": "Laden"}
    ])

    view_state = pdk.ViewState(latitude=20, longitude=30, zoom=1.1, pitch=45)
    
    # Glowing Cyan Layer for Hubs / Vessels
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=vessels,
        get_position="[lon, lat]",
        get_color="[0, 255, 255, 180]", # Neon Cyan
        get_radius=250000,
        pickable=True,
    )

    deck = pdk.Deck(
        map_style="mapbox://styles/mapbox/dark-v11",
        initial_view_state=view_state,
        layers=[layer],
        tooltip={"text": "Vessel: {name}\nStatus: {status}"}
    )
    st.pydeck_chart(deck)

# --- 4. SHADOW X FEED ENGINE ---
async def get_shadow_tweets():
    client = Client('en-US')
    try:
        with open('cookies.json', 'r') as f:
            raw_cookies = json.load(f)
        formatted = {c['name']: c['value'] for c in raw_cookies} if isinstance(raw_cookies, list) else raw_cookies
        client.set_cookies(formatted) 
        tweets = await client.search_tweet('$OIL OR $NVDA filter:verified', 'Latest', count=10)
        return [{"User": t.user.name, "Handle": t.user.screen_name, "Text": t.text} for t in tweets]
    except Exception as e:
        return [{"User": "SYSTEM", "Handle": "error", "Text": f"Auth Failure: {str(e)}"}]

# --- 5. 301 EXCHANGES ---
def scrape_301_exchanges():
    driver = get_headless_driver()
    try:
        driver.get("https://finance.yahoo.com/markets/world-indices/")
        time.sleep(8)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        rows = soup.select('table tbody tr')
        data = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 5:
                data.append({
                    "Symbol": cols[0].text.strip(),
                    "Name": cols[1].text.strip(),
                    "Price": cols[2].text.strip(),
                    "Change": cols[3].text.strip()
                })
        return pd.DataFrame(data)
    finally:
        driver.quit()

# --- MAIN INTERFACE ---
st.set_page_config(layout="wide", page_title="YN_GLOBAL_COMMAND")
st.title("𝕏 GLOBAL INTELLIGENCE TERMINAL")

tab1, tab2, tab3 = st.tabs(["🏛️ 301_MARKETS", "🚢 AIS_SURVEILLANCE", "🐦 SHADOW_FEED"])

with tab1:
    if st.button("SYNC_MARKETS"):
        df = scrape_301_exchanges()
        st.dataframe(df, use_container_width=True, height=600)

with tab2:
    st.subheader("Global Crude Fleet AIS Live Feed")
    st.markdown('<div class="map-frame">', unsafe_allow_html=True)
    render_tech_map()
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<span class="x-logo">𝕏 Intelligence Stream</span>', unsafe_allow_html=True)
    if st.button("EXECUTE_INTEL_SCAN"):
        feed = asyncio.run(get_shadow_tweets())
        for post in feed:
            st.markdown(f"""
            <div class="tweet-container">
                <div class="tweet-header">
                    <span>{post['User']}</span> 
                    <span style="color: #71767b; font-weight: normal;">@{post['Handle']} · 𝕏</span>
                </div>
                <div class="tweet-content">{post['Text']}</div>
            </div>
            """, unsafe_allow_html=True)
