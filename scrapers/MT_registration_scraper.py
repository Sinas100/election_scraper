###############################################################################
# Script to scrape Montana voter registration data
# Written by Sina Shaikh in 2024
###############################################################################

import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pyautogui
import shutil

import helper

###############################################################################
# Global variables
###############################################################################

BASE_URL = "https://sosmt.gov/elections/regvotercounty/"
STATE_TYPE = "MT/registration"

###############################################################################
# Setup
###############################################################################

options = Options()

options.add_experimental_option("prefs", helper.setup_prefs(STATE_TYPE, 
                                                            quarantine = True))
options.add_argument("--window-size=2560,1440")

service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

###############################################################################
# Scrape
###############################################################################

# I couldn't figure out a good way to do this headless! This is a sort of hacky
# workaround to the iframe
try:
    driver.get(BASE_URL)

    helper.pause(5)

    pyautogui.moveTo(300, 720, duration=1)
    pyautogui.scroll(-10)
    helper.pause(20)
    pyautogui.moveTo(1300, 850, duration=1)
    pyautogui.leftClick()
    helper.pause(5)
    pyautogui.moveTo(1000, 650, duration=1)
    pyautogui.leftClick()

    helper.pause(5)

    os.rename(os.path.join(helper.get_path(STATE_TYPE, True), 
                           'County Data.xlsx'), 
              os.path.join(helper.get_path(STATE_TYPE, False), 
                           f"{helper.CURR_DATE}.xlsx"))

    helper.pause(5)
    shutil.rmtree(helper.get_path(STATE_TYPE, True))

except Exception as e:
    print(f"{STATE_TYPE} scraper failed to retrieve stats on " 
          + f"{helper.CURR_DATE}: {str(e)}")
finally:
    driver.quit()