###############################################################################
# Script to help run scrapers
# Written by Sina Shaikh in 2025
###############################################################################

import os
from pathlib import Path
import sys
from datetime import date

###############################################################################
# Global variables
###############################################################################

BASE_PATH = os.path.join(Path(__file__).resolve().parents[1])
SCRAPER_PATH = os.path.join(BASE_PATH, "scrapers")
# EVERY_WEEK is default, EVERY_MORNING, EVERY_EVENING, and INACTIVE are 
# also accepted values
DOWNLOAD_FREQ_DICT = {"EVERY_MORNING": ["PA/early", 
                                        "PA/registration", 
                                        "PA/mail", 
                                        "MI/registration",
                                        "NC/registration",
                                        "SC/registration",
                                        "NC/early",
                                        "WI/early",
                                        "FL/registration",
                                        "TX/early"],
                        "EVERY_EVENING": ["FL/vbm"],
                        "INACTIVE": ["MT/registration", "RI/registration",
                                     "NV/registration", "AZ/registration"]}

###############################################################################
# Running
###############################################################################

files_to_run = []

time_of_day = sys.argv[1] if len(sys.argv) > 1 else "morning"

if time_of_day == "morning":
    if(date.today().weekday() == 0):
        inactive = []
        for state_type in DOWNLOAD_FREQ_DICT["INACTIVE"]:
            inactive.append(f"{state_type.replace('/', '_')}_scraper.py")
        inactive.extend(["helper.py", "SlackMessage.py"])
        for scraper in os.listdir(SCRAPER_PATH):
            if scraper.endswith(".py") and scraper not in inactive:
                files_to_run.append(scraper)
    else:    
        for state_type in DOWNLOAD_FREQ_DICT["EVERY_MORNING"]:
            files_to_run.append(
                f"{state_type.replace('/', '_')}_scraper.py")
elif time_of_day == "evening":
    for state_type in DOWNLOAD_FREQ_DICT["EVERY_EVENING"]:
        files_to_run.append(
            f"{state_type.replace('/', '_')}_scraper.py")

print(files_to_run)
print("Contents of SCRAPER_PATH:", os.listdir(SCRAPER_PATH))

for file in files_to_run: 
    os.system(f"python3  -W 'ignore' {os.path.join(SCRAPER_PATH, file)}" \
              " >> errors.txt 2>&1")

# # Only run this if you've set up SlackMessage.py
# os.system(f"python3 {os.path.join(SCRAPER_PATH, 'SlackMessage.py')}")