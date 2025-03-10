###############################################################################
# Script to scrape Rhode Island voter registration data
# Written by Sina Shaikh in 2024
# This may no longer work if anything on the page changes, this is not a good
# scraper but is an example of how you can scrape a website with no useful
# html
###############################################################################

import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pyperclip
import pyautogui

import helper

###############################################################################
# Global variables
###############################################################################

BASE_URL = "https://datahub.sos.ri.gov/RegisteredVoter.aspx"
STATE_TYPE = "RI/registration"

PATH = helper.get_path(STATE_TYPE, False)

###############################################################################
# Setup
###############################################################################

options = Options()

options.add_experimental_option("prefs", helper.setup_prefs(STATE_TYPE))
options.add_argument("--window-size=2560,1440")

service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

###############################################################################
# Scrape
###############################################################################


try:
    driver.get(BASE_URL)
    helper.pause(5)

    pyautogui.moveTo(680, 650, duration=1)
    pyautogui.leftClick()
    pyautogui.rightClick()
    pyautogui.moveTo(680, 600, duration=1)
    pyautogui.moveTo(900, 600, duration=1)
    pyautogui.moveTo(900, 625, duration=1)

    pyautogui.leftClick()

    s = pyperclip.paste()
    with open(os.path.join(PATH, helper.CURR_DATE+'_dem.txt'), 'w') as g:
        g.write(s)

    pyautogui.moveTo(950, 600, duration=1)
    pyautogui.leftClick()
    pyautogui.rightClick()
    pyautogui.moveTo(950, 600, duration=1)
    pyautogui.moveTo(1270, 600, duration=1)
    pyautogui.moveTo(1270, 625, duration=1)

    pyautogui.leftClick()

    s = pyperclip.paste()
    with open(os.path.join(PATH, helper.CURR_DATE+'_rep.txt'), 'w') as g:
        g.write(s)

    pyautogui.moveTo(1050, 590, duration=1)
    pyautogui.leftClick()
    pyautogui.rightClick()
    pyautogui.moveTo(1050, 600, duration=1)
    pyautogui.moveTo(1270, 600, duration=1)
    pyautogui.moveTo(1270, 625, duration=1)

    pyautogui.leftClick()

    s = pyperclip.paste()

    with open(os.path.join(PATH, helper.CURR_DATE+'_unaff.txt'), 'w') as g:
        g.write(s)

except Exception as e:
    print(f"{STATE_TYPE} scraper failed to retrieve stats on "
          + f"{helper.CURR_DATE}: {str(e)}")
finally:
    driver.quit()
