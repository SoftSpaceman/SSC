# This script is bases upon these chats from OpenAI:

# https://chat.openai.com/share/1a77781a-99c2-4a92-81f4-45c37da1870d

# https://chat.openai.com/share/342972b7-88e8-48d9-95ed-158f3cbd92e9

# https://chat.openai.com/share/a31ef68d-e87d-4a84-ae1b-a4ba548e449e

# https://chat.openai.com/share/663e56c5-efc3-4e32-abad-535abda56de9

import os
import time
import logging
import requests
import psycopg2
import configparser


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MyError(Exception):
    """Custom exception class."""
    def __init__(self, args):
        """Initialize MyError instance."""
        super().__init__("My exception was raised with arguments {0}".format(args))
        self.args = args





# # Get the directory path of the current script
# script_dir = os.path.dirname(os.path.realpath(__file__))

# # Navigate to the parent directory (one level up from the current script directory)
# parent_dir = os.path.dirname(script_dir)

# # Construct the path to the config directory
# config_dir = os.path.join(parent_dir, 'config')

# # Construct the full path to the config.ini file
# config_file_path = os.path.join(config_dir, 'config.ini')

# # Initialize config parser
# config = configparser.ConfigParser()

# # Read the configuration file
# config.read(config_file_path)

# Construct the full path to the config.ini file
config_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'config', 'config.ini')

# Initialize config parser and read the configuration file
config = configparser.ConfigParser()
config.read(config_file_path)


# Get API credentials
api_username = config.get('API', 'username')
api_password = config.get('API', 'password')

siteCred = {'identity': api_username, 'password': api_password}


# Get database connection parameters
host = config.get('tables', 'host')
dbname = config.get('tables', 'dbname')
user = config.get('tables', 'user')
password = config.get('tables', 'password')
port = config.get('tables', 'port')


# Global variables
uriBase = "https://www.space-track.org"
requestLogin = "/ajaxauth/login"
requestCmdAction = "/basicspacedata/query"
requestGPdata = f'/class/gp/decay_date/null-val/epoch/%3Enow-30/orderby/norad_cat_id/format/json'
# #he recommended URL for retrieving the newest propagable element set for all on-orbit objects is: 
# # /class/gp/decay_date/null-val/epoch/%3Enow-30/orderby/norad_cat_id/format/json




def fetch_data_from_api(session):

    try:
        # Perform a POST request to login to the API
        resp = session.post(uriBase + requestLogin, data=siteCred)
        if resp.status_code != 200:
            raise Exception(f"POST fail on login. Status code: {resp.status_code}")

        logging.info("Login successful. Proceeding to fetch data.")

        # Perform a GET request to fetch satellite data
        resp = session.get(uriBase + requestCmdAction + requestGPdata)
        if resp.status_code != 200:
            raise Exception(f"GET fail on request for satellites. Status code: {resp.status_code}")

        logging.info("Data fetched successfully.")

        # Parse the JSON response
        data = resp.json()
        if isinstance(data, list):
            if data:
                return data[0]  # Return the first item if data is a list
            else:
                logging.warning("No data received from the API")
                return None  # Return None if no data received
        else:
            return data  # Return the response if it's not a list
    except requests.RequestException as e:
        logging.error("Error fetching data from API: %s", e)  # Log any exceptions that occur during API requests
        return None

# Example usage
# session = requests.Session()
# fetch_data_from_api(session)





