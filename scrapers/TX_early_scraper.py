##############################################################################
# Script to scrape the Texas early voting data
# Written by Samuel Baltz in 2024 refactored by Sina Shaikh in 2025 
###############################################################################

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import helper

###############################################################################
# Global variables and setup
###############################################################################
#List the elections of interest
elections = ["2024 NOVEMBER 5TH GENERAL ELECTION"]

BASE_URL = "https://earlyvoting.texas-election.com/Elections/getElectionEVDa" \
    + "tes.do"
STATE_TYPE = "TX/early"

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
# Scraping loop
###############################################################################
try:
    for i in range(len(elections)):
        currElec = elections[i]

        driver.get(BASE_URL)

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "idElection"))
        )

        #Populate the dropdown menu with the election of interest
        election = Select(driver.find_element(By.ID,"idElection"))
        election.select_by_visible_text(currElec)
        #Click the submit button
        driver.find_element('xpath',
                '//button[normalize-space()="Submit"]').click()

        #Get a list of the available dates
        dates = []
        dateMenu = Select(driver.find_element(By.NAME, "selectedDate"))
        dateObjs = dateMenu.options
        for j in range(len(dateObjs)):
            textDate = dateObjs[j].text
            dates.append(textDate)
        #Drop the first date, which is a header
        dates = dates[1:]

        helper.pause(2)

        #Now for every date, grab the full early voting data from that date
        for date in dates:
            dateMenu.select_by_visible_text(date)
            driver.find_element('xpath',
                    '//button[normalize-space()="Submit"]').click()
            helper.write_csv("", STATE_TYPE, driver, 0, 
                            currElec.replace(' ', '-') + '_' + date,
                            already_on_url=True)
            #Return to the page that has the dates dropdown menu
            driver.back()
            dateMenu = Select(driver.find_element(By.NAME, "selectedDate"))
            helper.pause(1)
except Exception as e:
    print(f"{STATE_TYPE} scraper failed to retrieve stats on " 
          + f"{helper.CURR_DATE}: {str(e)}")
finally:
    driver.quit()