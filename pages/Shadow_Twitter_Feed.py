import streamlit as st
import pandas as pd
import requests
import asyncio
import json
import time
import pydeck as pdk
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from twikit import Client

# --- 1. CLOUD-STABLE DRIVER (Fixes SessionError) ---
def get_headless_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/usr/bin/chromium" 
    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=options)

# --- 2. TECHY TANKER MAP (Visual Logic) ---
def render_tech_map():
    # Glowing orange dots on a dark Mapbox style
    # Coordinates must be floats!
    df = pd.DataFrame([
        {"name": "VLCC_ARABIA", "lat": 25.1, "lon": 55.2, "status": "Laden"},
        {"name": "NORDIC_STAR", "lat": 1.2, "lon": 103.8, "status": "Transit"},
        {"name": "GULF_EXPLORER", "lat": 26.5, "lon": 50.3, "status": "Underway"},
        {"name": "ATLANTIC_ACE", "lat": 40.7, "lon": -74.0, "status": "Moored"}
    ])

    view_state = pdk.ViewState(latitude=20, longitude=30, zoom=1.2, pitch=40)
    
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position="[lon, lat]",
        get_color="[255, 140, 0, 200]", # Neon Orange Glow
        get_radius=250000,
        pickable=True,
    )

    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/dark-v11",
        initial_view_state=view_state,
        layers=[layer],
        tooltip={"text": "Vessel: {name}\nStatus: {status}"}
    ))

# --- 3. SHADOW X FEED (Fixes Unpacking/Cookie Format) ---
async def get_shadow_tweets():
    client = Client('en-US')
    try:
        with open('cookies.json', 'r') as f:
            raw_cookies = json.load(f)
        
        # TRANSFORMATION LOGIC: Converts list format to twikit dict format
        if isinstance(raw_cookies, list):
            formatted_cookies = {c['name']: c['value'] for c in raw_cookies}
        else:
            formatted_cookies = raw_cookies
            
        client.set_cookies(formatted_cookies) 
        tweets = await client.search_tweet('$OIL OR $NVDA filter:verified', 'Latest', count=10)
        return [{"User": t.user.name, "Text": t.text} for t in tweets]
    except Exception as e:
        return [{"User": "SYSTEM", "Text": f"Auth Failure: {str(e)}"}]

# --- 4. 301 EXCHANGES (Fixed Selectors & Unlimited Rows) ---
def scrape_301_exchanges():
    driver = get_headless_driver()
    try:
        # Targeting the master indices page
        driver.get("https://finance.yahoo.com/markets/world-indices/")
        time.sleep(8) # Wait for live prices to stream in
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # Target the 2026 Yahoo Finance table structure
        rows = soup.select('table tbody tr')
        
        data = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 5:
                data.append({
                    "Symbol": cols[0].text.strip(),
                    "Name": cols[1].text.strip(),
                    "Price": cols[2].text.strip(),
                    "Change": cols[3].text.strip(),
                    "% Change": cols[4].text.strip()
                })
        return pd.DataFrame(data)
    finally:
        driver.quit()

# --- MAIN INTERFACE ---
st.set_page_config(layout="wide", page_title="YN_GLOBAL_COMMAND")
st.title("🌐 YN GLOBAL COMMAND CENTER")

tab1, tab2, tab3 = st.tabs(["🏛️ 301_EXCHANGES", "🚢 TANKER_MAP", "🐦 SHADOW_X"])

with tab1:
    if st.button("SYNC_GLOBAL_MARKETS"):
        with st.spinner("Harvesting World Exchanges..."):
            df = scrape_301_exchanges()
            st.dataframe(df, use_container_width=True, height=600)

with tab2:
    st.subheader("Global AIS Maritime Surveillance")
    # This renders the PyDeck high-tech map
    render_tech_map()

with tab3:
    if st.button("EXECUTE_SHADOW_SCAN"):
        with st.spinner("Scraping Verified Intel..."):
            feed = asyncio.run(get_shadow_tweets())
            for post in feed:
                st.info(f"**{post['User']}**: {post['Text']}")
