###############################################################################
# Script to scrape Kansas voter registration data
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

BASE_URL = "https://sos.ks.gov/elections/election-statistics.html"
STATE_TYPE = "KS/registration"

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
        EC.presence_of_element_located((By.ID, "vrCountyTab"))
    )

    driver.find_element(By.ID, "vrCountyTab").click()

    helper.pause(5)
    dropdowns = driver.find_elements(By.XPATH,
                                     "//button[contains(@class, " 
                                     + "'accordion-button collapsed')]")

    for dropdown in dropdowns:
        driver.execute_script("arguments[0].scrollIntoView(true);", dropdown)
        helper.pause(2)
        driver.execute_script("arguments[0].click();", dropdown)

    helper.pause(3)
    links = driver.find_elements(By.XPATH, "//a[contains(@href, "
                                 + "'Voter-Registration-Numbers-by-County')]")

    for link in links:
        helper.download_file(link.get_attribute("href"), STATE_TYPE, driver)
except Exception as e:
    print(f"{STATE_TYPE} scraper failed to retrieve stats on "
          + f"{helper.CURR_DATE}: {str(e)}")
finally:
    driver.quit()
