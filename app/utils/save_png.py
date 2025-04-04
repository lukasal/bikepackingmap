from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import pathlib
import time

def save_png(map_file_path):
    filename = map_file_path.replace("html", "png")
    # Automatically manage ChromeDriver installation
    service = Service(ChromeDriverManager().install())
    
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Initialize the WebDriver
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(2560, 1740)
    
    
    # Open the HTML file with the Folium map
    map_file = pathlib.Path(map_file_path)
    file_url = map_file.resolve().as_uri()
    
    driver.get(file_url)  # Change the path to your actual file location
    time.sleep(5)  # Give it some time to load
    
    # Take a screenshot
    driver.save_screenshot(filename)
    
    # Close the browser
    driver.quit()
    
    return filename