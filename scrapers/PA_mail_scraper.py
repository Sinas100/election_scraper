###############################################################################
# Script to scrape Pennsylvania mail in ballot data
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

BASE_URL = "https://www.pavoterservices.pa.gov/2024%20Primary%20Daily%20Mail" \
    + "%20Ballot%20Report.xlsx"
STATE_TYPE = "PA/mail"

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
                             helper.CURR_DATE + ".xlsx")
except Exception as e:
    print(f"{STATE_TYPE} scraper failed to retrieve stats on "
          + f"{helper.CURR_DATE}: {str(e)}")
finally:
    driver.quit()
