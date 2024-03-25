

import requests
import json
import configparser
import os
import time
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler

# Configure rotating file handler
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_file = 'logfile.txt'
max_log_size_bytes = 10 * 1024 * 1024  # 10 MB
backup_count = 5  # Number of backup log files

file_handler = RotatingFileHandler(log_file, maxBytes=max_log_size_bytes, backupCount=backup_count)
file_handler.setFormatter(log_formatter)

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

# Now you can use logger to log messages
#logger.info("Starting session...")






# Configure logging
#logging.basicConfig(filename='logfile.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#logging.basicConfig(filename='logfile.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
#logging.basicConfig(filename='logfile.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', flush=True)



class MyError(Exception):
    def __init__(self, args):
        Exception.__init__(self, "My exception was raised with arguments {0}".format(args))
        self.args = args

# See https://www.space-track.org/documentation for details on REST queries
# the "Find Starlinks" query searches all satellites with NORAD_CAT_ID > 40000, with OBJECT_NAME matching STARLINK*, 1 line per sat
# the "OMM Starlink" query gets all Orbital Mean-Elements Messages (OMM) for a specific NORAD_CAT_ID in JSON format

# uriBase = "https://www.space-track.org"
# requestLogin = "/ajaxauth/login"
# requestCmdAction = "/basicspacedata/query"
requestFindStarlinks = "/class/tle_latest/NORAD_CAT_ID/>40000/ORDINAL/1/OBJECT_NAME/STARLINK~~/format/json/orderby/NORAD_CAT_ID%20asc"
requestOMMStarlink1 = "/class/omm/NORAD_CAT_ID/"
requestOMMStarlink2 = "/orderby/EPOCH%20asc/format/json"

# Your credentials are stored in directory config and file named config.ini.
# These are needed to log in to the space-track.org RESTful service.
# Read API credentials from config file
config = configparser.ConfigParser()
config_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'config', 'config.ini')
config.read(config_file_path)
api_username = config.get('API', 'username')
api_password = config.get('API', 'password')

# Define URL components
uriBase = "https://www.space-track.org"
requestLogin = "/ajaxauth/login"
requestCmdAction = "/basicspacedata/query"
siteCred = {'identity': api_username, 'password': api_password}

getGPhistory = "/class/gp_history/orderby/NORAD_CAT_ID%20desc/emptyresult/show"
getGPhistory_small = "/class/gp/orderby/NORAD_CAT_ID%20asc/emptyresult/show"
all_norad = "/class/gp/NORAD_CAT_ID/>40000/ORDINAL/1/format/json/orderby/NORAD_CAT_ID%20asc"

logging.info("Starting session...")

# use requests package to drive the RESTful session with space-track.org
with requests.Session() as session:
    # run the session in a with block to force session to close if we exit

    # need to log in first. note that we get a 200 to say the web site got the data, not that we are logged in
    resp = session.post(uriBase + requestLogin, data=siteCred)
    if resp.status_code != 200:
        logging.error("POST fail on login")
        raise MyError(resp, "POST fail on login")
    else:
        logging.info("Logged in successfully.")

    # this query picks up all Starlink satellites from the catalog. Note - a 401 failure shows you have bad credentials
    resp = session.get(uriBase + requestCmdAction + all_norad)  # requestFindStarlinks
    if resp.status_code != 200:
        logging.error("GET fail on request for Starlink satellites")
        raise MyError(resp, "GET fail on request for Starlink satellites")
    else:
        logging.info("Retrieved Starlink satellites successfully.")

    # use the json package to break the json formatted response text into a Python structure (a list of dictionaries)
    retData = json.loads(resp.text)
    satCount = len(retData)
    satIds = []
    for e in retData:
        # each e describes the latest elements for one Starlink satellite. We just need the NORAD_CAT_ID
        catId = e['NORAD_CAT_ID']
        satIds.append(catId)

   #using our new list of Starlink satellite NORAD_CAT_IDs, we can now get the OMM message
    maxs = 1
    for s in satIds:
        resp = session.get(uriBase + requestCmdAction + requestOMMStarlink1 + s + requestOMMStarlink2)
        if resp.status_code != 200:
            # If you are getting error 500's here, its probably the rate throttle on the site (20/min and 200/hr)
            # wait a while and retry
            logging.error("GET fail on request for Starlink satellite " + s)
            raise MyError(resp, "GET fail on request for Starlink satellite " + s)
        else:
            logging.info("Retrieved OMM for Starlink satellite " + s + " successfully.")

        # the data here can be quite large, as it's all the elements for every entry for one Starlink satellite
        retData = json.loads(resp.text)
        for e in retData:
            maxs = maxs + 1
        if maxs > 18:
            logging.info("Snoozing for 60 secs for rate limit reasons (max 20/min and 200/hr)...")
            time.sleep(30)
            maxs = 1
    session.close()
    logging.info("Completed session")



















