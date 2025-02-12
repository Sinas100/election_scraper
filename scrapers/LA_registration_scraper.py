###############################################################################
# Script to scrape Louisiana voter registration data
# Written by Sina Shaikh in 2024
###############################################################################

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

import helper

###############################################################################
# Global variables
###############################################################################

BASE_URL = "https://www.sos.la.gov/ElectionsAndVoting/Pages/Registration" 
+ "StatisticsParish.aspx"
STATE_TYPE = "LA/registration"

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
    driver.switch_to.frame("QueryStringPageViewer_ctl00$ctl34$g_04665f4c_f181" 
                           + "_417e_a8cf_884f1b8fa02e")

    WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "cboYear"))
    )

    year_dropdown = Select(driver.find_element(By.ID, "cboYear"))

    year_texts = []

    for year in year_dropdown.options:
        year_texts.append(year.text)

    for year_text in year_texts:
        driver.get(BASE_URL)
        driver.switch_to.frame("QueryStringPageViewer_ctl00$ctl34$g_04665f4c_"
                               + "f181_417e_a8cf_884f1b8fa02e")
        year_dropdown = Select(driver.find_element(By.ID, "cboYear"))
        year_dropdown.select_by_visible_text(year_text)

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "xls"))
        )

        links = driver.find_elements(By.PARTIAL_LINK_TEXT, "xls")

        link_hrefs = []

        for link in links:
            link_hrefs.append(link.get_attribute("href"))

        for link_href in link_hrefs:
            helper.download_file(link_href, STATE_TYPE, driver)
except Exception as e:
    print(f"{STATE_TYPE} scraper failed to retrieve stats on " 
          + f"{helper.CURR_DATE}: {str(e)}")
finally:
    driver.quit()