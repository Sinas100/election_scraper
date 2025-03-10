###############################################################################
# Script to scrape Virginia voter registration data
# Written by Sina Shaikh in 2024
###############################################################################

import time

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

BASE_URL = "https://www.elections.virginia.gov/resultsreports/registration-" \
    + "statistics/"
STATE_TYPE = "VA/registration"

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
        EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "2024"))
    )

    links = []

    for year in range(2003, time.localtime().tm_year + 1):
        links.append(driver.find_element(
            By.LINK_TEXT, str(year)).get_attribute("href"))

    for link in links:
        driver.get(link)
        files = driver.find_elements(By.XPATH, (
        "//a[contains(@href, '.csv') or contains(@href, '.pdf')]"
        "[contains(translate(@href, 'Congressional', 'congressional'), " \
            + "'congressional')]"
        ))

        for file in files:
            helper.download_file(file.get_attribute("href"),
                                    STATE_TYPE,
                                    driver)
except Exception as e:
    print(f"{STATE_TYPE} scraper failed to retrieve stats on "
          + f"{helper.CURR_DATE}: {str(e)}")
finally:
    driver.quit()
