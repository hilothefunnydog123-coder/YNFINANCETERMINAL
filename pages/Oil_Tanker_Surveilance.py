import requests

def get_oil_tanker_locations():
    # The 'SHIPS_CURRENT' datasheet endpoint used by trackers
    # Filter for '8' (Tankers) and 'Cargo'
    url = "https://www.marinetraffic.com/en/ais/index/ships/all/ship_type:8"
    
    headers = {'User-Agent': 'Mozilla/5.0'} # Impersonate browser
    response = requests.get(url, headers=headers)
    
    # Parse the raw HTML table for the 'Exact' Lat/Lon columns
    soup = BeautifulSoup(response.text, 'html.parser')
    vessels = soup.find_all('div', class_='vessel-name')
    
    # For a deep dive, you would scrape the ship-specific detail page
    # which holds the Draught (Full vs Empty) data
    return [v.text for v in vessels]
