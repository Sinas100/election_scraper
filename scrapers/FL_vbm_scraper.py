###############################################################################
# Script to scrape Florida vote by mail data
# Written by Sbaltz in 2024 refactored by Sina Shaikh in 2025
###############################################################################

import os

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

BASE_URL = "https://countyballotfiles.floridados.gov/VoteByMailEarlyVotingRep \
    orts/PublicStats"
STATE_TYPE = "FL/vbm"

STATE_PATH = os.path.join(helper.BASE_PATH,
                          "election_scraper",
                          "data",
                          STATE_TYPE)

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

    #First find all the links to download files, and download them
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Download File"))
    )
    links = driver.find_elements(By.PARTIAL_LINK_TEXT,
            "Download File")
    for link in links:
        helper.download_file(link.get_attribute("href"), STATE_TYPE, driver)

    #Also write down the data that they've put into the website, which may not
    # match the data that's in the files linked on the website
    table = driver.find_element('id', 'statewideTotal')
    webText = table.text
    with open(os.path.join(STATE_PATH,
                        f"{helper.CURR_DATE}_WebData.txt"), "w+") as f:
        f.write(webText)

    #Change the name of any files not yet in date format into the date format
    allfnames = os.listdir(STATE_PATH)
    for fname in allfnames:
        if 'EarlyVoted' in fname:
            os.rename(os.path.join(STATE_PATH, fname), 
                    os.path.join(STATE_PATH, f"{helper.CURR_DATE}_early.txt"))
        if 'VbmProvided' in fname:
            os.rename(os.path.join(STATE_PATH, fname), 
                    os.path.join(STATE_PATH, f"{helper.CURR_DATE}_provided.txt"))
        elif 'VbmVoted' in fname:
            os.rename(os.path.join(STATE_PATH, fname),
                    os.path.join(STATE_PATH, f"{helper.CURR_DATE}_voted.txt"))
except Exception as e:
    print(f"{STATE_TYPE} scraper failed to retrieve stats on " 
          + f"{helper.CURR_DATE}: {str(e)}")
finally:
    driver.quit()