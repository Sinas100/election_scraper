###############################################################################
# Script to plot North Carolina early voting data
# Written by Sina Shaikh in 2025, using code from sbaltz and MedslStyleGuide
###############################################################################

from pathlib import Path
import os
from datetime import date

from matplotlib import font_manager
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd

###############################################################################
# Global variables
###############################################################################
#First download the .ttf files for the MEDSL fonts to whatever directory you
# name in the following path:
ROOT = Path(__file__).resolve().parents[1]
MY_FONT_DIR = os.path.join(ROOT, "plotters")

#Change this to the name of the font you are trying to add
FONT_TO_ADD = "Styrene B"

###############################################################################
# Font
###############################################################################
#Set the font
font_manager._get_fontconfig_fonts.cache_clear()
font_files = font_manager.findSystemFonts(MY_FONT_DIR)
for font_file in font_files:
    font_list = font_manager.fontManager.addfont(font_file)
#font_manager.fontManager.ttflist.extend(font_list)
# Set the font family globally for all plots
plt.rcParams['font.family'] = FONT_TO_ADD

###############################################################################
# Colours
###############################################################################
#Define the MEDSL colours according to
#   http://www.mit.edu/~medsl/brand/charts/index.html
medslGold = "#c0ba79"
medslBlue2 = "#04448B"
medslRed2 = "#CD3C2B"

###############################################################################
# Helper functions
###############################################################################

# This allows you to plot values relative to an election cycle. To see an
# example, see the NC early plot which plots election data relative to the 2020
# and 2024 elections.
def plot_relative(method, ad, output, state, data_source, election_dates,
                      xlims, y_var_to_plot):

    date_to_print = date.today().strftime("%m/%d/%Y")

    years = list(election_dates.keys())

    if len(ad['party'].unique()) > 1:
        parties_to_cols = {'DEM': medslBlue2,
                    'REP': medslRed2,
                    'OTH': medslGold}
    else:
        parties_to_cols = {'TOTAL': "black"}

    parties = list(parties_to_cols.keys())

    # Figure setup
    plt.rcParams["figure.figsize"] = (10, 8)
    plt.gcf().subplots_adjust(bottom=0.17, left=0.18, right=0.92)

    # Set the plot features that depend on the mode
    if method == 'MAIL':
        modeToPrint = 'Mail-In'
        theYLabel = "Cumulative Mail-In Ballots Accepted"
        saveFileName = os.path.join(output, date.today().strftime("%Y%m%d"))
    elif method == 'EARLY VOTING':
        modeToPrint = 'Early Vote'
        theYLabel = "Cumulative Early Votes Cast"
        saveFileName = os.path.join(output, date.today().strftime("%Y%m%d"))
    elif method == 'REGISTRATION':
        modeToPrint = 'Registration'
        theYLabel = "Registered Voters"
        saveFileName = os.path.join(output, date.today().strftime("%Y%m%d"))

    plt.title(
        f"{state} {modeToPrint} {years[0]} vs. " \
            + f"{years[1]}",
        size=21, pad=15)
    plt.figtext(0.05, 0.045,
                f"Data source: {data_source}",
                size=10)
    plt.figtext(0.05, 0.025,
            "Graph source: MIT Election Data and Science Lab, @MITelectionlab",
            size=10)
    plt.figtext(0.05, 0.005,
            f"Date of Graph: {date_to_print}",
            size=10)

    plt.yticks(fontsize=15)
    plt.xticks(fontsize=15)
    plt.gca().yaxis.set_major_formatter(
        mpl.ticker.StrMethodFormatter('{x:,.0f}'))
    YMAX = max(ad.loc[ad.method == method, y_var_to_plot]) * 1.1
    YMIN = min(ad.loc[ad.method == method, y_var_to_plot]) / 1.1

    plt.ylim((YMIN, YMAX))
    plt.ylabel(theYLabel, size=18, labelpad=20)

    plt.xlim(xlims)
    plt.gca().invert_xaxis()

    plt.xlabel("Days Before the Election", size=18, labelpad=15)
    labelX, labelY = (0.86, 0.09)
    plt.figtext(labelX,
                labelY,
                "(" + "/ \n ".join(dt.strftime("%b. %d %Y") for dt in 
                                election_dates.values()) + ")",
                fontsize=10)

    yearsToLine = {year: 'dotted' if year == years[0]
    else 'solid' for year in years}
    yearsToMark = {year: '' for year in years}

    for year in years:
        curr = ad.loc[(ad.year == year) & (ad.method == method)]
        for party in parties:
            plt.plot(list(curr.loc[curr.party == party, 'daysLeft']),
                     list(curr.loc[curr.party == party, y_var_to_plot]),
                     linewidth=3,
                     color=parties_to_cols[party],
                     linestyle=yearsToLine[year],
                     marker=yearsToMark[year],
                     ms=12,
                     alpha=0.75)
    plt.grid(alpha=0.75)

    # Add the legends
    if len(ad['party'].unique()) > 1:
        legendDem = mpl.lines.Line2D([], [], linewidth=3,
                                    color=parties_to_cols["DEM"])
        legendRep = mpl.lines.Line2D([], [], linewidth=3, 
                                    color=parties_to_cols["REP"])
        legendOth = mpl.lines.Line2D([], [], linewidth=3,
                                    color=parties_to_cols["OTH"])
        first_legend = plt.legend(loc='upper left',
                                prop={'size': 12},
                                handles=[legendDem, legendRep, legendOth],
                                labels=['Democrats', 'Republicans',
                                        'All others'])
        plt.gca().add_artist(first_legend)

        prevEx = mpl.lines.Line2D([], [],
                                linewidth=3,
                                color='black',
                                linestyle='dotted')
        currEx = mpl.lines.Line2D([], [],
                                linewidth=3,
                                color='black',
                                linestyle='solid')
        second_legend = plt.legend(loc=(0.01, 0.75),
                                prop={'size': 12},
                                handles=[prevEx, currEx],
                                handlelength=3,
                                labels=[str(year) for year in years])
        plt.gca().add_artist(second_legend)
    else: 
        prevEx = mpl.lines.Line2D([], [],
                                linewidth=3,
                                color='black',
                                linestyle='dotted')
        currEx = mpl.lines.Line2D([], [],
                                linewidth=3,
                                color='black',
                                linestyle='solid')
        second_legend = plt.legend(loc='upper left',
                                prop={'size': 12},
                                handles=[prevEx, currEx],
                                handlelength=3,
                                labels=[str(year) for year in years])
        plt.gca().add_artist(second_legend)

    plt.savefig(saveFileName, dpi=400)
    plt.close()

