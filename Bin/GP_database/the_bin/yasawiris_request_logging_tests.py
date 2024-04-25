# this script is at its core from the Yasawiris project. https://github.com/ysawiris/space_track/blob/master/spack_track.py
# Modifications will be made to fit the current project.

# AS OF NOW: 06/03/2024 
## This script fetches data from spacetrack without puting it any where.

import requests
import json
import configparser
import time
from datetime import datetime



class MyError(Exception):
    def __init___(self,args):
        Exception.__init__(self,"my exception was raised with arguments {0}".format(args))
        self.args = args

# See https://www.space-track.org/documentation for details on REST queries

# login and request URL components to access the RESTful service at spce-track.org.
uriBase                = "https://www.space-track.org"
requestLogin           = "/ajaxauth/login"
requestCmdAction       = "/basicspacedata/query"


# Your credientials are stored in a file named APIconfig.ini. 
# these are needed to log in to the space-track.org RESTful service.
# Use configparser package to pull in the ini file (pip install configparser)
config = configparser.ConfigParser()
config.read(r'C:\Users\Bananberg\Desktop\Space_info\SSC\projects\SSC_database\test_db\api\APIconfig.ini')
configUsr = config.get("configuration","username")
configPwd = config.get("configuration","password")
siteCred = {'identity': configUsr, 'password': configPwd}
## THIS WORKED FINE! 04/03/2024 We are connected. Now to get some acutal data out of this. 

###############################################################
# FOR THE SCRIPT BELOW. 

# rate limit not needed?? []

# I need it to log the time when it fetches the data. [ ]

# Load the data into the database. [ ]
    # try with only 50 data points. [ ]
    #this query: https://www.space-track.org/basicspacedata/query/class/gp/NORAD_CAT_ID/%3C10000/orderby/NORAD_CAT_ID%20asc/limit/50/emptyresult/show
        # is limted to only load 50 Norad_cat_id. 

    # check with your old script to se how you loaded the thata to a database. 



##########################################################################
##########################################################################
##########################################################################
## THIS FILE IS JUST FOR LOGGIN TEST ACCUIERED FROM THIS CHAT FAR DONW IN THE CONVERSIATION: https://g.co/gemini/share/c648d95538c4

import logging
# Configure logging (adjust based on your needs)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')



def getGP():
    # Log request details before sending the request
    logging.debug(f"Sending GET request to: {uriBase + requestCmdAction + requestGPdata}")
    logging.debug(f"Headers (redacted): {dict((k, 'REDACTED') for k in session.headers.keys())}")

    requestGPdata   = f'/class/gp/NORAD_CAT_ID/%3C20000/orderby/NORAD_CAT_ID%20asc/emptyresult/show'
    # use requests package to drive the RESTful session with space-track.org
    with requests.Session() as session:
        # run the session in a with block to force session to close if we exit

        # need to log in first. note that we get a 200 to say the web site got the data, not that we are logged in
        resp = session.post(uriBase + requestLogin, data = siteCred)
        if resp.status_code != 200:
            raise MyError(resp, "POST fail on login")

        # this query picks up GPs for all satellites from the catalog. Note - a 401 failure shows you have bad credentials 
        resp = session.get(uriBase + requestCmdAction + requestGPdata)
        if resp.status_code != 200:
            print(resp)
            raise MyError(resp, "GET fail on request for satellites")

        # resp.text contains all GP data ordere by NORAD_CAT_ID for all the satellies in GP file. 
        satellites = resp.text
        session.close()



    return satellites 




#######################################################################################################################
### TESTS FUNCTIONSFOR MODIFICATIONS ################# 


### A WAY TO LOG THE TIME WHEN THE DATA IS FETCHED.


# import logging

# # Configure logging (adjust based on your needs)
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# def getGP():
#     # ... existing code ...

#     # Log request details with redacted data
#     logging.debug(f"GET request to: {uriBase + requestCmdAction + requestGPdata}")
#     logging.debug(f"Headers (redacted): {dict((k, 'REDACTED') for k in session.headers.keys())}")

#     # ... existing code ...

#     return satellites

# BEFOR THE REQUEST IS SENT.
# import logging

# # Configure logging (adjust based on your needs)
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# def getGP():
#     # Log request details before sending the request
#     logging.debug(f"Sending GET request to: {uriBase + requestCmdAction + requestGPdata}")
#     logging.debug(f"Headers (redacted): {dict((k, 'REDACTED') for k in session.headers.keys())}")

#     # ... existing code ...

#     return satellites



# AFTER A SUCSESSFUL RESPONSE.
# def getGP():
#     # ... existing code ...

#     # Log successful response details (optional)
#     if resp.status_code == 200:
#         logging.debug(f"Received successful response (status code: {resp.status_code})")

#     # ... existing code ...

#     return satellites



# DURING ERROR HANDLING.
# def getGP():
#     # ... existing code ...

#     try:
#         # Send the request
#         resp = session.get(uriBase + requestCmdAction + requestGPdata)
#     except requests.exceptions.RequestException as e:
#         logging.error(f"Request failed: {e}")
#         raise MyError(resp, "GET request failed")

#     # ... existing code ...

#     return satellites
