# https://chat.openai.com/share/020e2c05-c09a-4b98-a977-94ec05ea5871

# https://chat.openai.com/share/942a2da9-8f47-4fbc-8fc7-bb3f8ab9f158

# https://chat.openai.com/share/53e9dda9-eae4-4623-8a40-a7a7f8abc214

import psycopg2
import requests
import json
import logging
import datetime
import configparser
import time
from datetime import datetime
#import os


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MyError(Exception):
    """Custom exception class."""
    def __init__(self, args):
        """Initialize MyError instance."""
        super().__init__("My exception was raised with arguments {0}".format(args))
        self.args = args











# Global variables
uriBase = "https://www.space-track.org"
requestLogin = "/ajaxauth/login"
requestCmdAction = "/basicspacedata/query"


# Your credientials are stored in a file named APIconfig.ini. 
# these are needed to log in to the space-track.org RESTful service.
# Use configparser package to pull in the ini file (pip install configparser)
config = configparser.ConfigParser()
config.read(r'C:\Users\Bananberg\Desktop\Space_info\SSC\projects\SSC_database\test_db\api\APIconfig.ini')
configUsr = config.get("configuration","username")
configPwd = config.get("configuration","password")
siteCred = {'identity': configUsr, 'password': configPwd}

requestGPdata = f'/class/gp/NORAD_CAT_ID/%3E20000/orderby/NORAD_CAT_ID%20asc/emptyresult/show'





# def fetch_data_from_api(session):
#     try:
#         resp = session.post(uriBase + requestLogin, data=siteCred)
#         if resp.status_code != 200:
#             raise MyError(resp, "POST fail on login. Status code: {resp.status_code}")

#         resp = session.get(uriBase + requestCmdAction + requestGPdata)
#         if resp.status_code != 200:
#             raise MyError(resp, "GET fail on request for satellites. Status code: {resp.status_code}")

    

#         return resp.json()
#     except requests.RequestException as e:
#         print("Error fetching data from API:", e)
#         return None



# Function to fetch data from the API
# This function handles the interaction with the space-track.org API. 
# It sends a POST request to log in and a GET request to retrieve satellite data. 
# It returns the JSON data received from the API or None if an error occurs.

# the request package is initialized with a session object to maintain the state of the login in the main() function.

def fetch_data_from_api(session):
    try:
        # need to log in first. note that we get a 200 to say the web site got the data, not that we are logged in.
        resp = session.post(uriBase + requestLogin, data=siteCred)
        if resp.status_code != 200:
            raise Exception(f"POST fail on login. Status code: {resp.status_code}")


        # this query picks up whatever the requestGPdata variable contians.
        # Stated at the Global variables. It is a string that contains the URL query to get the data from the API.
        # Note - a 401 failure shows you have bad credentials
        resp = session.get(uriBase + requestCmdAction + requestGPdata)
        if resp.status_code != 200:
            raise Exception(f"GET fail on request for satellites. Status code: {resp.status_code}")

        data = resp.json()
        if isinstance(data, list):
            # Assuming the data is a list of dictionaries, you may need to adjust this based on the actual structure
            if data:
                return data[0]  # Return the first item of the list
            else:
                print("No data received from the API")
                return None
        else:
            return data
    except requests.RequestException as e:
        print("Error fetching data from API:", e)
        return None
    