#
## SLTrack.py
## (c) 2019 Andrew Stokes  All Rights Reserved
##
##
## Simple Python app to extract Starlink satellite history data from www.space-track.org into a spreadsheet
## (Note action for you in the code below, to set up a config file with your access and output details)
##
##
##  Copyright Notice:
##
##  This program is free software: you can redistribute it and/or modify
##  it under the terms of the GNU General Public License as published by
##  the Free Software Foundation, either version 3 of the License, or
##  (at your option) any later version.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU General Public License for more details.
##
##  For full licencing terms, please refer to the GNU General Public License
##  (gpl-3_0.txt) distributed with this release, or see
##  http://www.gnu.org/licenses/.
##

# import requests
# import json
# import configparser
# import os
# import time
# from datetime import datetime

# class MyError(Exception):
#     def __init___(self,args):
#         Exception.__init__(self,"my exception was raised with arguments {0}".format(args))
#         self.args = args

# # See https://www.space-track.org/documentation for details on REST queries
# # the "Find Starlinks" query searches all satellites with NORAD_CAT_ID > 40000, with OBJECT_NAME matching STARLINK*, 1 line per sat
# # the "OMM Starlink" query gets all Orbital Mean-Elements Messages (OMM) for a specific NORAD_CAT_ID in JSON format

# uriBase                = "https://www.space-track.org"
# requestLogin           = "/ajaxauth/login"
# requestCmdAction       = "/basicspacedata/query" 
# requestFindStarlinks   = "/class/tle_latest/NORAD_CAT_ID/>40000/ORDINAL/1/OBJECT_NAME/STARLINK~~/format/json/orderby/NORAD_CAT_ID%20asc"
# requestOMMStarlink1    = "/class/omm/NORAD_CAT_ID/"
# requestOMMStarlink2    = "/orderby/EPOCH%20asc/format/json"


# # Your credientials are stored in directory config and file named config.ini. 
# # these are needed to log in to the space-track.org RESTful service.
# # Read API credentials from config file
# config = configparser.ConfigParser()
# config_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'config', 'config.ini')
# config.read(config_file_path)
# api_username = config.get('API', 'username')
# api_password = config.get('API', 'password')

# # Define URL components
# uriBase = "https://www.space-track.org"
# requestLogin = "/ajaxauth/login"
# requestCmdAction = "/basicspacedata/query"
# siteCred = {'identity': api_username, 'password': api_password}

# # write the headers on the spreadsheet
# # now = datetime.now()

# # wsline = 3

# # use requests package to drive the RESTful session with space-track.org
# with requests.Session() as session:
#     # run the session in a with block to force session to close if we exit

#     # need to log in first. note that we get a 200 to say the web site got the data, not that we are logged in
#     resp = session.post(uriBase + requestLogin, data = siteCred)
#     if resp.status_code != 200:
#         raise MyError(resp, "POST fail on login")

#     # this query picks up all Starlink satellites from the catalog. Note - a 401 failure shows you have bad credentials 
#     resp = session.get(uriBase + requestCmdAction + requestFindStarlinks)
#     if resp.status_code != 200:
#         print(resp)
#         raise MyError(resp, "GET fail on request for Starlink satellites")

#     # use the json package to break the json formatted response text into a Python structure (a list of dictionaries)
#     retData = json.loads(resp.text)
#     satCount = len(retData)
#     satIds = []
#     for e in retData:
#         # each e describes the latest elements for one Starlink satellite. We just need the NORAD_CAT_ID 
#         catId = e['NORAD_CAT_ID']
#         satIds.append(catId)

#     # using our new list of Starlink satellite NORAD_CAT_IDs, we can now get the OMM message
#     maxs = 1
#     for s in satIds:
#         resp = session.get(uriBase + requestCmdAction + requestOMMStarlink1 + s + requestOMMStarlink2)
#         if resp.status_code != 200:
#             # If you are getting error 500's here, its probably the rate throttle on the site (20/min and 200/hr)
#             # wait a while and retry
#             print(resp)
#             raise MyError(resp, "GET fail on request for Starlink satellite " + s)

#         # the data here can be quite large, as it's all the elements for every entry for one Starlink satellite
#         retData = json.loads(resp.text)
#         for e in retData:
            
#           #  wsline = wsline + 1
#             maxs = maxs + 1
#         if maxs > 18:
#             print("Snoozing for 60 secs for rate limit reasons (max 20/min and 200/hr)...")
#             time.sleep(60)
#             maxs = 1
#     session.close()
# print("Completed session") 
                

        