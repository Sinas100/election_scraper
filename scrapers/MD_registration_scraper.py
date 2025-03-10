###############################################################################
# Script to scrape Maryland voter registration data
# Written by Sina Shaikh in 2024
###############################################################################

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

BASE_URL = "https://elections.maryland.gov/voter_registration/stats.html"
STATE_TYPE = "MD/registration"

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
        EC.presence_of_element_located((By.PARTIAL_LINK_TEXT,
                                "Monthly Voter Registration Activity Reports"))
    )

    driver.find_element(By.PARTIAL_LINK_TEXT,
                        "Monthly Voter Registration Activity Reports").click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "January"))
    )

    links =[]
    for month in helper.MONTHS:
        links += driver.find_elements(By.PARTIAL_LINK_TEXT, month)

    for link in links:
        helper.download_file(link.get_attribute("href"), STATE_TYPE, driver)
except Exception as e:
    print(f"{STATE_TYPE} scraper failed to retrieve stats on "
          + f"{helper.CURR_DATE}: {str(e)}")
finally:
    driver.quit()
