###############################################################################
# Script to scrape Oregon voter registration data
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

BASE_URL = "https://sos.oregon.gov/elections/Pages/electionsstatistics.aspx"
STATE_TYPE = "OR/registration"

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

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "accordion-toggle"))
    )

    dropdowns = driver.find_elements(By.CLASS_NAME, "accordion-toggle")

    saved_hrefs = []
    monthly_hrefs = []

    # Click each dropdown and collect the links
    for dropdown in dropdowns:
        driver.execute_script("arguments[0].scrollIntoView(true);", dropdown)
        helper.pause(2)
        driver.execute_script("arguments[0].click();", dropdown)
        
        # Extract the year from the href attribute of the dropdown
        year = dropdown.get_attribute('href').split('#')[-1]
        helper.pause(3)
        # Collect links that contain the specific year in their partial link
        year_links = driver.find_elements(By.PARTIAL_LINK_TEXT, " "+str(year))
        for year_link in year_links:
            href = year_link.get_attribute("href")
            if ".pdf" in href:
                helper.download_file(href, STATE_TYPE, driver)
            else:
                monthly_hrefs.append(href)
        
    for year in range(2001, 2018 + 1):
        year_links = driver.find_elements(By.PARTIAL_LINK_TEXT, str(year))
        for year_link in year_links:
            href = year_link.get_attribute("href")
            saved_hrefs.append(href)

    # Process saved hrefs
    for href in saved_hrefs:
        driver.get(href)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT,
                                            "Voter Registration"))
        )

        voter_registration_links = driver.find_elements(By.PARTIAL_LINK_TEXT,
                                                         "Voter Registration")
        for vr_link in voter_registration_links:
            monthly_hrefs.append(vr_link.get_attribute("href"))

    for page in monthly_hrefs:
        driver.get(page)
        view_download_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "btn.dropdown-toggle"))
        )
        view_download_button.click()
        helper.pause(1)
        download = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Download"))
        )
        download.click()
except Exception as e:
    print(f"{STATE_TYPE} scraper failed to retrieve stats on "
          + f"{helper.CURR_DATE}: {str(e)}")
finally:
    driver.quit()
