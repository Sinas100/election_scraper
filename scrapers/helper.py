###############################################################################
# Script to help scrape data from state websites
# Written by Sina Shaikh in 2025
###############################################################################

import os
import pathlib
from pathlib import Path
import shutil
import csv
import time
from datetime import datetime
from datetime import date

import numpy as np
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import requests

###############################################################################
# Global variables
###############################################################################

# Can be set to "ORIGINAL", "OVERWRITE", or "SAVE_COPY" (The states will be
# treated as ORIGINAL by default). Be extremely careful with OVERWRITE!!!
DOWNLOAD_TYPE_DICT = {"NC/registration": "OVERWRITE",
                      "PA/early": "OVERWRITE",
                      "TX/early": "SAVE_COPY"}
# Global break time
BREAK_AFTER = 500
# The folder in which election_scraper is located
BASE_PATH = Path(__file__).resolve().parents[2]
# Headless can be disabled and you can run additional scripts if a GUI is
# available
SELENIUM_ARGUMENTS = [
    "--headless", 
    "--disable-gpu", 
    "--no-sandbox", 
    "--start-maximized", 
    "--disable-infobars", 
    "--disable-extensions"
]

MONTHS = [date(2024, i, 1).strftime('%B') for i in range(1, 13)]
MONTHS_ABB = [date(2024, i, 1).strftime('%b') for i in range(1, 13)]
CURR_DATE = datetime.today().strftime("%Y%m%d")

###############################################################################
# Global functions
# Be careful changing these!!
###############################################################################

# Random pause time
def pause(least):
    least = max(least, 2)
    time.sleep(max(0,np.random.randint(least-1,least)+np.random.uniform(0,1)))

# Set preferences for scraper, depending on whether files need to be put into
# quarantine folder and the download_type
def setup_prefs(STATE_TYPE, quarantine = False):
    download_type = DOWNLOAD_TYPE_DICT.get(STATE_TYPE, "ORIGINAL")
    state_path = os.path.join(BASE_PATH,
                              "election_scraper",
                              "data",
                              STATE_TYPE)

    if download_type == "ORIGINAL":
        download_dir = state_path
        if quarantine:
            download_dir = os.path.join(download_dir, "quarantine")

        pathlib.Path(download_dir).mkdir(parents=True, exist_ok=True)

        prefs = {
        "plugins.always_open_pdf_externally": True,  # Download PDF, don't open
        "download.default_directory": download_dir, 
        "download.prompt_for_download": False, 
        "profile.content_settings.exceptions.automatic_downloads.*.setting": 1, 
        }
    else:
        download_dir = os.path.join(state_path, f"archive_{CURR_DATE}")
        if quarantine:
            download_dir = os.path.join(download_dir, "quarantine")
        pathlib.Path(download_dir).mkdir(parents=True, exist_ok=True)
        prefs = {
            "plugins.always_open_pdf_externally": True,  # Download PDF, don't
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "profile.content_settings.exceptions.\
                automatic_downloads.*.setting": 1,

        }
    return prefs

def get_path(STATE_TYPE, quarantine):
    download_type = DOWNLOAD_TYPE_DICT.get(STATE_TYPE, "ORIGINAL")
    state_path = os.path.join(BASE_PATH,
                              "election_scraper",
                              "data",
                              STATE_TYPE)
    download_dir = state_path
    if download_type == "ORIGINAL":
        if quarantine:
            download_dir = os.path.join(download_dir, "quarantine")
    else:
        download_dir = os.path.join(state_path, f"archive_{CURR_DATE}")
        if quarantine:
            download_dir = os.path.join(download_dir, "quarantine")
    return download_dir

# Helper function for OVERWRITE download setting
def wipe_previous_days_if_overwrite(download_type, state_path):
    if download_type == "OVERWRITE":
        for dir_or_file_name in os.listdir(state_path):
            full_path = os.path.join(state_path, dir_or_file_name)
            if (full_path != os.path.join(state_path,
                        f"archive_{CURR_DATE}")) and os.path.isdir(full_path):
                shutil.rmtree(os.path.join(state_path,
                                            dir_or_file_name))
            elif not os.path.isdir(full_path):
                os.remove(full_path)