# Function to insert data into the database
# This function inserts the retrieved data into the PostgreSQL database. 
# It first checks if the data already exists in the database, and if not, 
# it inserts it into the gp_file table and records the historical change in the gp_file_historical table.
def insert_into_gp_file(conn, data):
    try:
        cursor = conn.cursor() # Create a cursor object to execute SQL queries
        for item in data:
      
            # if the data with the given NORAD_CAT_ID already exists in the gp_file table
            cursor.execute("SELECT COUNT(*) FROM gp_file WHERE NORAD_CAT_ID = %s", (data['NORAD_CAT_ID'],))
            count = cursor.fetchone()[0]
            # If the data does not exist in gp_file, insert it into both gp_file and gp_file_historical tables    
            if count == 0:
                cursor.execute("""
                               INSERT INTO gp_file (NORAD_CAT_ID, modification_timestamp, CCSDS_OMM_VERS, COMMENT, CREATION_DATE, 
                    ORIGINATOR, OBJECT_NAME, OBJECT_ID, CENTER_NAME, REF_FRAME, TIME_SYSTEM, MEAN_ELEMENT_THEORY, EPOCH, 
                    MEAN_MOTION, ECCENTRICITY, INCLINATION, RA_OF_ASC_NODE, ARG_OF_PERICENTER, MEAN_ANOMALY, EPHEMERIS_TYPE, 
                    CLASSIFICATION_TYPE, ELEMENT_SET_NO, REV_AT_EPOCH, BSTAR, MEAN_MOTION_DOT, MEAN_MOTION_DDOT, SEMIMAJOR_AXIS, 
                    PERIOD, APOAPSIS, PERIAPSIS, OBJECT_TYPE, RCS_SIZE, COUNTRY_CODE, LAUNCH_DATE, SITE, DECAY_DATE, FILE, GP_ID, 
                    TLE_LINE0, TLE_LINE1, TLE_LINE2)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (data['NORAD_CAT_ID'], datetime.now(), data['CCSDS_OMM_VERS'], data['COMMENT'], data['CREATION_DATE'], 
                    data['ORIGINATOR'], data['OBJECT_NAME'], data['OBJECT_ID'], data['CENTER_NAME'], data['REF_FRAME'], 
                    data['TIME_SYSTEM'], data['MEAN_ELEMENT_THEORY'], data['EPOCH'], data['MEAN_MOTION'], data['ECCENTRICITY'], 
                    data['INCLINATION'], data['RA_OF_ASC_NODE'], data['ARG_OF_PERICENTER'], data['MEAN_ANOMALY'], 
                    data['EPHEMERIS_TYPE'], data['CLASSIFICATION_TYPE'], data['ELEMENT_SET_NO'], data['REV_AT_EPOCH'], 
                    data['BSTAR'], data['MEAN_MOTION_DOT'], data['MEAN_MOTION_DDOT'], data['SEMIMAJOR_AXIS'], data['PERIOD'], 
                    data['APOAPSIS'], data['PERIAPSIS'], data['OBJECT_TYPE'], data['RCS_SIZE'], data['COUNTRY_CODE'], 
                    data['LAUNCH_DATE'], data['SITE'], data['DECAY_DATE'], data['FILE'], data['GP_ID'], data['TLE_LINE0'], 
                    data['TLE_LINE1'], data['TLE_LINE2'])) 
                
                # Insert the same data into gp_file_historical
                cursor.execute("""
                               INSERT INTO gp_file_historical (NORAD_CAT_ID, gp_file_id, modification_timestamp, CCSDS_OMM_VERS, COMMENT, 
                    CREATION_DATE, ORIGINATOR, OBJECT_NAME, OBJECT_ID, CENTER_NAME, REF_FRAME, TIME_SYSTEM, MEAN_ELEMENT_THEORY, 
                    EPOCH, MEAN_MOTION, ECCENTRICITY, INCLINATION, RA_OF_ASC_NODE, ARG_OF_PERICENTER, MEAN_ANOMALY, EPHEMERIS_TYPE, 
                    CLASSIFICATION_TYPE, ELEMENT_SET_NO, REV_AT_EPOCH, BSTAR, MEAN_MOTION_DOT, MEAN_MOTION_DDOT, SEMIMAJOR_AXIS, 
                    PERIOD, APOAPSIS, PERIAPSIS, OBJECT_TYPE, RCS_SIZE, COUNTRY_CODE, LAUNCH_DATE, SITE, DECAY_DATE, FILE, GP_ID, 
                    TLE_LINE0, TLE_LINE1, TLE_LINE2)
                    SELECT * FROM gp_file WHERE NORAD_CAT_ID = %s
                """, (data['NORAD_CAT_ID'],))

                print("New data inserted into gp_file")
                conn.commit() # Commit the transaction
            else:
                print("Data already exists in gp_file")

    except psycopg2.Error as e:
        print("Error inserting data into gp_file:", e)

# Main function
# This is the main function that orchestrates the entire process. 
# It reads database credentials from a configuration file, 
# establishes a connection to the database, initializes a session for API requests, 
# continuously fetches data from the API, and inserts it into the database in an infinite loop.       
def main():
    # reads the file with the database credentials.
    config = configparser.ConfigParser()
    config.read(r'C:\Users\Bananberg\Desktop\Space_info\SSC\projects\SSC_database\test_db\database\database_config.ini')

    host = config.get("tables","host")
    dbname = config.get('tables', 'dbname')
    user = config.get('tables', 'user')
    password = config.get('tables', 'password')
    port = config.get('tables', 'port')

    # config_path = os.path.join(os.getcwd(), 'database_config.ini')
    # config = configparser.ConfigParser()
    # config.read(config_path)


    # Establish a connection to the PostgreSQL database
    conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)


    # use requests package to drive the RESTful session with space-track.org
    session = requests.Session()
    siteCred = {'identity': user, 'password': password}

    while True:
        data = fetch_data_from_api(session)
        if data:
            insert_into_gp_file(conn, data)
            print("Resting for 5 seconds...")
        time.sleep(5)

    conn.close()

if __name__ == "__main__":
    main()

