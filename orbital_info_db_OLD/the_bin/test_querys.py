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





                    ## TEST TEST TEST 18/04/24 Testar att ordna efter creation_date istället och så jobbar vi oss neråt i now-tid för att få det senaste 
            # 0.02 = ca 30 min funnkar 


        # gp_id = f'/class/gp/gp_id/%3E255143244/format/json/orderby/norad_cat_id'



        test = f'/class/gp/CREATION_DATE/%3Enow-0.006/orderby/CREATION_DATE%20asc/format/json'  # denna är skcikad UTC 19:47 och gav datan 19:36 creation date. Alltså är den mer än 10 min bakåt i tiden. 
        # NORAD: 59479, Creation Date: 2024-04-22T19:36:15
        # Number of data points fetched: 1

        newest = f'/class/gp/CREATION_DATE/%3Enow-0.3/orderby/CREATION_DATE%20desc/limit/10/format/josn'


        # Define the request to fetch data from space-track.org
        query = f'/class/gp/creation_date/%3Enow-0.00533375/orderby/norad_cat_id/format/json'

        # Main script
        with requests.Session() as session:
            # Login to space-track.org
            resp = session.post(uriBase + requestLogin, data=siteCred)
            resp.raise_for_status()  # Raise an error for bad response status

            # Fetch satellite data
            resp = session.get(uriBase + requestCmdAction + test)
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
