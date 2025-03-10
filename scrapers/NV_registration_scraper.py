###############################################################################
# Script to scrape Nevada voter registration data
# Written by Sina Shaikh in 2024
#
# This script no longer works!!! There is a popup captcha which makes this
# script crash, I've left it in here for posterity in case they remove the
# captcha
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

BASE_URL = "https://www.nvsos.gov/sos/elections/voters/voter-registration-" \
    + "statistics/"
STATE_TYPE = "NV/registration"

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
        EC.presence_of_element_located((By.XPATH,
                            "//a[contains(@href, 'showpublisheddocument')]"))
    )

    links = driver.find_elements(By.XPATH,
                            "//a[contains(@href, 'showpublisheddocument')]")

    for link in links:
        helper.download_file(link.get_attribute("href"), STATE_TYPE, driver)

    for year in range(2000, datetime.today().year):
        driver.get(BASE_URL+year+"-statistics/-fsiteid-1")

        more_links = driver.find_elements(By.XPATH,
                    "//table[1]").find_elements(By.PARTIAL_LINK_TEXT, "Excel")

        for link in more_links:
            helper.download_file(link.get_attribute("href"),
                                 STATE_TYPE, driver)
except Exception as e:
    print(f"{STATE_TYPE} scraper failed to retrieve stats on "
          + f"{helper.CURR_DATE}: {str(e)}")
finally:
    driver.quit()