def update_postgres_data(conn, data):
    cursor = None
    try:
        cursor = conn.cursor()
 
        cursor.execute("""
            UPDATE gp_file
            SET CCSDS_OMM_VERS = %s, COMMENT = %s, CREATION_DATE = %s, ORIGINATOR = %s, OBJECT_NAME = %s, OBJECT_ID = %s, CENTER_NAME = %s,
                REF_FRAME = %s, TIME_SYSTEM = %s, MEAN_ELEMENT_THEORY = %s, EPOCH = %s, MEAN_MOTION = %s, ECCENTRICITY = %s,
                INCLINATION = %s, RA_OF_ASC_NODE = %s, ARG_OF_PERICENTER = %s, MEAN_ANOMALY = %s, EPHEMERIS_TYPE = %s,
                CLASSIFICATION_TYPE = %s, ELEMENT_SET_NO = %s, REV_AT_EPOCH = %s, BSTAR = %s, MEAN_MOTION_DOT = %s,
                MEAN_MOTION_DDOT = %s, SEMIMAJOR_AXIS = %s, PERIOD = %s, APOAPSIS = %s, PERIAPSIS = %s,
                OBJECT_TYPE = %s, RCS_SIZE = %s, COUNTRY_CODE = %s, LAUNCH_DATE = %s, SITE = %s,
                DECAY_DATE = %s, FILE = %s, GP_ID = %s, TLE_LINE0 = %s, TLE_LINE1 = %s,
                TLE_LINE2 = %s    
            WHERE NORAD_CAT_ID = %s           
        """, (data['CCSDS_OMM_VERS'], data['COMMENT'], data['CREATION_DATE'], data['ORIGINATOR'], data['OBJECT_NAME'], 
              data['OBJECT_ID'], data['CENTER_NAME'], data['REF_FRAME'], data['TIME_SYSTEM'], data['MEAN_ELEMENT_THEORY'], 
              data['EPOCH'], data['MEAN_MOTION'], data['ECCENTRICITY'], data['INCLINATION'], data['RA_OF_ASC_NODE'], 
              data['ARG_OF_PERICENTER'], data['MEAN_ANOMALY'], data['EPHEMERIS_TYPE'], data['CLASSIFICATION_TYPE'], 
              data['ELEMENT_SET_NO'], data['REV_AT_EPOCH'], data['BSTAR'], data['MEAN_MOTION_DOT'], data['MEAN_MOTION_DDOT'], 
              data['SEMIMAJOR_AXIS'], data['PERIOD'], data['APOAPSIS'], data['PERIAPSIS'], data['OBJECT_TYPE'], 
              data['RCS_SIZE'], data['COUNTRY_CODE'], data['LAUNCH_DATE'], data['SITE'], data['DECAY_DATE'], 
              data['FILE'], data['GP_ID'], data['TLE_LINE0'], data['TLE_LINE1'], data['TLE_LINE2'], data['NORAD_CAT_ID']))
        conn.commit()
        logging.info("Data updated successfully")
        #print("Data updated successfully")
        log_updated_data(data)  # Log the updated data

    except psycopg2.Error as error:
        logging.error("Error while updating PostgreSQL data: %s", error)
        conn.rollback() # Rollback changes to prevent data corruption
       
    except Exception as e:
        print("An unexpected error occurred: %s", e)
        # Handle other exceptions
    finally:
        if cursor:
            cursor.close()  # Close cursor only if it's not None





def log_updated_data(data):
    print("Updated data:")
    for key, value in data.items():
        print(f"{key}: {value}")




def main():
    conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
    session = requests.Session()

    try:
        while True:
            api_data = fetch_data_from_api(session)
            if api_data:
                update_postgres_data(conn, api_data)
                print("Resting for 5 seconds...")
            time.sleep(5)
    except KeyboardInterrupt:
        print("Script interrupted by user")
    finally:
        if conn:
            conn.close()
            print("PostgreSQL connection is closed")

if __name__ == "__main__":
    main()



# def main():


    
#     conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
#     session = requests.Session()

#     while True:
#         api_data = fetch_data_from_api(session)
#         if api_data:
#             update_postgres_data(conn, api_data)
#             print("Resting for 5 seconds...")
#         time.sleep(5)

# if __name__ == "__main__":
#     main()





# import time
# import requests
# import psycopg2
# import configparser

# uriBase = "https://www.space-track.org"
# requestLogin = "/ajaxauth/login"
# requestCmdAction = "/basicspacedata/query"
# requestGPdata = f'/class/gp/NORAD_CAT_ID/%3E20000/orderby/NORAD_CAT_ID%20asc/emptyresult/show'

# config = configparser.ConfigParser()
# config.read(r'C:\Users\Bananberg\Desktop\Space_info\SSC\projects\SSC_database\test_db\api\APIconfig.ini')
# config_db = configparser.ConfigParser()
# config_db.read(r'C:\Users\Bananberg\Desktop\Space_info\SSC\projects\SSC_database\test_db\database\database_config.ini')

# siteCred = {'identity': config.get("configuration", "username"), 'password': config.get("configuration", "password")}
# host = config_db.get("tables", "host")
# dbname = config_db.get('tables', 'dbname')
# user = config_db.get('tables', 'user')
# password = config_db.get('tables', 'password')
# port = config_db.get('tables', 'port')