# This allows you to plot values based on the date. To see an example, see the
# WI registration plot which plots voter registration data for the past 6
# months and for the equivalent period four years prior.
def plot_absolute(method, ad, output, state, data_source, y_var_to_plot,
                  how_many_months, years_since_last_cycle):
    date_to_print = date.today().strftime("%m/%d/%Y")
    cycles = ["Current", f"{years_since_last_cycle} Years Prior"]

    ad['day'] = pd.to_datetime(ad['day'], format="%Y-%m-%d")

    # Calculate the date range for the specified periods
    today = pd.to_datetime(date.today())
    current_cycle_start = today - pd.DateOffset(months=how_many_months)
    last_cycle_start = current_cycle_start - pd.DateOffset(
        years=years_since_last_cycle)
    last_cycle_end = today - pd.DateOffset(years=years_since_last_cycle)

    # Filter data for the two specified periods
    period_1_data = ad[(ad['day'] >= current_cycle_start) &
                        (ad['day'] <= today)]
    period_2_data = ad[(ad['day'] >= last_cycle_start) &
                        (ad['day'] <= last_cycle_end)]

    period_2_data.loc[:, 'day'] = period_2_data['day'] + pd.DateOffset(
        years=years_since_last_cycle)

    if len(ad['party'].unique()) > 1:
        parties_to_cols = {'DEM': medslBlue2,
                    'REP': medslRed2,
                    'OTH': medslGold}
    else:
        parties_to_cols = {'TOTAL': "black"}

    parties = list(parties_to_cols.keys())

    # Figure setup
    plt.rcParams["figure.figsize"] = (10, 8)
    plt.gcf().subplots_adjust(bottom=0.17, left=0.18, right=0.92)

    # Set the plot features that depend on the mode
    if method == 'MAIL':
        modeToPrint = 'Mail-In'
        theYLabel = "Cumulative Mail-In Ballots Accepted"
        saveFileName = os.path.join(output, date.today().strftime("%Y%m%d"))
    elif method == 'EARLY VOTING':
        modeToPrint = 'Early Vote'
        theYLabel = "Cumulative Early Votes Cast"
        saveFileName = os.path.join(output, date.today().strftime("%Y%m%d"))
    elif method == 'REGISTRATION':
        modeToPrint = 'Registration'
        theYLabel = "Registered Voters"
        saveFileName = os.path.join(output, date.today().strftime("%Y%m%d"))

    plt.title(
        f"{state} {modeToPrint} - {cycles[0]} vs. {cycles[1]}",
        size=21, pad=15)
    plt.figtext(0.05, 0.045,
                f"Data source: {data_source}",
                size=10)
    plt.figtext(0.05, 0.025,
            "Graph source: MIT Election Data and Science Lab, @MITelectionlab",
            size=10)
    plt.figtext(0.05, 0.005,
                f"Date of Graph: {date_to_print}",
                size=10)

    plt.yticks(fontsize=15)
    plt.xticks(fontsize=15)
    plt.gca().yaxis.set_major_formatter(
        mpl.ticker.StrMethodFormatter('{x:,.0f}'))

    # Set Y-axis limits dynamically
    YMAX = max(ad.loc[ad.method == method, y_var_to_plot]) * 1.1
    YMIN = min(ad.loc[ad.method == method, y_var_to_plot]) / 1.1
    plt.ylim((YMIN, YMAX))

    # Set labels for axes
    plt.ylabel(theYLabel, size=18, labelpad=20)
    plt.xlabel("Date", size=18, labelpad=15)

    for party in parties:
        plt.plot(list(period_1_data.loc[period_1_data.party == party, 'day']),
                    list(period_1_data.loc[period_1_data.party == party,
                                            y_var_to_plot]),
                    linewidth=3,
                    color=parties_to_cols[party],
                    linestyle='solid',
                    marker='',
                    ms=12,
                    alpha=0.75)
        plt.plot(list(period_2_data.loc[period_2_data.party == party, 'day']),
                    list(period_2_data.loc[period_2_data.party == party,
                                            y_var_to_plot]),
                    linewidth=3,
                    color=parties_to_cols[party],
                    linestyle='dotted',
                    marker='',
                    ms=12,
                    alpha=0.75)

    plt.grid(alpha=0.75)

    # Add legends
    if len(ad['party'].unique()) > 1:
        legendDem = mpl.lines.Line2D([], [], linewidth=3,
                                    color=parties_to_cols["DEM"])
        legendRep = mpl.lines.Line2D([], [], linewidth=3, 
                                    color=parties_to_cols["REP"])
        legendOth = mpl.lines.Line2D([], [], linewidth=3,
                                    color=parties_to_cols["OTH"])
        first_legend = plt.legend(loc='upper left',
                                prop={'size': 12},
                                handles=[legendDem, legendRep, legendOth],
                                labels=['Democrats', 'Republicans',
                                        'All others'])
        plt.gca().add_artist(first_legend)

        prevEx = mpl.lines.Line2D([], [],
                                linewidth=3,
                                color='black',
                                linestyle='solid')
        currEx = mpl.lines.Line2D([], [],
                                linewidth=3,
                                color='black',
                                linestyle='dotted')
        second_legend = plt.legend(loc=(0.01, 0.75),
                                prop={'size': 12},
                                handles=[prevEx, currEx],
                                handlelength=3,
                                labels=[str(cycle) for cycle in cycles])
        plt.gca().add_artist(second_legend)
    else:
        prevEx = mpl.lines.Line2D([], [],
                                linewidth=3,
                                color='black',
                                linestyle='solid')
        currEx = mpl.lines.Line2D([], [],
                                linewidth=3,
                                color='black',
                                linestyle='dotted')
        second_legend = plt.legend(loc='upper left',
                                prop={'size': 12},
                                handles=[prevEx, currEx],
                                handlelength=3,
                                labels=[str(cycle) for cycle in cycles])
        plt.gca().add_artist(second_legend)

    # Save the plot
    plt.savefig(saveFileName, dpi=400)
    plt.close()

