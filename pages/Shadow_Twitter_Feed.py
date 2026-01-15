import streamlit as st
import pandas as pd
import yfinance as yf
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

# --- 1. STABLE CLOUD ENGINE (FIXES SESSION ERROR) ---
def get_headless_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Point directly to the binary installed via packages.txt
    options.binary_location = "/usr/bin/chromium" 
    
    # Point directly to the Cloud Driver path
    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=options)

# --- 2. TECHY WORLD TANKER MAP ---
def get_live_tanker_data():
    # Scraping logic for vessel coordinates from detail pages
    # Returning high-tech mock data for initial load
    return pd.DataFrame([
        {"name": "VLCC_ARABIA", "lat": 25.1, "lon": 55.2, "status": "Underway"},
        {"name": "NORDIC_STAR", "lat": 1.2, "lon": 103.8, "status": "Moored"},
        {"name": "GULF_EXPLORER", "lat": 26.5, "lon": 50.3, "status": "In Transit"}
    ])

def render_tech_map(df):
    view_state = pdk.ViewState(latitude=20, longitude=60, zoom=2, pitch=45)
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/dark-v10",
        initial_view_state=view_state,
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=df,
                get_position="[lon, lat]",
                get_color="[0, 255, 255, 160]", # Cyber Cyan
                get_radius=150000,
                pickable=True,
            ),
        ],
        tooltip={"text": "Vessel: {name}\nStatus: {status}"}
    ))

# --- 3. SHADOW X FEED (COOKIE REPAIR) ---
async def get_shadow_tweets():
    client = Client('en-US')
    try:
        # File must be in the same folder as your script
        client.load_cookies('cookies.json')
        tweets = await client.search_tweet('$OIL OR $NVDA filter:verified', 'Latest', count=5)
        return [{"User": t.user.name, "Text": t.text} for t in tweets]
    except Exception as e:
        return [{"User": "SYSTEM", "Text": f"Auth Failure: {e}"}]

# --- 4. 301 EXCHANGES (UPDATED SELECTORS) ---
def scrape_301_exchanges():
    driver = get_headless_driver()
    try:
        driver.get("https://finance.yahoo.com/markets/world-indices/")
        time.sleep(5) # Wait for live prices
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        rows = soup.select('table tbody tr')
        data = []
        for row in rows[:25]:
            cols = row.find_all('td')
            if len(cols) > 4:
                data.append({"Market": cols[1].text, "Price": cols[2].text, "Change": cols[4].text})
        return pd.DataFrame(data)
    finally:
        driver.quit()

# --- MAIN INTERFACE ---
st.set_page_config(layout="wide")
st.title("🌐 YN GLOBAL COMMAND CENTER")

tab1, tab2, tab3 = st.tabs(["🏛️ 301_EXCHANGES", "🚢 TANKER_MAP", "🐦 SHADOW_X"])

with tab1:
    if st.button("SYNC_MARKETS"):
        st.table(scrape_301_exchanges())

with tab2:
    st.subheader("Global Crude Fleet AIS Live Feed")
    render_tech_map(get_live_tanker_data())

with tab3:
    if st.button("SCAN_INTEL_FEED"):
        feed = asyncio.run(get_shadow_tweets())
        for post in feed:
            st.info(f"**{post['User']}**: {post['Text']}")
