###############################################################################
# Script to scrape Pennsylvania voter registration data
# Written by Sina Shaikh in 2024
###############################################################################

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import helper

###############################################################################
# Global variables
###############################################################################

BASE_URL = "https://www.pavoterservices.pa.gov/AVR-Party-Breakdown.pdf"
STATE_TYPE = "PA/avr"

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
    helper.download_and_name(BASE_URL, STATE_TYPE, driver,
                             helper.CURR_DATE + ".pdf")
except Exception as e:
    print(f"{STATE_TYPE} scraper failed to retrieve stats on "
          + f"{helper.CURR_DATE}: {str(e)}")
finally:
    driver.quit()
