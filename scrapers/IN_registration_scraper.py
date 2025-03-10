###############################################################################
# Script to scrape Indiana voter registration data
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

BASE_URL = "https://www.in.gov/sos/elections/voter-information/register-to-" \
+ "vote/voter-registration-and-turnout-statistics/"
STATE_TYPE = "IN/registration"


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
    helper.pause(1)

    WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Data"))
    )

    links = driver.find_elements(By.PARTIAL_LINK_TEXT, "Data")
    hrefs =[]

    for link in links:
        hrefs.append(link.get_attribute("href"))

    for href in hrefs:
        if ".pdf" in href or ".PDF"  in href:
            helper.download_file(href, STATE_TYPE, driver)
        else:
            helper.write_csv(href, STATE_TYPE, driver, 0, href.split("/")[-1])
except Exception as e:
    print(f"{STATE_TYPE} scraper failed to retrieve stats on "
          + f"{helper.CURR_DATE}: {str(e)}")
finally:
    driver.quit()
