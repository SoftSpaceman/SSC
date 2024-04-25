import requests
import json
import time
import os
import configparser

# Read API credentials from config file
config = configparser.ConfigParser()
config_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config', 'config.ini')
config.read(config_file_path)
api_username = config.get('API', 'username')
api_password = config.get('API', 'password')

# Define URL components
uriBase = "https://www.space-track.org"
requestLogin = "/ajaxauth/login"
requestCmdAction = "/basicspacedata/query"
siteCred = {'identity': api_username, 'password': api_password}

test = '/class/gp/CREATION_DATE/%3Enow-1/orderby/CREATION_DATE%20asc/format/json'

# use requests package to drive the RESTful session with space-track.org
with requests.Session() as session:
    # run the session in a with block to force session to close if we exit

    # need to log in first. note that we get a 200 to say the web site got the data, not that we are logged in
    resp = session.post(uriBase + requestLogin, data=siteCred)
    if resp.status_code != 200:
        raise OSError(resp, "POST fail on login")

    # this query picks up all Starlink satellites from the catalog.
    resp = session.get(uriBase + requestCmdAction + test)
    if resp.status_code != 200:
        print(resp)
        raise OSError(resp, "GET fail on request for Starlink satellites")

    # use the json package to break the json formatted response text into a Python structure (a list of dictionaries)
    retData = json.loads(resp.text)
    satCount = len(retData)
    maxs = 1
    for e in retData:
        # each e describes the latest elements for one Starlink satellite.
        print("Satellite Name:", e['OBJECT_NAME'])
        print("Epoch:", e['EPOCH'])
        print()
        
        maxs += 1
        if maxs > 40:
            print("Snoozing for 60 secs for rate limit reasons (max 20/min and 200/hr)...")
            time.sleep(60)
            maxs = 1

    session.close()

print("Completed session")
