###############################################################################
# Script to scrape Maine voter registration data
# Note further information is available at the BASE_URL
# Written by Sina Shaikh in 2024
###############################################################################

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

import helper

###############################################################################
# Global variables
###############################################################################

BASE_URL = "https://www.maine.gov/sos/cec/elec/data/prevregandenroll.html"
STATE_TYPE = "ME/registration"

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
                                "Statewide Registered and Enrolled Data File"))
    )

    li_elements = driver.find_elements(By.XPATH, "//li[a[contains(text()," 
                        + "'Statewide Registered and Enrolled Data File')]]")


    for li in li_elements:
        # Find the closest preceding <p> element for this <li>
        preceding_p = li.find_element(By.XPATH, "preceding::p[1]").text.strip()
        
        links = li.find_elements(By.TAG_NAME, "a")

        for link in links:
            href = link.get_attribute("href")
            if href and (".html" not in href) and (".pdf" not in href):
                new_name = (f"{preceding_p} - {li.text}"
                            + f"{os.path.splitext(href)[1]}").replace('/', '')
                helper.download_and_name(link.get_attribute("href"), 
                                                    STATE_TYPE, 
                                                    driver,
                                                    new_name)
except Exception as e:
    print(f"{STATE_TYPE} scraper failed to retrieve stats on " 
          + f"{helper.CURR_DATE}: {str(e)}")
finally:
    driver.quit()