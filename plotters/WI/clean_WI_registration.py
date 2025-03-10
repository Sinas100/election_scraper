###############################################################################
# Script to clean Wisconsin registration data
# Written by Sina Shaikh in 2025
###############################################################################

from datetime import datetime
import os
import glob
import sys
from re import sub
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from plotting_helper import *

###############################################################################
# Global variables and functions
###############################################################################

BASE_DIR = os.path.join(ROOT, 'plotters/WI/')
PREP_PAST_DATA = True

ELECTION_DATES = {
    2023: datetime(2023, 4, 4),
    2025: datetime(2025, 4, 1)
}


################################################################################
# Read the raw data and build the dataframe to plot
################################################################################

os.chdir(os.path.join(ROOT, 'data/WI/registration/'))

files = glob.glob("*.csv") + glob.glob("*.xlsx")
data = []

if not PREP_PAST_DATA:
    data = pd.read_csv(sorted(glob.glob(os.path.join(os.path.join(BASE_DIR,
                                                'plot_data'), "*.csv")))[-1])
    max_year = data["year"].max()

for file in files:
    standardized_file = sub(r",\s*", ", ", file)
    date_str = " ".join(standardized_file.split()[:3]) 
    file_date = datetime.strptime(date_str, "%B %d, %Y")
    year = file_date.year

    if not PREP_PAST_DATA and year < max_year:
        continue

    if file.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df_preview = pd.read_excel(file, sheet_name=0, header=None, nrows=2)
        first_row_contains_vote = any("vote" in str(col).lower() for
                                       col in df_preview.iloc[0])
        header_row = 0 if first_row_contains_vote else 1

        df = pd.read_excel(file, sheet_name=0, header=header_row)

    vote_cols = [col for col in df.columns if "vote" in col.lower()]

    total_votes = df[vote_cols].sum().sum() if vote_cols else 0

    data.append([file_date, total_votes, year])

output = pd.DataFrame(data, columns=["day", "registered_voters", "year"])
output = output.sort_values(by='day')
output['method'] = 'REGISTRATION'
output['party'] = 'TOTAL'

output.day = pd.to_datetime(output.day)
output['daysLeft'] = pd.NA
elecDayCurr = ELECTION_DATES[2025]
elecDayPrev = ELECTION_DATES[2023]
output.loc[output.day.dt.year == 2023, 'daysLeft'] = (elecDayPrev -
                                                       output.day).dt.days
output.loc[output.day.dt.year == 2025, 'daysLeft'] = (elecDayCurr - 
                                                      output.day).dt.days
output['year'] = output.day.dt.year
output.daysLeft = output.daysLeft.astype("Int64")

os.makedirs(os.path.join(BASE_DIR, 'plot_data'), exist_ok=True)
output.to_csv(os.path.join(BASE_DIR, 'plot_data', 
                           f'{date.today().strftime("%Y%m%d")}.csv'),
           index=False)
