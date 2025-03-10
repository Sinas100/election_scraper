###############################################################################
# Script to scrape West Virginia voter registration data
# Written by Sina Shaikh in 2024
###############################################################################

from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import helper

###############################################################################
# Global variables
###############################################################################

MONTHS_ABB = helper.MONTHS_ABB
MONTHS_ABB.append("June")

BASE_URL = "https://sos.wv.gov/elections/Documents/VoterRegistrationTotals/"
STATE_TYPE = "WV/registration"

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
    for year in range(2016, datetime.today().year + 1):
        for month in MONTHS_ABB:   
            helper.download_file(f'{BASE_URL}/{year}/{month}{year}.pdf',
                                 STATE_TYPE, driver)
except Exception as e:
    print(f"{STATE_TYPE} scraper failed to retrieve stats on "
          + f"{helper.CURR_DATE}: {str(e)}")
finally:
    driver.quit()
