# Election Scrapers
Repository for gathering voter registration and early vote data

readme first written by Sina Shaikh at MEDSL in 2025

## Setup

1. Clone or download this repository.
2. Install the latest version of Python and pip if you don't have it already. 
3. In your console, change directory to the election\_scraper folder.
4. Install dependencies by typing in the following in console:
  ```
  python -m pip install --user -r requirements.txt
  ```
5. Open election\_scraper/scrapers/executor.py 
6. Configure which scrapers you want to run and how frequently using
DOWNLOAD\_FREQ\_DICT. 
    The default is that all scrapers not specified run once a
    week and you can choose to run scrapers more frequently or not at all. By
    default, MT/registration and RI/registration are inactive as they won't run
    in headless mode. AZ/registration and NV/registration are also disabled by
    default as CAPTCHA prevents them from working right now. I've included them
    in case you have a monitor you can run a non-headless (headfull?) scraper
    on and want data from states like MT and RI.
7. Open election\_scraper/scrapers/helper.py
8. Configure download type
    All scrapers default to original which download all new files and do
    not redownload old files. SAVE\_COPY downloads all available files every
    time the scraper runs and saves it to a folder archive\_{CURR\_DATE}. 
    OVERWRITE is similar to SAVE\_COPY but each time it runs it clears all
    previous archive\_{PAST\_DATE} folders. By default NC/registration and 
    PA/early are set to overwrite as they take up a lot of storage. 
    If you have the space and want more data, you can remove those lines.
    TX/early has SAVE\_COPY as we found that they modify early voting numbers
    for past days as they process ballots from previous days.
9. Setup the automation 

    Open crontab by running crontab -e in your terminal.

    Enter these two lines in your crontab:
    00 6 * * * python3 {ROOT}/election\_scrapers/scrapers/executor.py
    00 18 * * * python3 {ROOT}/election\_scrapers/scrapers/executor.py "evening"
    (where ROOT is the full path to the directory containg election\_scrapers)

    You can change the specific timing based on when you want the morning and
    evening scrapers to run
14. Setup SlackMessage.py (Optional)
    You can set up slack notifications using webhooks to notify you when
    a change has been made to errors.txt in the last day. You can learn more
    about getting a slack webhooks address for your slack here: 
    https://api.slack.com/messaging/webhooks. Note that some organizations
    may limit the use of webhooks.
10. Setup plotters
    Set root directory in plotting_helper.py
11. Write additional plotters as needed
    3 example plot types have been laid out in plotting\_helper.py (more details
    details in plotting\_helper.py):
        1. Plot values relative to the current and a past election (ex NC early)
        2. Plot values relative to current time period and a past time period
        (ex WI reg)
        3. Plot change from a previous time period (ex WI reg if you change to
        use plot_change function)
12. Add plotters and cleaners to executor.py in plotters as needed
    (Simmilar format to the other executor except for no default of weekly)
13. Setup the plotting automation 
    Open crontab by running crontab -e in your terminal.
    
    Enter this line in your crontab:
    00 6 * * * python3 {ROOT}/election\_plotters/executor.py
    (where ROOT is the full path to the directory containg election\_scrapers)
14. Sit back and relax on the beach in Puerto Rico while your data and plots
make themselves