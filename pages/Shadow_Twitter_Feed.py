import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import json
import asyncio
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from curl_cffi import requests as curl_requests
from twikit import Client

# --- 1. CORE ENGINE SETUP ---
st.set_page_config(layout="wide", page_title="YN_GLOBAL_SURVEILLANCE")

def get_headless_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

# --- 2. GLOBAL EXCHANGE SCRAPER (301+ Indices) ---
@st.cache_data(ttl=600)
def scrape_301_exchanges():
    url = "https://finance.yahoo.com/world-indices"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('tr', class_='simpTblRow')
        data = []
        for row in rows:
            name = row.find('td', {'field': 'name'}).text
            price = row.find('td', {'field': 'lastPrice'}).text
            change = row.find('td', {'field': 'change'}).text
            data.append({"Market": name, "Price": price, "Change": change})
        return pd.DataFrame(data)
    except Exception as e:
        return pd.DataFrame([{"Error": f"Source Blocked: {str(e)}"}])

# --- 3. SHADOW X FEED (No API) ---
async def fetch_shadow_tweets(query):
    client = Client('en-US')
    try:
        # Requires cookies.json in your repo root (Exported from your browser)
        client.load_cookies('cookies.json')
        tweets = await client.search_tweet(query, 'Latest', count=10)
        return [{"User": t.user.name, "Content": t.text} for t in tweets]
    except:
        return [{"User": "SYSTEM", "Content": "Cookie session expired. Update cookies.json"}]

# --- 4. OIL TANKER SURVEILLANCE (Exact AIS Locations) ---
def get_tanker_intel(mmsi_list):
    tanker_data = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for mmsi in mmsi_list:
        try:
            url = f"https://www.vesselfinder.com/vessels/details/{mmsi}"
            res = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(res.text, 'html.parser')
            lat = soup.find('span', class_='coordinate lat').text
            lon = soup.find('span', class_='coordinate lon').text
            status = soup.find('td', class_='v3').text
            tanker_data.append({"MMSI": mmsi, "Lat": lat, "Lon": lon, "Status": status})
        except:
            continue
    return pd.DataFrame(tanker_data)

# --- 5. TERMINAL UI ---
st.title("🌐 YN GLOBAL COMMAND CENTER")

t1, t2, t3 = st.tabs(["🏛️ 301 EXCHANGES", "🐦 SHADOW X FEED", "🚢 TANKER SURVEILLANCE"])

with t1:
    st.subheader("Global Equity Streams")
    indices_df = scrape_301_exchanges()
    st.dataframe(indices_df, use_container_width=True)

with t2:
    st.subheader("Curated Financial Intel")
    if st.button("RUN GHOST SEARCH"):
        tweets = asyncio.run(fetch_shadow_tweets("$OIL OR $BTC OR $NVDA filter:verified"))
        for t in tweets:
            st.markdown(f"**{t['User']}**: {t['Content']}")

with t3:
    st.subheader("Real-Time Tanker Tracking")
    # Example MMSIs for major VLCCs (Very Large Crude Carriers)
    mmsis = ["9332810", "9332822", "9292307"] 
    tanker_df = get_tanker_intel(mmsis)
    st.table(tanker_df)
