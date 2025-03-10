###############################################################################
# Script to scrape Oklahoma voter registration data
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

BASE_URL = "https://oklahoma.gov/elections/voter-registration/voter-" \
    + "registration-statistics/voter-registration-statistics-archive.html"
STATE_TYPE = "OK/registration"

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
        EC.presence_of_element_located((By.CLASS_NAME,
                                         "cmp-accordion__header"))
    )

    dropdowns = driver.find_elements(By.CLASS_NAME, "cmp-accordion__header")

    # Click each dropdown and collect the links
    for dropdown in dropdowns:

        dropdown.click()
        helper.pause(3)

        # Collect links that contain the specific year in their partial link
        year_links = driver.find_elements(By.XPATH, "//a[contains(text()," \
                        + "'county') and not(contains(text(), 'Monthly'))]")
        for year_link in year_links:
            helper.download_file(year_link.get_attribute("href"), STATE_TYPE,
                                 driver)
        
        month_links = driver.find_elements(By.PARTIAL_LINK_TEXT, "Monthly")
        month_hrefs = []

        for month_link in month_links:
            month_hrefs.append(month_link.get_attribute("href"))

        for href in month_hrefs:
            helper.download_file(href, STATE_TYPE, driver)
            helper.pause(5)
            links = driver.find_elements(By.PARTIAL_LINK_TEXT,
                                         "Voter registration ")
            for link in links:
                helper.download_file(link.get_attribute("href"), STATE_TYPE,
                                     driver)
            driver.back()
except Exception as e:
    print(f"{STATE_TYPE} scraper failed to retrieve stats on "
          + f"{helper.CURR_DATE}: {str(e)}")
finally:
    driver.quit()
