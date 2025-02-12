###############################################################################
# Script to plot North Carolina early voting data
# Written by sbaltz in 2024, refactored in 2025 by Sina Shaikh
###############################################################################

import sys
import os
import pandas as pd
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from plotting_helper import *

###############################################################################
# Global variables and functions
###############################################################################

# Define the state and its abbreviation
STATE = 'North Carolina'
STATE_ABB = 'NC'
DATA_SOURCE = "North Carolina State Board of Elections, ncsbe.gov"

# Define the election years and their corresponding election dates
ELECTION_YEARS = [2020, 2024]
ELECTION_DATES = {
    2020: datetime(2020, 11, 3),
    2024: datetime(2024, 11, 5)
}

# Define the parties and methods to plot
METHODS = ['MAIL', 'EARLY VOTING']

# Path to election_scraper
PLOT_DIR = os.path.join(ROOT, f'plots/{STATE_ABB}/')

###############################################################################
# Read in data and create plots
###############################################################################

ad = pd.read_csv(os.path.join(ROOT, 
                              f"plotters/{STATE_ABB}/plot_data/20250210.csv"))

# Cut off the dataset after early voting period ends. We do this here because
# we want to modify the data not the plot window
ad = ad.loc[(ad.daysLeft >= 3) | (ad.method == 'MAIL')]

os.makedirs(os.path.join(PLOT_DIR, 'early'), exist_ok=True)
os.makedirs(os.path.join(PLOT_DIR, 'mail'), exist_ok=True)

for method in METHODS:
    plot_relative(method, 
                      ad,
                      PLOT_DIR,
                      STATE, 
                      DATA_SOURCE,
                      ELECTION_DATES,
                      (0,31),
                      'returned')
