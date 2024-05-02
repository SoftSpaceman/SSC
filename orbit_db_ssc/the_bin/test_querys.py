


# THIS FILE was used to test different queries to the space-track API. It is not used in the final version of the program.


############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################

import os
import configparser
import requests
from datetime import datetime, timezone

def fetch_and_print_data():
    try:
        # Read API credentials from config file
        config = configparser.ConfigParser()
        config_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.ini')
        config.read(config_file_path)
        api_username = config.get('API', 'username')
        api_password = config.get('API', 'password')

        # Define URL components
        uriBase = "https://www.space-track.org"
        requestLogin = "/ajaxauth/login"
        requestCmdAction = "/basicspacedata/query"
        siteCred = {'identity': api_username, 'password': api_password}





        gp_id = f'/class/gp/gp_id/%3E255143244/format/json/orderby/norad_cat_id' # gets the data since the given gp_id number.

        kk = f'/class/gp/CREATION_DATE/%3Enow-1/orderby/CREATION_DATE%20asc/format/json' # gives data from the last 24 hours. in creation_date order.

        a = f'/class/gp/CREATION_DATE/%3Enow-0.5/orderby/CREATION_DATE%20asc/format/json' # gives data from the last 12 hours. in creation_date order.

        x = f'/class/gp/CREATION_DATE/%3Enow-0.25/orderby/CREATION_DATE%20asc/format/json' # gives data from the last 6 hours. in creation_date order.

        y = f'/class/gp/CREATION_DATE/%3Enow-0.125/orderby/CREATION_DATE%20asc/format/json' # gives data from the last 3 hours. in creation_date order.

        c = f'/class/gp/CREATION_DATE/%3Enow-0.0069444/orderby/CREATION_DATE%20asc/format/json' # gives data from the last 10 minutes. in creation_date order.


        newest = f'/class/gp/CREATION_DATE/%3Enow-0.3/orderby/CREATION_DATE%20desc/limit/10/format/josn' 


        # Main script
        with requests.Session() as session:
            # Login to space-track.org
            resp = session.post(uriBase + requestLogin, data=siteCred)
            resp.raise_for_status()  # Raise an error for bad response status

            # Fetch satellite data
            resp = session.get(uriBase + requestCmdAction + newest)
            resp.raise_for_status()  # Raise an error for bad response status

            # Print fetched data
            fetched_data = resp.json()
            print("NORAD Catalog IDs, Creation Dates, and UTC Time:")
            for obj in fetched_data:
                norad = obj['NORAD_CAT_ID']
                creation_date = obj['CREATION_DATE']
                utc_time = datetime.now(timezone.utc).strftime("%H:%M:%S UTC") # %Y-%m-%d 
                print(f"NORAD: {norad}, Creation Date: {creation_date}, UTC Time at fetch: {utc_time}")
            print(f"Number of data points fetched: {len(fetched_data)}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    fetch_and_print_data()
