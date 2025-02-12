###############################################################################
# Script to scrape New Hampshire voter registration data
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

BASE_URL = "https://www.sos.nh.gov/party-registration-history-1970-2024"
STATE_TYPE = "NH/registration"

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

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "file--mime-applica" +\
                "tion-vnd-openxmlformats-officedocument-spreadsheetml-sheet"))
    )

    links = driver.find_elements(By.CLASS_NAME, "file--mime-applica" +\
                "tion-vnd-openxmlformats-officedocument-spreadsheetml-sheet")
    for link in links:
        helper.download_file(link.get_attribute("href"), STATE_TYPE, driver)
    
    helper.write_csv(BASE_URL, STATE_TYPE, driver, 0, "past_registration")

except Exception as e:
    print(f"{STATE_TYPE} scraper failed to retrieve stats on " 
          + f"{helper.CURR_DATE}: {str(e)}")
finally:
    driver.quit()
