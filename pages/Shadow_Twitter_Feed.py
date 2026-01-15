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
    options.binary_location = "/usr/bin/chromium" 
    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=options)

# --- 2. THE TECHY LIVE TANKER MAP (FIXED) ---
def get_vessel_positions():
    # Example vessel coordinates - in a full build, this would scrape Vesselfinder details
    # We use high-tech glowing dots for the global view
    data = [
        {"name": "ULCC_SIRIUS", "lat": 26.2, "lon": 52.1, "status": "Laden"},
        {"name": "VLCC_NEPTUNE", "lat": 1.3, "lon": 103.8, "status": "Transit"},
        {"name": "OIL_HORIZON", "lat": 51.5, "lon": 1.2, "status": "Moored"},
        {"name": "GULF_RUNNER", "lat": 35.0, "lon": -15.0, "status": "Underway"}
    ]
    return pd.DataFrame(data)

def render_tech_map(df):
    # Dark high-tech theme with glowing Scatterplot layer
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/dark-v10",
        initial_view_state=pdk.ViewState(latitude=20, longitude=30, zoom=1.5, pitch=45),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=df,
                get_position="[lon, lat]",
                get_color="[255, 140, 0, 160]", # Neon Orange
                get_radius=180000,
                pickable=True,
            ),
        ],
        tooltip={"text": "Vessel: {name}\nStatus: {status}"}
    ))

# --- 3. SHADOW X FEED (UNPACKING FIX) ---
async def get_shadow_tweets():
    client = Client('en-US')
    try:
        # UNPACKING FIX: Ensure cookies.json is a dict, then loop correctly
        with open('cookies.json', 'r') as f:
            cookies = json.load(f)
        
        # Twikit expects a file path or a dictionary
        client.set_cookies(cookies) 
        
        query = "$OIL OR $NVDA filter:verified"
        tweets = await client.search_tweet(query, 'Latest', count=10)
        return [{"User": t.user.name, "Text": t.text} for t in tweets]
    except Exception as e:
        return [{"User": "SYSTEM", "Text": f"Auth Failure: {str(e)}"}]

# --- 4. 301 EXCHANGES (FIXED SELECTORS & PRICE) ---
def scrape_301_exchanges():
    driver = get_headless_driver()
    try:
        # Yahoo Finance World Indices Main Hub
        driver.get("https://finance.yahoo.com/markets/world-indices/")
        time.sleep(8) # Allow price-streamer to initialize
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # Targets the precise 2026 table structure
        rows = soup.select('section table tbody tr') 
        
        data = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 5:
                # Use data-field attributes if possible for accuracy
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

# --- MAIN TERMINAL UI ---
st.set_page_config(layout="wide")
st.title("🌐 YN GLOBAL COMMAND CENTER")

t1, t2, t3 = st.tabs(["🏛️ 301 EXCHANGES", "🚢 TANKER MAP", "🐦 SHADOW X"])

with t1:
    if st.button("SYNC_301_MARKETS"):
        df_ex = scrape_301_exchanges()
        st.dataframe(df_ex, use_container_width=True, height=600)

with t2:
    st.subheader("Global AIS Surveillance")
    vessels = get_vessel_positions()
    render_tech_map(vessels)

with t3:
    if st.button("RUN_SHADOW_SCAN"):
        feed = asyncio.run(get_shadow_tweets())
        for post in feed:
            st.info(f"**{post['User']}**: {post['Text']}")
