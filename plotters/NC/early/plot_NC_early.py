###############################################################################
# Script to plot North Carolina early voting data
# Written by sbaltz in 2024, refactored in 2025 by Sina Shaikh
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
STATE = 'North Carolina'
STATE_ABB = 'NC/early'
DATA_SOURCE = "North Carolina State Board of Elections, ncsbe.gov"

# Define the election years and their corresponding election dates
ELECTION_YEARS = [2020, 2024]
ELECTION_DATES = {
    2020: datetime(2020, 11, 3),
    2024: datetime(2024, 11, 5)
}

# Define the parties and methods to plot
PLOT_DIR = os.path.join(ROOT, f'plots/{STATE_ABB}/')

###############################################################################
# Read in data and create plots
###############################################################################

folder = os.path.join(ROOT, f"plotters/{STATE_ABB}/plot_data")
csv_files = sorted(os.listdir(folder), reverse=True)
ad = pd.read_csv(os.path.join(folder, csv_files[0]))

# Cut off the dataset after early voting period ends. We do this here because
# we want to modify the data not the plot window
ad = ad.loc[(ad.daysLeft >= 3) | (ad.method == 'MAIL')]

os.makedirs(PLOT_DIR, exist_ok=True)

plot_relative("EARLY VOTING",
              ad,
              PLOT_DIR,
              STATE,
              DATA_SOURCE,
              ELECTION_DATES,
              (0,31),
              'returned')
