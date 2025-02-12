###############################################################################
# Script to scrape Mississippi voter registration data
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

BASE_URL = "https://www.sos.ms.gov/elections-voting/active-voter-count-reports"
STATE_TYPE = "MS/registration"


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
        EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Voter Count"))
    )
    links = driver.find_elements(By.PARTIAL_LINK_TEXT, "Voter Count")
    link_hrefs = []

    for link in links:
        link_hrefs.append(link.get_attribute("href"))


    for link_href in link_hrefs:
        helper.download_file(link_href, STATE_TYPE, driver)

        if driver.current_url != BASE_URL:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Voter Count"))
            )
            more_links = driver.find_elements(By.PARTIAL_LINK_TEXT, "Voter Count")
            for m_link in more_links:
                helper.download_file(m_link.get_attribute("href"), 
                                     STATE_TYPE, driver)
            driver.back()
            helper.pause(2)
except Exception as e:
    print(f"{STATE_TYPE} scraper failed to retrieve stats on " 
          + f"{helper.CURR_DATE}: {str(e)}")
finally:
    driver.quit()
