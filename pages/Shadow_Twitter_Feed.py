import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import asyncio
import json
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from twikit import Client

# --- 1. CORE BROWSER ENGINE ---
def get_headless_driver():
    options = Options()
    options.add_argument("--headless=new") # 2026 Headless Mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

# --- 2. 301+ EXCHANGES (Aggregator Scraper) ---
@st.cache_data(ttl=600)
def scrape_301_exchanges():
    driver = get_headless_driver()
    try:
        driver.get("https://finance.yahoo.com/markets/world-indices/")
        time.sleep(7) # Wait for JS Streamer
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # 2026 CSS Selectors for the World Indices table
        rows = soup.select('table tbody tr')
        data = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) > 4:
                data.append({
                    "Symbol": cols[0].text,
                    "Name": cols[1].text,
                    "Price": cols[2].text,
                    "Change": cols[3].text,
                    "% Change": cols[4].text
                })
        return pd.DataFrame(data)
    finally:
        driver.quit()

# --- 3. SHADOW X-FEED (Cookie-Based) ---
async def get_shadow_tweets():
    client = Client('en-US')
    try:
        # Load your cookies.json exported from browser
        client.load_cookies('cookies.json')
        query = "$OIL OR $BTC OR $NVDA filter:verified"
        tweets = await client.search_tweet(query, 'Latest', count=10)
        return [{"User": t.user.name, "Text": t.text} for t in tweets]
    except Exception as e:
        return [{"User": "SYSTEM", "Text": f"Cookie Auth Failed: {e}"}]

# --- 4. OIL TANKER AIS SURVEILLANCE ---
def get_tanker_gps(mmsi):
    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"https://www.vesselfinder.com/vessels/details/{mmsi}"
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        # Scrape current coordinate spans
        lat = soup.find('span', class_='coordinate lat').get_text(strip=True)
        lon = soup.find('span', class_='coordinate lon').get_text(strip=True)
        status = soup.find('td', class_='v3').get_text(strip=True)
        return {"MMSI": mmsi, "Lat": lat, "Lon": lon, "Status": status}
    except:
        return {"MMSI": mmsi, "Lat": "N/A", "Lon": "N/A", "Status": "OFFLINE"}

# --- 5. TERMINAL UI ---
st.set_page_config(layout="wide")
st.title("🌐 YN GLOBAL COMMAND CENTER")

tabs = st.tabs(["🏛️ 301 EXCHANGES", "🐦 SHADOW FEED", "🚢 TANKER INTEL"])

with tabs[0]:
    if st.button("SYNC_WORLD_MARKETS"):
        df = scrape_301_exchanges()
        st.dataframe(df, use_container_width=True)

with tabs[1]:
    if st.button("SCAN_CASHTAGS"):
        feed = asyncio.run(get_shadow_tweets())
        for tweet in feed:
            st.markdown(f"**{tweet['User']}**: {tweet['Text']}")
            st.divider()

with tabs[2]:
    st.subheader("Global Crude Carrier Fleet")
    # Example Active Tanker MMSIs
    mmsi_list = ["9332810", "9332822", "9292307"]
    if st.button("TRACK_TANKERS"):
        fleet = [get_tanker_gps(m) for m in mmsi_list]
        st.table(pd.DataFrame(fleet))
