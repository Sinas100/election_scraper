###############################################################################
# Script to notify you when new errors appear in your error file
# Written by Sina Shaikh in 2024
###############################################################################

import time
import hashlib
import os

import requests

import helper

###############################################################################
# Setup Functions
###############################################################################

def send_slack_message(message):
    payload = '{"text":"%s"}' % message
    requests.post('!!!INPUT YOUR SLACK HOOKS ADDRESS HERE!!!',
               data=payload, timeout=helper.BREAK_AFTER)

def get_file_hash(file_path):
    # Calculate the hash of the file content
    with open(file_path, 'rb') as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    return file_hash

def check_file_changed(file_path, hours):
    try:
        current_time = time.time()
        past_time = current_time - hours * 3600


        # Get the modification time of the file
        modification_time = os.path.getmtime(file_path)

        # Check if the file has been modified within the last 'hours' hours
        if modification_time > past_time:
            return True
        return False

    except FileNotFoundError:
        # Handle file not found error if needed
        return False


# Check if file has changed in the last 24 hours
if check_file_changed(helper.BASE_PATH + \
                      'election_scraper/scrapers/errors.txt', 24):
    send_slack_message("New Errors!")
