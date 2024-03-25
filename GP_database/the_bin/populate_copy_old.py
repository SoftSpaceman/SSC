import requests
import os
import configparser
import logging
import time

# Configure logging
logging.basicConfig(filename='satellite_log.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MyError(Exception):
    def __init__(self, message):
        super().__init__(message)

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

def getTLESatellites(num_iterations):
    requestFindStarlinks = f'/class/gp/orderby/NORAD_CAT_ID%20asc/emptyresult/show'
    try:
        with requests.Session() as session:
            # Logging for login process
            logging.info("Logging in to space-track.org...")
            
            # Login to space-track.org
            resp = session.post(uriBase + requestLogin, data=siteCred)
            if resp.status_code != 200:
                raise MyError(f"POST failed on login. Status code: {resp.status_code}")
            logging.info("Login successful.")
            
            for i in range(num_iterations):
                # Retrieve satellite data
                resp = session.get(uriBase + requestCmdAction + requestFindStarlinks)
                if resp.status_code != 200:
                    raise MyError(f"GET failed on request for satellites. Status code: {resp.status_code}")

                # Log successful data retrieval
                logging.info(f"Iteration {i+1}: Successfully retrieved satellite data")

                satellites = resp.text
                
                # Print a portion of the retrieved data
                print(f"Iteration {i+1}: Sample of retrieved data:")
                print(satellites[:500])  # Print first 500 characters
                
                # Count the total number of data points retrieved
                total_data_points = satellites.count('\n') + 1  # Count number of lines to get total data points
                logging.info(f"Iteration {i+1}: Total data points retrieved: {total_data_points}")
                
                time.sleep(3)  # Throttle limiter
            
            return satellites
    except Exception as e:
        # Log errors and raise custom exception
        logging.error(f"Error occurred: {str(e)}")
        raise MyError(str(e))

try:
    num_iterations = 3  # Set the number of iterations
    satellites_data = getTLESatellites(num_iterations)
    print("Satellite data retrieved successfully!")
except MyError as e:
    print(f"An error occurred: {str(e)}")