# def fetch_data_from_api(session):
#     try:
#         resp = session.post(uriBase + requestLogin, data=siteCred)
#         if resp.status_code != 200:
#             raise Exception(f"POST fail on login. Status code: {resp.status_code}")

#         resp = session.get(uriBase + requestCmdAction + requestGPdata)
#         if resp.status_code != 200:
#             raise Exception(f"GET fail on request for satellites. Status code: {resp.status_code}")

#         data = resp.json()
#         if isinstance(data, list):
#             if data:
#                 return data[0]
#             else:
#                 print("No data received from the API")
#                 return None
#         else:
#             return data
#     except requests.RequestException as e:
#         print("Error fetching data from API:", e)
#         return None

# def update_postgres_data(conn, data):
#     try:
#         cursor = conn.cursor()
#         cursor.execute("""
#             UPDATE gp_file
#             SET CCSDS_OMM_VERS = %s, COMMENT = %s, CREATION_DATE = %s, ORIGINATOR = %s, OBJECT_NAME = %s, OBJECT_ID = %s, CENTER_NAME = %s,
#                 REF_FRAME = %s, TIME_SYSTEM = %s, MEAN_ELEMENT_THEORY = %s, EPOCH = %s, MEAN_MOTION = %s, ECCENTRICITY = %s,
#                 INCLINATION = %s, RA_OF_ASC_NODE = %s, ARG_OF_PERICENTER = %s, MEAN_ANOMALY = %s, EPHEMERIS_TYPE = %s,
#                 CLASSIFICATION_TYPE = %s, ELEMENT_SET_NO = %s, REV_AT_EPOCH = %s, BSTAR = %s, MEAN_MOTION_DOT = %s,
#                 MEAN_MOTION_DDOT = %s, SEMIMAJOR_AXIS = %s, PERIOD = %s, APOAPSIS = %s, PERIAPSIS = %s,
#                 OBJECT_TYPE = %s, RCS_SIZE = %s, COUNTRY_CODE = %s, LAUNCH_DATE = %s, SITE = %s,
#                 DECAY_DATE = %s, FILE = %s, GP_ID = %s, TLE_LINE0 = %s, TLE_LINE1 = %s,
#                 TLE_LINE2 = %s    
#             WHERE NORAD_CAT_ID = %s           
#         """, (data['CCSDS_OMM_VERS'], data['COMMENT'], data['CREATION_DATE'], data['ORIGINATOR'], data['OBJECT_NAME'], 
#               data['OBJECT_ID'], data['CENTER_NAME'], data['REF_FRAME'], data['TIME_SYSTEM'], data['MEAN_ELEMENT_THEORY'], 
#               data['EPOCH'], data['MEAN_MOTION'], data['ECCENTRICITY'], data['INCLINATION'], data['RA_OF_ASC_NODE'], 
#               data['ARG_OF_PERICENTER'], data['MEAN_ANOMALY'], data['EPHEMERIS_TYPE'], data['CLASSIFICATION_TYPE'], 
#               data['ELEMENT_SET_NO'], data['REV_AT_EPOCH'], data['BSTAR'], data['MEAN_MOTION_DOT'], data['MEAN_MOTION_DDOT'], 
#               data['SEMIMAJOR_AXIS'], data['PERIOD'], data['APOAPSIS'], data['PERIAPSIS'], data['OBJECT_TYPE'], 
#               data['RCS_SIZE'], data['COUNTRY_CODE'], data['LAUNCH_DATE'], data['SITE'], data['DECAY_DATE'], 
#               data['FILE'], data['GP_ID'], data['TLE_LINE0'], data['TLE_LINE1'], data['TLE_LINE2'], data['NORAD_CAT_ID']))
#         conn.commit()
#         print("Data updated successfully")
#     except (Exception, psycopg2.Error) as error:
#         print("Error while updating PostgreSQL data:", error)
#     finally:
#         if conn:
#             cursor.close()
#             conn.close()
#             print("PostgreSQL connection is closed")

# def main():
#     conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
#     session = requests.Session()

#     while True:
#         api_data = fetch_data_from_api(session)
#         if api_data:
#             update_postgres_data(conn, api_data)
#             print("Resting for 5 seconds...")
#         time.sleep(5)


# if __name__ == "__main__":
#     main()









