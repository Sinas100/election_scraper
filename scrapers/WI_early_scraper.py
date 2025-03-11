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

BASE_URL = "https://elections.wi.gov/statistics-data/absentee-statistics"
STATE_TYPE = "WI/early"

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

        links =[]
        links = links + (driver.find_elements(By.PARTIAL_LINK_TEXT, 
                                            "2024 General Election"))
                    
        for link in links:
            link.click()
            date_updated = driver.find_element(By.TAG_NAME,
                                        'time').get_attribute('datetime')[:10]
            if driver.find_elements(By.PARTIAL_LINK_TEXT, "Muni"):
                days = driver.find_elements(By.PARTIAL_LINK_TEXT, "Muni")
                for day in days:
                    if(len(days) > 1 or "2024" in date_updated):
                        helper.download_and_name(day.get_attribute("href"), 
                                        STATE_TYPE, driver, day.text + ".csv")
                    else:
                        # This path exists for scraping past years
                        helper.download_and_name(day.get_attribute("href"), 
                                                STATE_TYPE, driver, 
                                                date_updated + ".csv")
            else:
                helper.write_csv("", STATE_TYPE, driver, 0, date_updated,
                                already_on_url=True)

            driver.back()
            helper.pause(15)

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
