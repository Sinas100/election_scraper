###############################################################################
# Script to scrape Pennsylvania Early Data
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
####################################################################s###########

BASE_URL = "https://copaftp.state.pa.us/Web/Account/Login.htm"
STATE_TYPE = "PA/early"


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
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    helper.pause(3)

    driver.find_element(By.ID, "username").send_keys("ST-DOSFTP5A")
    driver.find_element(By.ID, "password").send_keys("JQTxnEV4")
    driver.find_element(By.ID, "loginSubmit").click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "mat-checkbox-1-input"))
    )

    helper.pause(2)

    driver.find_elements(By.CSS_SELECTOR,
                         ".mat-checkbox-inner-container")[2].click()
    helper.pause(2)
    driver.find_elements(By.CSS_SELECTOR,
                         ".mat-checkbox-inner-container")[3].click()
    helper.pause(2)

    driver.find_element(By.XPATH, "//span[text()='Download']").click()

    helper.pause_while_downloading(helper.get_path(STATE_TYPE, False))

except Exception as e:
    print(f"{STATE_TYPE} scraper failed to retrieve stats on "
          + f"{helper.CURR_DATE}: {str(e)}")
finally:
    driver.quit()
