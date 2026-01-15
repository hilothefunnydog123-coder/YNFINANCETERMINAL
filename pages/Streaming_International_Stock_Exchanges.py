from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape_301_exchanges():
    options = Options()
    options.add_argument("--headless") # Run in background
    driver = webdriver.Chrome(options=options)
    
    # Target the global aggregator page
    driver.get("https://finance.yahoo.com/world-indices")
    time.sleep(5) # Allow live data to populate
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup.find('table') # Finding the main global table
    
    data = []
    # Scraping rows: Name, Last Price, Change, % Change
    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')
        if cols:
            data.append({
                "Exchange": cols[1].text,
                "Price": cols[2].text,
                "Change": cols[3].text
            })
    driver.quit()
    return pd.DataFrame(data)