# This allows you to plot values based on the date. To see an example, change
# the WI registration plot to plot_change which plots the difference between
# voter registration data for the past 6 months and the equivalent period four
# years prior.
def plot_change(method, ad, output, state, data_source, y_var_to_plot,
                  how_many_months, years_since_last_cycle):
    date_to_print = date.today().strftime("%m/%d/%Y")
    cycles = ["Current", f"{years_since_last_cycle} Years Prior"]

    ad['day'] = pd.to_datetime(ad['day'], format="%Y-%m-%d")

    # Calculate the date range for the specified periods
    today = pd.to_datetime(date.today())
    current_cycle_start = today - pd.DateOffset(months=how_many_months)
    last_cycle_start = current_cycle_start - pd.DateOffset(
        years=years_since_last_cycle)
    last_cycle_end = today - pd.DateOffset(years=years_since_last_cycle)

    # Filter data for the two specified periods
    period_1_data = ad[(ad['day'] >= current_cycle_start) &
                        (ad['day'] <= today)]
    period_2_data = ad[(ad['day'] >= last_cycle_start) &
                        (ad['day'] <= last_cycle_end)]

    period_2_data.loc[:, 'day'] = period_2_data['day'] + pd.DateOffset(
        years=years_since_last_cycle)

    if len(ad['party'].unique()) > 1:
        parties_to_cols = {'DEM': medslBlue2,
                    'REP': medslRed2,
                    'OTH': medslGold}
    else:
        parties_to_cols = {'TOTAL': "black"}

    parties = list(parties_to_cols.keys())

    # Figure setup
    plt.rcParams["figure.figsize"] = (10, 8)
    plt.gcf().subplots_adjust(bottom=0.17, left=0.18, right=0.92)

    # Set the plot features that depend on the mode
    if method == 'MAIL':
        modeToPrint = 'Mail-In'
        theYLabel = "Cumulative Mail-In Ballots Accepted"
        saveFileName = os.path.join(output, date.today().strftime("%Y%m%d"))
    elif method == 'EARLY VOTING':
        modeToPrint = 'Early Vote'
        theYLabel = "Cumulative Early Votes Cast"
        saveFileName = os.path.join(output, date.today().strftime("%Y%m%d"))
    elif method == 'REGISTRATION':
        modeToPrint = 'Registration'
        theYLabel = "Registered Voters"
        saveFileName = os.path.join(output, date.today().strftime("%Y%m%d"))

    plt.title(
        f"{state} {modeToPrint} - {cycles[0]} vs. {cycles[1]}",
        size=21, pad=15)
    plt.figtext(0.05, 0.045,
                f"Data source: {data_source}",
                size=10)
    plt.figtext(0.05, 0.025,
            "Graph source: MIT Election Data and Science Lab, @MITelectionlab",
            size=10)
    plt.figtext(0.05, 0.005,
                f"Date of Graph: {date_to_print}",
                size=10)

    plt.yticks(fontsize=15)
    plt.xticks(fontsize=15)
    plt.gca().yaxis.set_major_formatter(
        mpl.ticker.StrMethodFormatter('{x:,.0f}'))

    # Set Y-axis limits dynamically

    # Set labels for axes
    plt.ylabel(theYLabel, size=18, labelpad=20)
    plt.xlabel("Date", size=18, labelpad=15)

    ymax = 0
    ymin = 0
    for party in parties:
        p1 = period_1_data.loc[period_1_data.party == "TOTAL",
                                y_var_to_plot].reset_index(drop=True)
        p2 = period_2_data.loc[period_2_data.party == "TOTAL",
                               y_var_to_plot].reset_index(drop=True)
        plt.plot(list(period_1_data.loc[period_1_data.party == party, 'day']),
                    (p1 - p2).tolist(),
                    linewidth=3,
                    color=parties_to_cols[party],
                    linestyle='solid',
                    marker='',
                    ms=12,
                    alpha=0.75)
        if max((p1 - p2).tolist()) > ymax:
            ymax = max((p1 - p2).tolist())
        if min((p1 - p2).tolist()) < ymin:
            ymin = min((p1 - p2).tolist())

    ymax = ymax * 1.4
    ymin = ymin * 1.4 if ymin < 0 else ymin / 1.5
    plt.ylim((ymin, ymax))

    plt.grid(alpha=0.75)

    # Add legends
    if len(ad['party'].unique()) > 1:
        legendDem = mpl.lines.Line2D([], [], linewidth=3,
                                    color=parties_to_cols["DEM"])
        legendRep = mpl.lines.Line2D([], [], linewidth=3,
                                    color=parties_to_cols["REP"])
        legendOth = mpl.lines.Line2D([], [], linewidth=3,
                                    color=parties_to_cols["OTH"])
        first_legend = plt.legend(loc='upper left',
                                prop={'size': 12},
                                handles=[legendDem, legendRep, legendOth],
                                labels=['Democrats', 'Republicans',
                                        'All others'])
        plt.gca().add_artist(first_legend)

        prevEx = mpl.lines.Line2D([], [],
                                linewidth=3,
                                color='black',
                                linestyle='solid')
        currEx = mpl.lines.Line2D([], [],
                                linewidth=3,
                                color='black',
                                linestyle='dotted')
        second_legend = plt.legend(loc=(0.01, 0.75),
                                prop={'size': 12},
                                handles=[prevEx, currEx],
                                handlelength=3,
                                labels=[str(cycle) for cycle in cycles])
        plt.gca().add_artist(second_legend)

    # Save the plot
    plt.savefig(saveFileName, dpi=400)
    plt.close()
