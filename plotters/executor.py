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
PLOTTER_PATH = os.path.join(BASE_PATH, "plotters")

# There is no default, EVERY_WEEK, EVERY_MORNING, EVERY_EVENING, and INACTIVE 
# are accepted values
DOWNLOAD_FREQ_DICT = {"EVERY_MORNING": ["WI/clean_WI_registration.py",
                                        "WI/plot_WI_registration.py"],
                      "INACTIVE": ["NC/clean_NC_early.py",
                                   "NC/plot_NC_early.py"]}

###############################################################################
# Running
###############################################################################

files_to_run = []

time_of_day = sys.argv[1] if len(sys.argv) > 1 else "morning"

if time_of_day == "morning":
    if(date.today().weekday() == 0):
        for state_type in DOWNLOAD_FREQ_DICT["EVERY_WEEK"]:
            files_to_run.append(state_type)
    for state_type in DOWNLOAD_FREQ_DICT["EVERY_MORNING"]:
        files_to_run.append(state_type)
elif time_of_day == "evening":
    for state_type in DOWNLOAD_FREQ_DICT["EVERY_EVENING"]:
        files_to_run.append(state_type)

for file in files_to_run:
    os.system(f"python3  -W 'ignore' {os.path.join(PLOTTER_PATH, file)}" \
              " >> errors.txt 2>&1")
