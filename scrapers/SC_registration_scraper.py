###############################################################################
# Script to scrape South Carolina voter registration data
# Written by Sina Shaikh in 2024
###############################################################################

import os
import shutil

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

import helper

###############################################################################
# Global variables
###############################################################################

BASE_URL = "https://vrems.scvotes.sc.gov/Statistics/CountyAndPrecinct"
STATE_TYPE = "SC/registration"

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
            EC.presence_of_element_located((By.ID, "Demographic"))
        )

    county_dropdown = Select(driver.find_element(By.ID, "CountySID"))
    demographic_dropdown = Select(driver.find_element(By.ID, "Demographic"))

    for county in county_dropdown.options[1:]:
        for demographic in demographic_dropdown.options[1:]:
            county_dropdown.select_by_visible_text(county.text)
            demographic_dropdown.select_by_visible_text(demographic.text)
            driver.find_element(By.ID, "viewResults").click()
            helper.pause(1)
            driver.find_element(By.PARTIAL_LINK_TEXT, "Export").click()

            helper.pause_while_downloading(helper.get_path(STATE_TYPE, False))

            # Move files out of quarantine and name
            for file in os.listdir(helper.get_path(STATE_TYPE, True)):
                os.rename(
                    os.path.join(helper.get_path(STATE_TYPE, True), file),
                    os.path.join(helper.get_path(STATE_TYPE, False),
                  f"{county.text}_{demographic.text}_{helper.CURR_DATE}.xlsx"))
except Exception as e:
    print(f"{STATE_TYPE} scraper failed to retrieve stats on "
          + f"{helper.CURR_DATE}: {str(e)}")
finally:
    shutil.rmtree(helper.get_path(STATE_TYPE, True))
    driver.quit()
