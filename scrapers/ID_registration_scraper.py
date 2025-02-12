###############################################################################
# Script to scrape Idaho voter registration data#
# Written by Sina Shaikh in 2024
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

BASE_URL = "https://sos.idaho.gov/elect/results/history.html"
STATE_TYPE = "ID/registration"

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

path = os.path.join(helper.BASE_PATH,
                    "election_scraper",
                    "data",
                    STATE_TYPE)
if(helper.DOWNLOAD_TYPE_DICT.get(STATE_TYPE, "ORIGINAL") != "ORIGINAL"):
    os.path.join(path, f"archive_{helper.CURR_DATE}")

try:
    driver.get(BASE_URL)

    WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH,
                                 "//table//a[not(contains(@href, 'Absentee')" +
                                 ") and not(contains(@href, 'absentee'))]"))
    )

    links = driver.find_elements(By.XPATH,
                                 "//table//a[not(contains(@href, 'Absentee')" +
                                 ") and not(contains(@href, 'absentee'))]")

    link_names = []
    link_hrefs = []
    for link in links:
        link_hrefs.append(link.get_attribute("href"))
        link_names.append(link.text)

    for i in range(0,len(link_names)):
        file_name = link_names[i]

        which_table = 0

        for year in range(2002, 2015):
                if str(year) in file_name:
                    which_table = 1
                    
        if ".xlsx" in link_hrefs[i]:
            helper.download_file(link_hrefs[i], STATE_TYPE, driver)
        elif not os.path.exists(os.path.join(path, f"{file_name}.csv")):
            helper.write_csv(link_hrefs[i], STATE_TYPE, driver,
                             which_table, file_name)
except Exception as e:
    print(f"{STATE_TYPE} scraper failed to retrieve stats on " 
          + f"{helper.CURR_DATE}: {str(e)}")
finally:
    driver.quit()