
### THIS IS JUST A TEST SCRIPT TO SE IF THE QUERYS WORK... 

import sched
import time
import requests
import os
import configparser

def fetch_and_print_data(sc):
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

        f = f'/class/gp/creation_date/%3Enow-0.0035/orderby/norad_cat_id/format/json'

        with requests.Session() as session:
            # Login to space-track.org
            resp = session.post(uriBase + requestLogin, data=siteCred)
            resp.raise_for_status()  # Raise an error for bad response status

            # Fetch satellite data
            resp = session.get(uriBase + requestCmdAction + f)
            resp.raise_for_status()  # Raise an error for bad response status

            # Print fetched data
            fetched_data = resp.json()
            norad_cat_ids = [obj['NORAD_CAT_ID'] for obj in fetched_data]
            print("NORAD Catalog IDs:")
            print(norad_cat_ids)
            print(f"Number of data points fetched: {len(fetched_data)}")

        # Reschedule the function to run after 60 seconds
        sc.enter(60, 1, fetch_and_print_data, (sc,))

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    # Create a scheduler
    s = sched.scheduler(time.time, time.sleep)
    # Schedule the function to run initially
    s.enter(0, 1, fetch_and_print_data, (s,))
    # Run the scheduler
    s.run()









#########################################################################################################################
#######  THIS IS THE SIMPLES SCRITP THAT JUST FETCHES AND PRINTS THE QUERYS..
#########################################################################################################################



# import os
# import configparser
# import requests

# def fetch_and_print_data():
#     try:
#         # Read API credentials from config file
#         config = configparser.ConfigParser()
#         config_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.ini')
#         config.read(config_file_path)
#         api_username = config.get('API', 'username')
#         api_password = config.get('API', 'password')

#         # Define URL components
#         uriBase = "https://www.space-track.org"
#         requestLogin = "/ajaxauth/login"
#         requestCmdAction = "/basicspacedata/query"
#         siteCred = {'identity': api_username, 'password': api_password}




#         # Define the request to fetch data from space-track.org
#         # This query gives all data from the gp class that has a epoch date from yesterday to today.
#         a = f'/class/gp/epoch/%3Enow-1/orderby/norad_cat_id/format/json'

#         #This query give all data from this moment right now and will be run every minute to get the latest data.
#         b = f'/class/gp/epoch/%3Enow/orderby/norad_cat_id/format/json'

#         # This query will get all data from the gp class that has a decay date that is null. 
#         c = f'/class/gp/DECAY_DATE/null-val/orderby/NORAD_CAT_ID%20asc/emptyresult/show'




#         ## THIS ONE WILL RUN IN gpdata2 It get data that was create within 25 minutes of each request
#         ## this will run every minute
#         d = f'/class/gp/creation_date/%3Enow-0.02/orderby/norad_cat_id/format/json'

#         # THIS WILL RUN IN gpdata3 
#         # This will get data taht ahs been create within 3h of teh reques . 
#         e = f'/class/gp/creation_date/%3Enow-0.125/orderby/norad_cat_id/format/json'

#         # data created within the lates 5 minuts. 
#         f = f'/class/gp/creation_date/%3Enow-0.0035/orderby/norad_cat_id/format/json'


#         # Main script
#         with requests.Session() as session:
#             # Login to space-track.org
#             resp = session.post(uriBase + requestLogin, data=siteCred)
#             resp.raise_for_status()  # Raise an error for bad response status

#             # Fetch satellite data
#             resp = session.get(uriBase + requestCmdAction + f)
#             resp.raise_for_status()  # Raise an error for bad response status

#             # Print fetched data
#             fetched_data = resp.json()
#             norad_cat_ids = [obj['NORAD_CAT_ID'] for obj in fetched_data]
#             print("NORAD Catalog IDs:")
#             print(norad_cat_ids)
#             print(f"Number of data points fetched: {len(fetched_data)}")

#     except Exception as e:
#         print(f"An error occurred: {str(e)}")

# if __name__ == "__main__":
#     fetch_and_print_data()

