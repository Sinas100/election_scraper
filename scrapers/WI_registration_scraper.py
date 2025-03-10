###############################################################################
# Script to scrape Wisconsin voter registration data
# Written by Sina Shaikh in 2024
###############################################################################

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

import helper

###############################################################################
# Global variables
###############################################################################

BASE_URL = "https://elections.wi.gov/statistics-data/voter-registration-" \
    + "statistics"
STATE_TYPE = "WI/registration"

###############################################################################
# Setup
###############################################################################

options = Options()

options.add_experimental_option("prefs", helper.setup_prefs(STATE_TYPE,
                                                             quarantine=True))
for arg in helper.SELENIUM_ARGUMENTS:
    options.add_argument(arg)

service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

###############################################################################
# Scrape
###############################################################################

try:        
    driver.get(BASE_URL)

    while True:

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "views-row"))
        )

        links = []
        links = driver.find_elements(By.PARTIAL_LINK_TEXT,
                                    " Voter Registration Statistics")
        hrefs = []
        link_texts =[]
        for link in links:
            hrefs.append(link.get_attribute("href"))
        for link in links:
            link_texts.append(link.text)

        for i in range(len(links)):
            driver.get(hrefs[i])
            try:
                element = driver.find_element(
                    By.XPATH,
                    "//a[(contains(@href, 'Ward') or contains(@href, 'ward')) "
                    "and (contains(@href, '.csv') or contains(@href, '.xls') "
                    "or contains(@href, '.xlsx'))]"
                )
                if element:
                    helper.download_and_name(element.get_attribute('href'),
                                            STATE_TYPE,
                                            driver,
                                            link_texts[i] + "."
                            + element.get_attribute('href').rsplit('.', 1)[-1])
            except NoSuchElementException:
                pass
            driver.back()
            helper.pause(10)
        try:
            driver.get(driver.find_element(By.XPATH,
                        "//a[@title='Go to next page']").get_attribute("href"))
        except NoSuchElementException:
            break
except Exception as e:
    print(f"{STATE_TYPE} scraper failed to retrieve stats on "
          + f"{helper.CURR_DATE}: {str(e)}")
finally:
    driver.quit()
