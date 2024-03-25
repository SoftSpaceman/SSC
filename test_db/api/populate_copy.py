import os
import requests
import logging
import datetime
import configparser
import psycopg2
import time

# Set up logging
logging.basicConfig(filename='GP_populate_copy.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define constants
REQUESTS_PER_MINUTE = 20
TIME_INTERVAL = 60  # in seconds

# Token bucket for throttling
token_bucket = REQUESTS_PER_MINUTE
last_refill_time = time.time()

class MyError(Exception):
    """Custom exception class."""
    def __init__(self, args):
        """Initialize MyError instance."""
        super().__init__("My exception was raised with arguments {0}".format(args))
        self.args = args

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

requestGPdata = f'/class/gp_history/orderby/NORAD_CAT_ID%20desc/emptyresult/show'

# /class/gp/orderby/NORAD_CAT_ID%20asc/emptyresult/show

# /class/gp_history/orderby/NORAD_CAT_ID%20desc/emptyresult/show

# Get database connection parameters
host = config.get('tables', 'host')
dbname = config.get('tables', 'dbname')
user = config.get('tables', 'user')
password = config.get('tables', 'password')
port = config.get('tables', 'port')


# Function to check if throttling limit is reached
def is_throttled():
    global token_bucket, last_refill_time
    elapsed_time = time.time() - last_refill_time
    if elapsed_time > TIME_INTERVAL:
        refill_bucket()  # Refill token bucket after TIME_INTERVAL
        logging.info("Token bucket refilled. Current token bucket: %d", token_bucket)
    if token_bucket <= 0:
        logging.info("Throttling limit reached. Current token bucket: %d", token_bucket)
        return True  # Throttling limit reached
    else:
        token_bucket -= 1  # Decrement token bucket for each request
        logging.info("Token bucket decremented. Current token bucket: %d", token_bucket)
        return False


# Function to refill token bucket
def refill_bucket():
    global token_bucket, last_refill_time
    token_bucket = REQUESTS_PER_MINUTE
    last_refill_time = time.time()
    logging.info("Token bucket refilled. Current token bucket: %d", token_bucket)

# Function to make API requests with throttling
def make_request(session, url):
    while is_throttled():
        time.sleep(1)  # Wait until token bucket is refilled
    return session.get(url)


# Function to store data in PostgreSQL
def store_data_in_postgresql(data):
    num_inserted = 0
    conn = None
    try:
        # Connect to PostgreSQL database
        conn = psycopg2.connect( host=host, dbname=dbname, user=user, password=password, port=port)
        cursor = conn.cursor()

        # Insert data into PostgreSQL table
        for item in data:
            #print(item)  # print into the debugging line
            
            try:
                cursor.execute("INSERT INTO gp_file (CCSDS_OMM_VERS, COMMENT, CREATION_DATE, ORIGINATOR, OBJECT_NAME, OBJECT_ID, CENTER_NAME, REF_FRAME, TIME_SYSTEM, MEAN_ELEMENT_THEORY, EPOCH, MEAN_MOTION, ECCENTRICITY, INCLINATION, RA_OF_ASC_NODE, ARG_OF_PERICENTER, MEAN_ANOMALY, EPHEMERIS_TYPE, CLASSIFICATION_TYPE, NORAD_CAT_ID, ELEMENT_SET_NO, REV_AT_EPOCH, BSTAR, MEAN_MOTION_DOT, MEAN_MOTION_DDOT, SEMIMAJOR_AXIS, PERIOD, APOAPSIS, PERIAPSIS, OBJECT_TYPE, RCS_SIZE, COUNTRY_CODE, LAUNCH_DATE, SITE, DECAY_DATE, FILE, GP_ID, TLE_LINE0, TLE_LINE1, TLE_LINE2) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (item['CCSDS_OMM_VERS'], item['COMMENT'], item['CREATION_DATE'], item['ORIGINATOR'], item['OBJECT_NAME'], item['OBJECT_ID'], item['CENTER_NAME'], item['REF_FRAME'], item['TIME_SYSTEM'], item['MEAN_ELEMENT_THEORY'], item['EPOCH'], item['MEAN_MOTION'], item['ECCENTRICITY'], item['INCLINATION'], item['RA_OF_ASC_NODE'], item['ARG_OF_PERICENTER'], item['MEAN_ANOMALY'], item['EPHEMERIS_TYPE'], item['CLASSIFICATION_TYPE'], item['NORAD_CAT_ID'], item['ELEMENT_SET_NO'], item['REV_AT_EPOCH'], item['BSTAR'], item['MEAN_MOTION_DOT'], item['MEAN_MOTION_DDOT'], item['SEMIMAJOR_AXIS'], item['PERIOD'], item['APOAPSIS'], item['PERIAPSIS'], item['OBJECT_TYPE'], item['RCS_SIZE'], item['COUNTRY_CODE'], item['LAUNCH_DATE'], item['SITE'], item['DECAY_DATE'], item['FILE'], item['GP_ID'], item['TLE_LINE0'], item['TLE_LINE1'], item['TLE_LINE2']))
            
                num_inserted += 1
            except Exception as e:
                print(f"Error occurred with item {item}: {e}")
                raise e
           
        conn.commit()
        logging.info("Data insertion into PostgreSQL successful.")
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error("Error occurred while inserting data into PostgreSQL: %s", error)

    finally:
        if conn is not None:
            cursor.close()
            conn.close()
            logging.info("Database connection closed.")
    return num_inserted


# Main script
with requests.Session() as session:
   
    try:
        # Login
        resp_login = session.post(uriBase + requestLogin, data=siteCred)
        if resp_login.status_code != 200:
            raise Exception(f"Login failed with status code: {resp_login.status_code}")
        logging.info("Login successful")

        # Fetch satellite data
        resp_fetch = make_request(session, uriBase + requestCmdAction + requestGPdata)
        if resp_fetch.status_code != 200:
            raise Exception(f"Failed to fetch data with status code: {resp_fetch.status_code}")
        logging.info("Data fetched successfully")

        # Calculate data size
        data_size = len(resp_fetch.content) if resp_fetch.content else 0
        logging.info("Data size: %d bytes", data_size)

        # Store fetched data
        fetched_data = resp_fetch.json()

        # Check if data was fetched successfully and print it
        if fetched_data:
            num_inserted = store_data_in_postgresql(fetched_data)
            logging.info("Number of objects inserted: %d", num_inserted)

        else:
            logging.info("No data fetched.")

    except Exception as e:
        logging.error("Error occurred: %s", e)

# Function to make API requests with throttling
def make_request(session, url):
    while is_throttled():
        time.sleep(1)  # Wait until token bucket is refilled
    try:
        return session.get(url)
    except requests.exceptions.RequestException as e:
        logging.error(f"Error occurred during API request: {e}")
        return None

