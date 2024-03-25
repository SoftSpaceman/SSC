import os
import logging
import requests
import psycopg2
from psycopg2 import sql
import configparser


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

# Get database connection parameters
host = config.get('tables', 'host')
dbname = config.get('tables', 'dbname')
user = config.get('tables', 'user')
password = config.get('tables', 'password')
port = config.get('tables', 'port')

# Logging Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')





# Function to fetch data from API
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

# Function to update PostgreSQL database
def update_database(data):
    
    try:
        # Connect to your PostgreSQL database
        conn = psycopg2.connect( host=host, dbname=dbname, user=user, password=password, port=port)

        logging.info("Connected to PostgreSQL database successfully.")

        # Create a cursor object
        cur = conn.cursor()

        # Execute SQL statements to update the database with fetched data
        # Example: Update a table named 'satellite_data' with the fetched data
        # Assuming the fetched data is a dictionary with keys matching table columns
        if data:
            sql_query = sql.SQL("INSERT INTO gp_file (CCSDS_OMM_VERS, modification_timestamp = CURRENT_TIMESTAMPCOMMENT, CREATION_DATE, ORIGINATOR, OBJECT_NAME, OBJECT_ID, CENTER_NAME, REF_FRAME, TIME_SYSTEM, MEAN_ELEMENT_THEORY, EPOCH, MEAN_MOTION, ECCENTRICITY, INCLINATION, RA_OF_ASC_NODE, ARG_OF_PERICENTER, MEAN_ANOMALY, EPHEMERIS_TYPE, CLASSIFICATION_TYPE, NORAD_CAT_ID, ELEMENT_SET_NO, REV_AT_EPOCH, BSTAR, MEAN_MOTION_DOT, MEAN_MOTION_DDOT, SEMIMAJOR_AXIS, PERIOD, APOAPSIS, PERIAPSIS, OBJECT_TYPE, RCS_SIZE, COUNTRY_CODE, LAUNCH_DATE, SITE, DECAY_DATE, FILE, GP_ID, TLE_LINE0, TLE_LINE1, TLE_LINE2) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
            cur.execute(sql_query, (data.get("CCSDS_OMM_VERS"), data.get("COMMENT"), data.get("CREATION_DATE"), data.get("ORIGINATOR"), data.get("OBJECT_NAME"), 
                                    data.get("OBJECT_ID"), data.get("CENTER_NAME"), data.get("REF_FRAME"), data.get("TIME_SYSTEM"), data.get("MEAN_ELEMENT_THEORY"), 
                                    data.get("EPOCH"), data.get("MEAN_MOTION"), data.get("ECCENTRICITY"), data.get("INCLINATION"), data.get("RA_OF_ASC_NODE"), data.get("ARG_OF_PERICENTER"), data.get("MEAN_ANOMALY"), data.get("EPHEMERIS_TYPE"), data.get("CLASSIFICATION_TYPE"), data.get("NORAD_CAT_ID"), 
                                    data.get("ELEMENT_SET_NO"), data.get("REV_AT_EPOCH"), data.get("BSTAR"), data.get("MEAN_MOTION_DOT"), data.get("MEAN_MOTION_DDOT"), data.get("SEMIMAJOR_AXIS"), data.get("PERIOD"), data.get("APOAPSIS"), data.get("PERIAPSIS"), data.get("OBJECT_TYPE"), data.get("RCS_SIZE"), data.get("COUNTRY_CODE"), data.get("LAUNCH_DATE"), data.get("SITE"), data.get("DECAY_DATE"), 
                                    data.get("FILE"), data.get("GP_ID"), data.get("TLE_LINE0"), data.get("TLE_LINE1"), data.get("TLE_LINE2")))
            logging.info("Data inserted into database successfully.")
        else:
            logging.warning("No data to insert into the database.")

        # Commit the transaction
        conn.commit()
    except psycopg2.IntegrityError as e:
        # Handle duplicate key violation
        logging.warning("Duplicate key violation: %s", e)
        conn.rollback()  # Rollback the transaction to avoid partial insertion
    except psycopg2.Error as e:
        logging.error("Error updating PostgreSQL database: %s", e)
        
    finally:
        # Close database connection
        if conn is not None:
            conn.close()
            logging.info("PostgreSQL database connection closed.")



# Main function
def main():
    # Create a session for API requests
    with requests.Session() as session:
        data = fetch_data_from_api(session)
        update_database(data)

if __name__ == "__main__":
    main()


