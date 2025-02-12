###############################################################################
# Script to scrape New Mexico voter registration data
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

BASE_URL = "https://www.sos.nm.gov/voting-and-elections/data-and-maps/voter-" \
    + "registration-statistics/"
STATE_TYPE = "NM/registration"

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
                                            "Voter Registration Data"))
    )

    pages = driver.find_elements(By.PARTIAL_LINK_TEXT, "Registration Data")
    page_htmls = []
    for page in pages:
        page_htmls.append(page.get_attribute("href"))

    for page_html in page_htmls:
        driver.get(page_html)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, 
            "Open File"))
        )
        # Can swap Precincts/Precints out for Statewide depending on what you're
        # interested in
        links = driver.find_elements(By.XPATH, 
            "//a[contains(@href, 'Precincts') or contains(@href, 'Precints')]")
        for link in links:
            helper.download_file(link.get_attribute("href"),
                                    STATE_TYPE, driver)
        driver.back()
except Exception as e:
    print(f"{STATE_TYPE} scraper failed to retrieve stats on " 
          + f"{helper.CURR_DATE}: {str(e)}")
finally:
    driver.quit()