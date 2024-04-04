import os
import requests
import logging
import datetime
import configparser
import psycopg2




# Construct the full path to the config.ini file
config_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'config', 'config.ini')

# Initialize config parser and read the configuration file
config = configparser.ConfigParser()
config.read(config_file_path)

# Your credientials are stored in directory config and file named config.ini.
# login and request URL components to access the RESTful service at spce-track.org.
uriBase                = "https://www.space-track.org"
requestLogin           = "/ajaxauth/login"
requestCmdAction       = "/basicspacedata/query"
# Get API credentials
api_username = config.get('API', 'username')
api_password = config.get('API', 'password')

siteCred = {'identity': api_username, 'password': api_password}


requestGPdata = f'/class/gp/decay_date/null-val/epoch/%3Enow-30/orderby/norad_cat_id/format/json'


#The recommended URL for retrieving the newest propagable element set for all on-orbit objects is:
# /class/gp/decay_date/null-val/epoch/%3Enow-30/orderby/norad_cat_id/format/json





# Get database connection parameters
host = config.get('tables', 'host')
dbname = config.get('tables', 'dbname')
user = config.get('tables', 'user')
password = config.get('tables', 'password')
port = config.get('tables', 'port')









# Set up logging
log_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'GP_update_and_migrate.log')
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s - line: %(lineno)d - %(message)s')

# Read configuration from file
config = configparser.ConfigParser()
config_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config', 'config.ini')
config.read(config_file_path)






# Define function to update database with fetched data
def update_database():
    try:
        # Fetch data from RESTful service
        fetched_data = fetch_data_from_service()
        
        if fetched_data:
            # Update database with fetched data
            num_updated = store_data_in_postgresql(fetched_data)
            logging.info("Number of objects updated in database: %d", num_updated)
        else:
            logging.info("No data fetched.")
    except Exception as e:
        logging.error("Error occurred during database update: %s", e)






# Define function to fetch data from RESTful service
def fetch_data_from_service():
    with requests.Session() as session:
        # Perform login
        resp = session.post(uriBase + requestLogin, data=siteCred)
        resp.raise_for_status()  # Raise exception for non-200 response
        logging.info("Login successful")
        
        # Fetch data
        resp = session.get(uriBase + requestCmdAction + requestGPdata)
        resp.raise_for_status()  # Raise exception for non-200 response
        logging.info("Data fetched successfully")
        return resp.json()






# Define function to update database with fetched data
def store_data_in_postgresql(data):
    # Connect to PostgreSQL database
    conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
    cursor = conn.cursor()

    try:
        # Perform database update
        num_updated = 0
        for item in data:
            # Update database with fetched data
            # Example update query:
            # cursor.execute("UPDATE your_table SET column1 = %s, column2 = %s WHERE id = %s", (item['value1'], item['value2'], item['id']))
            cursor.execute("""
            UPDATE gp_file
            SET CCSDS_OMM_VERS = %s, COMMENT = %s, modification_timestamp = CURRENT_TIMESTAMP, CREATION_DATE = %s, ORIGINATOR = %s, OBJECT_NAME = %s, OBJECT_ID = %s, CENTER_NAME = %s,
                REF_FRAME = %s, TIME_SYSTEM = %s, MEAN_ELEMENT_THEORY = %s, EPOCH = %s, MEAN_MOTION = %s, ECCENTRICITY = %s,
                INCLINATION = %s, RA_OF_ASC_NODE = %s, ARG_OF_PERICENTER = %s, MEAN_ANOMALY = %s, EPHEMERIS_TYPE = %s,
                CLASSIFICATION_TYPE = %s, ELEMENT_SET_NO = %s, REV_AT_EPOCH = %s, BSTAR = %s, MEAN_MOTION_DOT = %s,
                MEAN_MOTION_DDOT = %s, SEMIMAJOR_AXIS = %s, PERIOD = %s, APOAPSIS = %s, PERIAPSIS = %s,
                OBJECT_TYPE = %s, RCS_SIZE = %s, COUNTRY_CODE = %s, LAUNCH_DATE = %s, SITE = %s,
                DECAY_DATE = %s, FILE = %s, GP_ID = %s, TLE_LINE0 = %s, TLE_LINE1 = %s,
                TLE_LINE2 = %s    
            WHERE NORAD_CAT_ID = %s           
        """, (item['CCSDS_OMM_VERS'], item['COMMENT'], item['CREATION_DATE'], item['ORIGINATOR'], item['OBJECT_NAME'], 
              item['OBJECT_ID'], item['CENTER_NAME'], item['REF_FRAME'], item['TIME_SYSTEM'], item['MEAN_ELEMENT_THEORY'], 
              item['EPOCH'], item['MEAN_MOTION'], item['ECCENTRICITY'], item['INCLINATION'], item['RA_OF_ASC_NODE'], 
              item['ARG_OF_PERICENTER'], item['MEAN_ANOMALY'], item['EPHEMERIS_TYPE'], item['CLASSIFICATION_TYPE'], 
              item['ELEMENT_SET_NO'], item['REV_AT_EPOCH'], item['BSTAR'], item['MEAN_MOTION_DOT'], item['MEAN_MOTION_DDOT'], 
              item['SEMIMAJOR_AXIS'], item['PERIOD'], item['APOAPSIS'], item['PERIAPSIS'], item['OBJECT_TYPE'], 
              item['RCS_SIZE'], item['COUNTRY_CODE'], item['LAUNCH_DATE'], item['SITE'], item['DECAY_DATE'], 
              item['FILE'], item['GP_ID'], item['TLE_LINE0'], item['TLE_LINE1'], item['TLE_LINE2'], item['NORAD_CAT_ID']))
        
            num_updated += 1
            #logging.info("Updated object with NORAD_CAT_ID: %s", item['NORAD_CAT_ID'])  # Log the updated object
        conn.commit()
        logging.info("Data insertion into PostgreSQL successful.")
        return num_updated
    finally:
        cursor.close()
        conn.close()
        logging.info("Database connection closed.")

if __name__ == "__main__":
    update_database()
