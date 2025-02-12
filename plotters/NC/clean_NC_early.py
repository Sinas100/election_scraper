###############################################################################
# Script to clean North Carolina early voting data
# Written by sbaltz in 2024, refactored in 2025 by Sina Shaikh
###############################################################################

import pandas as pd
import zipfile
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
from tqdm import tqdm
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from plotting_helper import *

###############################################################################
# Global variables and functions
###############################################################################

# Path to election_scrapers (including election_scrapers)
BASE_DIR = os.path.join(ROOT, 'plotters/NC/')
RAW_FOLDER = os.path.join(BASE_DIR, 'past_data/absentee_20241105_20241105.zip')
RAW_PREV = os.path.join(BASE_DIR, 'past_data/absentee_20201103.csv')
START_DAY = datetime.strptime('09/20/2024','%m/%d/%Y').date() 
# datetime.today()
CURR_DAY = datetime.strptime('11/05/2024','%m/%d/%Y').date() 
LAST_DAY_THEN = datetime.strptime('11/03/2020','%m/%d/%Y').date()

# If you want to go all the way to past election day, True, else False
GO_TO_END = True

#Do we need to go through the whole bother of calculating the 2020 values?
PREP_2020_DATA = False

PARTIES = ['OTH', 'DEM', 'REP']
METHODS = ['MAIL', 'EARLY VOTING']

#Calculate the dates of interest in 2024
DATE_SEQ = pd.date_range(START_DAY, CURR_DAY-timedelta(days=1), freq='d')

################################################################################
# Read the raw data and build the dataframe to plot
################################################################################
if PREP_2020_DATA:
    prev = pd.read_csv(RAW_PREV, encoding='ISO-8859-1', low_memory=False)
    
    prev['applyDate'] = pd.to_datetime(prev.ballot_req_dt)
    prev['sendDate'] = pd.to_datetime(prev.ballot_send_dt, errors='coerce')
    prev['returnDate'] = pd.to_datetime(prev.ballot_rtn_dt, errors='coerce')
    prev.loc[(prev.voter_party_code != 'DEM') &
             (prev.voter_party_code != 'REP'), 'voter_party_code'] = 'OTH'
    prev = prev.loc[prev.ballot_rtn_status == 'ACCEPTED']
    prev.loc[prev.ballot_req_type == 'ONE-STOP', 
             'ballot_req_type'] = 'EARLY VOTING'

    #We need to generate a sequence of days that is the same number of days before
    # the 2020 election as the corresponding days are before the 2024 election. For
    # the fixed first date, it's 2 days earlier. For the moving date, it's 2 days
    # before yesterday, which is a difference of 3 days
    if GO_TO_END:
        oldEndDay = LAST_DAY_THEN
    else:
        oldEndDay = CURR_DAY - relativedelta(years=4) - timedelta(days=3)

    oldDateSeq = pd.date_range(
        pd.to_datetime(START_DAY - relativedelta(years=4) - timedelta(days=2)),
        oldEndDay,
        freq='d')
    
    #The current date sequence is simpler
    allDates = list(oldDateSeq) + list(DATE_SEQ)
    
    #Now prepare an empty dataframe to store the plotting data
    entriesNum = len(allDates)*len(PARTIES)*len(METHODS)
    ad = pd.DataFrame(index=range(entriesNum),
                      columns = ['day','requested','sent','returned','party',
                                 'method']
                      )
    row = 0
    for party in PARTIES:
        for theDay in tqdm(list(oldDateSeq)):
            for method in METHODS:
                app = sum(prev.loc[(prev.voter_party_code == party) &
                        (prev.ballot_req_type == method),
                        'applyDate'] <= theDay)
                sen = sum(prev.loc[(prev.voter_party_code == party) &
                         (prev.ballot_req_type == method),
                         'sendDate'] <= theDay)
                ret = sum(prev.loc[(prev.voter_party_code == party) &
                                   (prev.ballot_req_type == method),
                                   'returnDate'] <= theDay)
                theRow = pd.Series([theDay,app,sen,ret,party,method])
                ad.iloc[row] = theRow
                row += 1

    ad.to_csv(f'{BASE_DIR}plot_data/2020_values.csv', index=False) 
    #We're done with the 2020 dataset; drop it
    del prev
else:
    ad = pd.read_csv(f'{BASE_DIR}plot_data/2020_values.csv')
    #The row to continue saving to is the first empty row
    row = min(ad.loc[ad.day.isna()].index)
    #We need enough empty rows to add all the data we have
    currEmpty = sum(ad.day.isna())
    emptyNeed = len(list(DATE_SEQ)*len(PARTIES)*len(METHODS))
    lenDiff = emptyNeed - currEmpty
    totalLen = len(ad)
    addOn = pd.DataFrame(index = range(totalLen, totalLen+lenDiff),
                         columns = list(ad.columns)
                      )
    ad = pd.concat([ad, addOn])

#Now proceed to the 2024 file
with zipfile.ZipFile(RAW_FOLDER, 'r') as z:
    with z.open('absentee_20241105.csv') as f:
        nc = pd.read_csv(f, encoding='unicode_escape')

nc['applyDate'] = pd.to_datetime(nc.ballot_req_dt)
nc['sendDate'] = pd.to_datetime(nc.ballot_send_dt)
nc['returnDate'] = pd.to_datetime(nc.ballot_rtn_dt, errors='coerce')
nc.loc[(nc.voter_party_code != 'DEM') &
       (nc.voter_party_code != 'REP'), 'voter_party_code'] = 'OTH'

nc = nc.loc[nc.ballot_rtn_status == 'ACCEPTED']

for party in PARTIES:
    for theDay in tqdm(list(DATE_SEQ)):
        for method in METHODS:
            app = sum(nc.loc[(nc.voter_party_code == party) &
                    (nc.ballot_req_type == method),
                    'applyDate'] <= theDay)
            sen = sum(nc.loc[(nc.voter_party_code == party) &
                     (nc.ballot_req_type == method),
                     'sendDate'] <= theDay)
            ret = sum(nc.loc[(nc.voter_party_code == party) &
                               (nc.ballot_req_type == method),
                               'returnDate'] <= theDay)
            theRow = pd.Series([theDay,app,sen,ret,party,method])
            ad.iloc[row] = theRow
            row += 1

#The x-axis will be the number of days left until the respective election
ad.day = pd.to_datetime(ad.day)
ad['daysLeft'] = pd.NA
elecDayCurr = datetime.strptime("11-05-2024", "%m-%d-%Y")
elecDayPrev = datetime.strptime("11-03-2020", "%m-%d-%Y")
ad.loc[ad.day.dt.year == 2020, 'daysLeft'] = (elecDayPrev - ad.day).dt.days
ad.loc[ad.day.dt.year == 2024, 'daysLeft'] = (elecDayCurr - ad.day).dt.days
ad['year'] = ad.day.dt.year
ad.daysLeft = ad.daysLeft.astype("Int64")

ad.to_csv(f'{BASE_DIR}plot_data/{date.today().strftime("%Y%m%d")}.csv',
           index=False)
