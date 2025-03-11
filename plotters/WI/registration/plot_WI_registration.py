###############################################################################
# Script to plot Wisconsin registration data
# Written by Sina Shaikh in 2025
###############################################################################

import sys
import os
from datetime import datetime

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                              "../..")))
from plotting_helper import *

###############################################################################
# Global variables and functions
###############################################################################

# Define the state and its abbreviation
STATE = 'Wisconsin'
STATE_ABB = 'WI/registration'
DATA_SOURCE = "Wisconsin Elections Commission, elections.wi.gov"

# Define the election years and their corresponding election dates
ELECTION_DATES = {
    2023: datetime(2023, 4, 4),
    2025: datetime(2025, 4, 1)
}

# Path to election_scraper
PLOT_DIR = os.path.join(ROOT, f'plots/{STATE_ABB}/')

###############################################################################
# Read in data and create plots
###############################################################################

folder = os.path.join(ROOT, f"plotters/{STATE_ABB}/plot_data")
csv_files = sorted(os.listdir(folder), reverse=True)
ad = pd.read_csv(os.path.join(folder, csv_files[0]))

os.makedirs(PLOT_DIR, exist_ok=True)

plot_absolute("REGISTRATION",
              ad,
              PLOT_DIR,
              STATE,
              DATA_SOURCE,
              'registered_voters',
              6,
              2)