# Stalls the program while file is still being downloaded
def pause_while_downloading(full_path):
    pause(2)
    downloading = True
    total_wait = 0
    while downloading and (total_wait <= BREAK_AFTER):
        downloading = False
        for file_name in os.listdir(full_path):
            if file_name.endswith(".crdownload"):
                downloading = True
                pause(5)
                total_wait += 5
                break

# Downloads file from url
def download_file(url, STATE_TYPE, driver):
    download_type = DOWNLOAD_TYPE_DICT.get(STATE_TYPE, "ORIGINAL")
    state_path = os.path.join(BASE_PATH, "election_scraper",
                               "data",
                               STATE_TYPE)

    # Remove all previous days if overwrite
    wipe_previous_days_if_overwrite(download_type, state_path)

    if download_type != "ORIGINAL":
        state_path = os.path.join(state_path, f"archive_{CURR_DATE}")

    # Remove .crdownload files
    for file_name in os.listdir(state_path):
        if file_name.endswith(".crdownload"):
            os.remove(os.path.join(state_path, file_name))

    file_name = url.split("/")[-1].replace('%20', ' ')
    file_path = os.path.join(state_path, file_name)

    if not os.path.exists(file_path):
        if ".txt" in file_name:
            with open(file_path, 'wb') as file:
                file.write(requests.get(url, timeout = BREAK_AFTER).content)
        else:
            driver.get(url)
            pause(2)

    pause_while_downloading(state_path)

# Downloads table as a csv on a given webpage
def write_csv(url, STATE_TYPE, driver, which_table, file_name,
              already_on_url = False):
    download_type = DOWNLOAD_TYPE_DICT.get(STATE_TYPE, "ORIGINAL")
    state_path = os.path.join(BASE_PATH, "election_scraper",
                               "data",
                               STATE_TYPE)

    # Remove all previous days
    wipe_previous_days_if_overwrite(download_type, state_path)

    if download_type != "ORIGINAL":
        state_path = os.path.join(state_path, f"archive_{CURR_DATE}")

    if not already_on_url:
        driver.get(url)

    table = driver.find_elements(By.TAG_NAME, 'table')[which_table]

    table_data = []

    headers = [header.text.strip() for header in table.find_element(
        By.TAG_NAME, 'tr').find_elements(By.TAG_NAME, 'th')]
    table_data.append(headers)

    rows = table.find_elements(By.TAG_NAME, 'tr')

    for i, row in enumerate(rows):
        cells = []

        if i > 0:
            try:
                cells.append(row.find_element(By.TAG_NAME, 'th'))
            except NoSuchElementException:
                pass

        cells.extend(row.find_elements(By.TAG_NAME, 'td'))
        row_data = [cell.text.strip() for cell in cells]

        if row_data:
            table_data.append(row_data)

    if not file_name.endswith(".csv"):
        file_name = f"{file_name}.csv"

    with open(os.path.join(state_path, file_name), 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(table_data)

    if not already_on_url:
        pause(1)
        driver.back()
        pause(1)

# Downloads file from a given url to a quarantine folder, renames it, and moves
# it into the base folder before removing the quarantine folder.
def download_and_name(url, STATE_TYPE, driver, new_name):
    download_type = DOWNLOAD_TYPE_DICT.get(STATE_TYPE, "ORIGINAL")
    state_path = os.path.join(BASE_PATH,
                              "election_scraper",
                              "data",
                              STATE_TYPE)

    # Remove all previous days
    wipe_previous_days_if_overwrite(download_type, state_path)

    if download_type != "ORIGINAL":
        state_path = os.path.join(state_path, f"archive_{CURR_DATE}")

    quarantine_path = os.path.join(state_path, "quarantine")

    if os.path.isdir(quarantine_path):
        shutil.rmtree(quarantine_path)
    pathlib.Path(quarantine_path).mkdir(parents=True, exist_ok=True)

    file_path = os.path.join(state_path, new_name)

    if not os.path.exists(file_path):
        if ".txt" in new_name:
            with open(file_path, 'wb') as file:
                file.write(requests.get(url, timeout=BREAK_AFTER).content)
        else:
            driver.get(url)
            pause(2)

    pause_while_downloading(quarantine_path)

    while len(os.listdir(quarantine_path)):
        for file in os.listdir(quarantine_path):
            os.rename(os.path.join(quarantine_path, file), 
                    os.path.join(state_path, new_name))
        pause(1)

    shutil.rmtree(quarantine_path)
