"""
Automated script to export the live Dash dashboard as a static HTML file.
- Launches the Dash app
- Waits for the server to start
- Uses Selenium to save the main dashboard as HTML
"""
import subprocess
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os

# Path to Dash app and output HTML
DASH_APP = 'dash_app.py'
OUTPUT_HTML = os.path.join('..', 'outputs', 'dashboards', '00_master_dashboard.html')
DASH_URL = 'http://127.0.0.1:8050'

# Start Dash app in background
proc = subprocess.Popen(['python', DASH_APP])

# Wait for server to start
print('Waiting for Dash app to start...')
time.sleep(10)  # Adjust if needed for slow startup

# Set up headless Chrome
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')

with webdriver.Chrome(options=chrome_options) as driver:
    driver.get(DASH_URL)
    time.sleep(5)  # Wait for dashboard to fully render
    # Optionally, interact with tabs here to export other views
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(driver.page_source)
    print(f'Exported dashboard to {OUTPUT_HTML}')

# Stop Dash app
proc.terminate()
print('Dash app stopped.')
