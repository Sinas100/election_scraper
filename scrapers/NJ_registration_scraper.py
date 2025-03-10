###############################################################################
# Script to scrape New Jersey voter registration data
# Written by Sina Shaikh in 2024
###############################################################################

from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import helper

###############################################################################
# Global variables
###############################################################################

BASE_URL = "https://www.nj.gov/state/elections/election-information-" \
    + "ballots-cast.shtml"
STATE_TYPE = "NJ/registration/"

###############################################################################
# Setup
###############################################################################

options = Options()

options.add_experimental_option("prefs", helper.setup_prefs(STATE_TYPE))
for arg in helper.SELENIUM_ARGUMENTS:
    options.add_argument(arg)

service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

###############################################################################
# Scrape
###############################################################################

try:
    driver.get(BASE_URL)

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "card-header"))
    )

    dropdowns = driver.find_elements(By.CLASS_NAME, "card-header")

    current_links = driver.find_elements(By.PARTIAL_LINK_TEXT,
                                         str(datetime.now().year)+" ")

    for link in current_links:
        helper.download_file(link.get_attribute("href"), STATE_TYPE, driver)

    # Click each dropdown and collect the links
    for dropdown in dropdowns:
        dropdown.click()

        # Extract the year from the href attribute of the dropdown
        year = dropdown.text.split(' ')[0]
        helper.pause(3)
        # Collect links that contain the specific year in their partial link
        year_links = driver.find_elements(By.PARTIAL_LINK_TEXT, str(year)+ " ")
        for year_link in year_links:
            helper.download_file(year_link.get_attribute("href"),
                                 STATE_TYPE, driver)
except Exception as e:
    print(f"{STATE_TYPE} scraper failed to retrieve stats on "
          + f"{helper.CURR_DATE}: {str(e)}")
finally:
    driver.quit()
