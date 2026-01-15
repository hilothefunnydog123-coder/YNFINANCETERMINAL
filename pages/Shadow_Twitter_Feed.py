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

# --- 1. THE ENGINE ---
def get_headless_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/usr/bin/chromium" 
    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=options)

# --- 2. AUTOMATIC TANKER TRACKER (NO HARDCODING) ---
def scrape_live_ais_data():
    """Automatically finds the 10 most recent active oil tankers."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
    # Type 8 = Oil/Chemical Tankers
    base_url = "https://www.vesselfinder.com/vessels?type=8" 
    
    fleet = []
    try:
        response = requests.get(base_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Grab the first 10 ships from the live global results table
        rows = soup.select("table.table-list tbody tr")[:10]
        
        for row in rows:
            ship_link = row.select_one("a.ship-link")
            if ship_link:
                ship_name = ship_link.text.strip()
                ship_path = ship_link['href']
                
                # Navigate to the specific ship's page for EXACT coordinates
                detail_res = requests.get(f"https://www.vesselfinder.com{ship_path}", headers=headers, timeout=5)
                detail_soup = BeautifulSoup(detail_res.text, 'html.parser')
                
                # Extract GPS coordinates from the live status table
                lat_str = detail_soup.find('span', class_='coordinate lat').text
                lon_str = detail_soup.find('span', class_='coordinate lon').text
                status = detail_soup.find('td', class_='v3').text
                
                # Clean coordinates into floats for PyDeck
                lat = float(''.join(c for c in lat_str if c.isdigit() or c == '.'))
                lon = float(''.join(c for c in lon_str if c.isdigit() or c == '.'))
                # Adjust for N/S and E/W
                if 'S' in lat_str: lat *= -1
                if 'W' in lon_str: lon *= -1
                
                fleet.append({"name": ship_name, "lat": lat, "lon": lon, "status": status})
        
        return pd.DataFrame(fleet)
    except Exception as e:
        st.error(f"AIS_SIGNAL_LOST: {e}")
        return pd.DataFrame()

# --- 3. DYNAMIC 𝕏 INTEL (ANY TICKER) ---
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
        return [{"User": "SYSTEM", "Handle": "error", "Text": f"Auth Failure: {str(e)}"}]

# --- 4. WORLD COMMAND INTERFACE ---
st.set_page_config(layout="wide")
st.title("🛰️ YN COMMAND: GLOBAL SURVEILLANCE")

col1, col2 = st.columns([2, 1])

# USER INPUTS
target_ticker = st.sidebar.text_input("📡 TARGET TICKER", value="NVDA").upper()
scan_trigger = st.sidebar.button("🔴 INITIATE GLOBAL SCAN")

tab1, tab2 = st.tabs(["🌍 LIVE_AIS_MAP", "𝕏 INTEL_STREAM"])

with tab1:
    if scan_trigger:
        with st.spinner("INTERCEPTING AIS SATELLITE FEED..."):
            tanker_df = scrape_live_ais_data() # This is now 100% automatic
            
            view_state = pdk.ViewState(latitude=20, longitude=30, zoom=1.1, pitch=40)
            layer = pdk.Layer(
                "ScatterplotLayer",
                data=tanker_df,
                get_position="[lon, lat]",
                get_color="[255, 140, 0, 200]", # Glowing Neon Orange
                get_radius=250000,
                pickable=True,
            )
            
            st.pydeck_chart(pdk.Deck(
                map_style=pdk.map_styles.CARTO_DARK, # Forces the world map to render
                initial_view_state=view_state,
                layers=[layer],
                tooltip={"text": "{name}\nStatus: {status}\nPos: {lat}, {lon}"}
            ))
            st.dataframe(tanker_df, use_container_width=True)

with tab2:
    if scan_trigger:
        st.subheader(f"𝕏 Intel Stream: ${target_ticker}")
        feed = asyncio.run(get_shadow_tweets(target_ticker)) # Fully dynamic
        for post in feed:
            st.markdown(f"""
            <div style="background:#000; border:1px solid #2f3336; padding:15px; border-radius:12px; margin-bottom:10px;">
                <div style="color:#fff; font-weight:bold;">𝕏 {post['User']} <span style="color:#71767b;">@{post['Handle']}</span></div>
                <div style="color:#fff; margin-top:5px;">{post['Text']}</div>
            </div>
            """, unsafe_allow_html=True)
