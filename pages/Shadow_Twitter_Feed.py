import streamlit as st
import pandas as pd
import asyncio
import json
import time
import pydeck as pdk
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from twikit import Client
from streamlit_autorefresh import st_autorefresh

# --- 1. AUTOMATIC REFRESH (Every 60 Seconds) ---
# Ensures the map and feed update while you watch
st_autorefresh(interval=60000, key="global_refresh")

# --- 2. GHOST ENGINE SETUP (Cloud Stable) ---
def get_headless_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/usr/bin/chromium" 
    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=options)

# --- 3. LIVE TANKER DISCOVERY (Automatic) ---
@st.cache_data(ttl=300) 
def scrape_live_ais():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
    url = "https://www.vesselfinder.com/vessels?type=8" 
    fleet = []
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Targets the precise 2026 table structure
        rows = soup.select("table.table-list tbody tr")
        
        for row in rows[:8]: # Grab top 8 laden tankers
            ship_link = row.select_one("a.ship-link")
            if ship_link:
                # Scrape detail page for exact coordinates
                res = requests.get(f"https://www.vesselfinder.com{ship_link['href']}", headers=headers)
                d_soup = BeautifulSoup(res.text, 'html.parser')
                lat_t = d_soup.find('span', class_='coordinate lat').text
                lon_t = d_soup.find('span', class_='coordinate lon').text
                
                # Convert string coords to floats for PyDeck
                lat = float(''.join(c for c in lat_t if c.isdigit() or c == '.'))
                lon = float(''.join(c for c in lon_t if c.isdigit() or c == '.'))
                if 'S' in lat_t: lat *= -1
                if 'W' in lon_t: lon *= -1
                fleet.append({"name": ship_link.text.strip(), "lat": lat, "lon": lon})
        return pd.DataFrame(fleet)
    except Exception as e:
        return pd.DataFrame([{"name": "SEARCHING...", "lat": 25.0, "lon": 55.0}])

# --- 4. SHADOW X FEED (Cookie Format Fix) ---
async def get_shadow_tweets(ticker):
    client = Client('en-US')
    try:
        with open('cookies.json', 'r') as f:
            raw = json.load(f)
        # UNPACKING FIX: Converts your list into a dictionary twikit expects
        formatted = {c['name']: c['value'] for c in raw} if isinstance(raw, list) else raw
        client.set_cookies(formatted) 
        # Search verified posts for the specific user-input ticker
        tweets = await client.search_tweet(f"${ticker} filter:verified", 'Latest', count=10)
        return [{"User": t.user.name, "Handle": t.user.screen_name, "Text": t.text} for t in tweets]
    except Exception as e:
        return [{"User": "SYSTEM", "Text": f"Auth Failure: {e}"}]

# --- MAIN UI ---
st.set_page_config(layout="wide", page_title="YN_COMMAND")
st.title("🛰️ YN GLOBAL SURVEILLANCE TERMINAL")

ticker = st.sidebar.text_input("📡 TARGET TICKER", value="NVDA").upper()
tanker_df = scrape_live_ais() # Runs automatically on load

t1, t2 = st.tabs(["🌍 LIVE_AIS_MAP", "𝕏 INTEL_STREAM"])

with t1:
    # CARTO_DARK fixes the black void without an API key
    st.pydeck_chart(pdk.Deck(
        map_style=pdk.map_styles.CARTO_DARK, 
        initial_view_state=pdk.ViewState(latitude=15, longitude=30, zoom=1.1, pitch=40),
        layers=[pdk.Layer("ScatterplotLayer", data=tanker_df, get_position="[lon, lat]", 
                          get_color="[0, 255, 255, 180]", get_radius=200000)],
        tooltip={"text": "Ship: {name}\nPos: {lat}, {lon}"}
    ))

with t2:
    st.subheader(f"𝕏 Intel: ${ticker}")
    feed = asyncio.run(get_shadow_tweets(ticker))
    for post in feed:
        st.markdown(f"""
        <div style="background:#000; border:1px solid #2f3336; padding:15px; border-radius:12px; margin-bottom:10px;">
            <div style="color:#fff; font-weight:bold;">𝕏 {post.get('User')} <span style="color:#71767b;">@{post.get('Handle')}</span></div>
            <div style="color:#fff; margin-top:5px;">{post.get('Text')}</div>
        </div>""", unsafe_allow_html=True)
