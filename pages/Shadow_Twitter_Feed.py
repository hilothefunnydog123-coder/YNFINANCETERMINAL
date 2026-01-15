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

# --- 1. CLOUD-READY BROWSER ENGINE ---
def get_headless_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/usr/bin/chromium" 
    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=options)

# --- 2. AUTOMATIC TANKER DISCOVERY ---
@st.cache_data(ttl=600) # Refresh data every 10 minutes
def scrape_live_ais_data():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
    base_url = "https://www.vesselfinder.com/vessels?type=8" 
    fleet = []
    try:
        response = requests.get(base_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.select("table.table-list tbody tr")[:8] # Top 8 active tankers
        
        for row in rows:
            ship_link = row.select_one("a.ship-link")
            if ship_link:
                ship_path = ship_link['href']
                detail_res = requests.get(f"https://www.vesselfinder.com{ship_path}", headers=headers, timeout=5)
                detail_soup = BeautifulSoup(detail_res.text, 'html.parser')
                
                # Scrape coordinates
                lat_str = detail_soup.find('span', class_='coordinate lat').text
                lon_str = detail_soup.find('span', class_='coordinate lon').text
                
                # Float conversion for PyDeck
                lat = float(''.join(c for c in lat_str if c.isdigit() or c == '.'))
                lon = float(''.join(c for c in lon_str if c.isdigit() or c == '.'))
                if 'S' in lat_str: lat *= -1
                if 'W' in lon_str: lon *= -1
                
                fleet.append({"name": ship_link.text.strip(), "lat": lat, "lon": lon})
        return pd.DataFrame(fleet)
    except:
        return pd.DataFrame()

# --- 3. DYNAMIC 𝕏 INTEL STREAM ---
async def get_shadow_tweets(ticker):
    client = Client('en-US')
    try:
        with open('cookies.json', 'r') as f:
            raw = json.load(f)
        formatted = {c['name']: c['value'] for c in raw} if isinstance(raw, list) else raw
        client.set_cookies(formatted) 
        # Search verified posts for the specific user-input ticker
        tweets = await client.search_tweet(f"${ticker} filter:verified", 'Latest', count=10)
        return [{"User": t.user.name, "Handle": t.user.screen_name, "Text": t.text} for t in tweets]
    except Exception as e:
        return [{"User": "SYSTEM", "Text": f"Auth Failure: {e}"}]

# --- 4. TERMINAL INTERFACE ---
st.set_page_config(layout="wide", page_title="YN_GLOBAL_SURVEILLANCE")
st.title("🛰️ YN GLOBAL COMMAND CENTER")

# Sidebar settings
ticker = st.sidebar.text_input("📡 TARGET TICKER", value="NVDA").upper()

# AUTOMATIC DATA FETCHING (No buttons)
with st.sidebar:
    st.write("Intercepting AIS Feeds...")
    tanker_df = scrape_live_ais_data()
    st.success(f"Detected {len(tanker_df)} Active Tankers")

tab1, tab2 = st.tabs(["🌍 LIVE_AIS_MAP", "𝕏 INTEL_STREAM"])

with tab1:
    # High-Tech World Map
    view_state = pdk.ViewState(latitude=20, longitude=30, zoom=1.1, pitch=40)
    
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=tanker_df,
        get_position="[lon, lat]",
        get_color="[255, 140, 0, 200]", # Neon Orange Glow
        get_radius=250000,
        pickable=True,
    )
    
    # Using CARTO_DARK ensures the world map renders without a key
    st.pydeck_chart(pdk.Deck(
        map_style=pdk.map_styles.CARTO_DARK, 
        initial_view_state=view_state,
        layers=[layer],
        tooltip={"text": "{name}\nCoordinates: {lat}, {lon}"}
    ))

with tab2:
    # Tweets load automatically on page load
    with st.spinner(f"Scouring 𝕏 for ${ticker}..."):
        feed = asyncio.run(get_shadow_tweets(ticker))
        for post in feed:
            st.markdown(f"""
            <div style="background:#000; border:1px solid #2f3336; padding:15px; border-radius:12px; margin-bottom:10px;">
                <div style="color:#fff; font-weight:bold;">𝕏 {post.get('User')} <span style="color:#71767b;">@{post.get('Handle')}</span></div>
                <div style="color:#fff; margin-top:5px;">{post.get('Text')}</div>
            </div>
            """, unsafe_allow_html=True)
