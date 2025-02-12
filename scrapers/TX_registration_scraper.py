###############################################################################
# Script to scrape Texas voter registration data
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

BASE_URL = "https://www.sos.texas.gov/elections/historical/vrfig.shtml"
STATE_TYPE = "TX/registration"


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
                                        "//a[contains(@href, 'mar')]"))
    )

    links = []

    for month in ['January', 'March', 'November']:
        temp = driver.find_elements(By.PARTIAL_LINK_TEXT, month)
        for element in temp:
            links.append(element.get_attribute('href'))

    for link in links:
        driver.get(link)
        helper.write_csv(link, STATE_TYPE, driver, 0,
                        driver.find_element(By.TAG_NAME, 'h1').text,
                        already_on_url=True)
        driver.back()
        helper.pause(1)
except Exception as e:
    print(f"{STATE_TYPE} scraper failed to retrieve stats on " 
          + f"{helper.CURR_DATE}: {str(e)}")
finally:
    driver.quit()
