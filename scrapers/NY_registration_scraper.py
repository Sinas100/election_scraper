###############################################################################
# Script to scrape New York voter registration data
# Written by Sina Shaikh in 2024
###############################################################################

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

import helper

###############################################################################
# Global variables
###############################################################################

BASE_URL = "https://elections.ny.gov/enrollment-election-district?page=0"
STATE_TYPE = "NY/registration"

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

    while True:

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//a[text()='Download']"))
        )

        links =[]
        links = driver.find_elements(By.XPATH, "//a[text()='Download']")

        for link in links:
            helper.download_file(link.get_attribute("href"), 
                                 STATE_TYPE, 
                                 driver)

        try:
            driver.get(driver.find_element(By.XPATH, 
                "//a[@title='Go to next page']").get_attribute("href"))
        except NoSuchElementException:
            break
except Exception as e:
    print(f"{STATE_TYPE} scraper failed to retrieve stats on " 
          + f"{helper.CURR_DATE}: {str(e)}")
finally:
    driver.quit()