
# THIS SCIRPT IS A MODIFIED VERSION OF THE insert_orbital_info_auto.py SCRIPT.
###################################################################################################
###################################################################################################
## IF HTERER IS ANY PROBLEM WITH THE INSERTION OF DATA INTO THE DATABASE, THE FOLLOWING FILE:
# insert_orbital_info_auto.py CAN BE USED TO INSERT DATA INTO THE DATABASE. 


import os
import time
import requests
import psycopg2
import hashlib
import logging
import configparser
from psycopg2 import sql
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler







def configure_logging():
    """
    Configure logging settings.
    """
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    script_directory = os.path.dirname(os.path.abspath(__file__))  # Directory of the current script
    # Define log file and format
    LOG_DIRECTORY = os.path.join(script_directory, "fetch_log")  # Path to fetch_log folder
    if not os.path.exists(LOG_DIRECTORY):
        os.makedirs(LOG_DIRECTORY)
    LOG_FILE = os.path.join(LOG_DIRECTORY, 'automatic_insert_orbital_info_db.log')
    max_bytes = 5 * 1024 * 1024  # 5 MB in bytes (max log file size before rotation)
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=max_bytes, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')####################################################### DELETE THIS AFTER TESTING
    formatter.converter = time.gmtime  # Convert timestamps to UTC time ############################################################## DELETE THIS AFTER TESTING
    file_handler.setFormatter(formatter)

    # Add file handler to logger
    logger.addHandler(file_handler)




def read_config():
    """
    Read configuration from config file.
    """
    config = configparser.ConfigParser()
    # Specify the path to the config file
    config_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'config', 'config.ini')
    config.read(config_file_path)
    return config





def login_to_space_track(uriBase, requestLogin, siteCred):
    """
    Log in to space-track.org using provided credentials.
    """
    try:
        with requests.Session() as session:
            # Send POST request to log in
            resp = session.post(uriBase + requestLogin, data=siteCred)
            resp.raise_for_status()
            logging.info("Logged in successfully to space-track.org.")
            return session
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to login to space-track.org: {str(e)}")
        raise






def fetch_satellite_data(session, uriBase, requestCmdAction, any):
    # """
    # Fetch satellite data from space-track.org.
    # """
    # max_retries = 3
    # retry_interval = 60  # 60 seconds retry interval

    # for attempt in range(max_retries):
    #     try:
    #         # Send GET request to fetch satellite data
    #         resp = session.get(uriBase + requestCmdAction + any)
    #         resp.raise_for_status()
    #         logging.info("Satellite data fetched successfully.")
    #         return resp.json()
    #     except requests.exceptions.RequestException as e:
    #         logging.error(f"Failed to fetch satellite data: {str(e)}")
    #         if isinstance(e, requests.exceptions.ConnectionError) and isinstance(e.__cause__, OSError):
    #             # Pause execution before retrying
    #             logging.info(f"Pausing script for {retry_interval} seconds before retrying...")
    #             time.sleep(retry_interval)
    #         else:
    #             logging.error("Unhandled request exception occurred. Exiting...")
    #             raise

    # # If all retries fail, raise an error
    # logging.error("Failed to fetch satellite data after multiple attempts.")
    # raise RuntimeError("Failed to fetch satellite data after multiple attempts")


    """
    Fetch satellite data from space-track.org.
    """
    try:
        # Send GET request to fetch satellite data
        resp = session.get(uriBase + requestCmdAction + any) #########  the query parameter. 
        resp.raise_for_status()
        logging.info("Satellite data fetched successfully.")
        return resp.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch satellite data: {str(e)}")
        raise





####################################################################################################
############### ADDED TODAY 10/04/24 ##############################################
#### NOT TESTED ###################################################################

# def retry_connection():
#     """
#     Function to retry establishing a database connection.
#     """
#     max_retries = 3
#     retry_interval = 10

#     for attempt in range(1, max_retries + 1):
#         logging.info(f"Retrying database connection... Attempt {attempt}/{max_retries}")
#         try:
#             config = read_config()
#             host = config.get('tables', 'host')
#             dbname = config.get('tables', 'dbname')
#             user = config.get('tables', 'user')
#             password = config.get('tables', 'password')
#             port = config.get('tables', 'port')

#             conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
#             logging.info("Database connection re-established.")
#             return conn
#         except psycopg2.OperationalError as e:
#             logging.error(f"Failed to connect to the database: {str(e)}")
#             if attempt < max_retries:
#                 logging.info(f"Waiting {retry_interval} seconds before retrying...")
#                 time.sleep(retry_interval)
#         except Exception as e:
#             logging.error(f"An unexpected error occurred during connection retry: {str(e)}")
#             if attempt < max_retries:
#                 logging.info(f"Waiting {retry_interval} seconds before retrying...")
#                 time.sleep(retry_interval)

#     logging.error("Failed to establish database connection after multiple attempts.")
#     raise RuntimeError("Failed to establish database connection after multiple attempts")

####################################################################################################
####################################################################################################






def insert_data_into_database(conn, fetched_data):
    """
    Insert fetched data into PostgreSQL database. With added hashing and a counter that keeps track
    of the number of data points inserted and skipped.
    """
    try:
        with conn.cursor() as cur:
            inserted_count = 0
            skipped_count = 0
            for obj in fetched_data:
                obj_str = str(obj)
                obj_hash = hashlib.sha256(obj_str.encode()).hexdigest()
                # Check if the data is already present in the database
                cur.execute(sql.SQL("SELECT COUNT(*) FROM gp WHERE data_hash = %s"), (obj_hash,))
                count = cur.fetchone()[0]
                if count == 0:
                    try:
                        # Insert data into the database
                        cur.execute(sql.SQL("""
                            INSERT INTO gp (
                            insertion_date, data_hash, NORAD_CAT_ID, CREATION_DATE, EPOCH, ORIGINATOR, OBJECT_NAME,
                            OBJECT_ID, CENTER_NAME, REF_FRAME, TIME_SYSTEM, MEAN_ELEMENT_THEORY, MEAN_MOTION,
                            ECCENTRICITY, INCLINATION, RA_OF_ASC_NODE, ARG_OF_PERICENTER, MEAN_ANOMALY, EPHEMERIS_TYPE,
                            CLASSIFICATION_TYPE, CCSDS_OMM_VERS, COMMENT, ELEMENT_SET_NO, REV_AT_EPOCH, BSTAR,
                            MEAN_MOTION_DOT, MEAN_MOTION_DDOT, SEMIMAJOR_AXIS, PERIOD, APOAPSIS, PERIAPSIS,
                            OBJECT_TYPE, RCS_SIZE, COUNTRY_CODE, LAUNCH_DATE, SITE, DECAY_DATE, FILE, GP_ID,
                            TLE_LINE0, TLE_LINE1, TLE_LINE2
                        ) VALUES (
                            CURRENT_TIMESTAMP, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        """), (
                            obj_hash, obj['NORAD_CAT_ID'], obj['CREATION_DATE'], obj['EPOCH'], obj['ORIGINATOR'],
                            obj['OBJECT_NAME'], obj['OBJECT_ID'], obj['CENTER_NAME'], obj['REF_FRAME'],
                            obj['TIME_SYSTEM'], obj['MEAN_ELEMENT_THEORY'], obj['MEAN_MOTION'], obj['ECCENTRICITY'],
                            obj['INCLINATION'], obj['RA_OF_ASC_NODE'], obj['ARG_OF_PERICENTER'], obj['MEAN_ANOMALY'],
                            obj['EPHEMERIS_TYPE'], obj['CLASSIFICATION_TYPE'], obj['CCSDS_OMM_VERS'], obj['COMMENT'],
                            obj['ELEMENT_SET_NO'], obj['REV_AT_EPOCH'], obj['BSTAR'], obj['MEAN_MOTION_DOT'], obj['MEAN_MOTION_DDOT'],
                            obj['SEMIMAJOR_AXIS'], obj['PERIOD'], obj['APOAPSIS'], obj['PERIAPSIS'], obj['OBJECT_TYPE'],
                            obj['RCS_SIZE'], obj['COUNTRY_CODE'], obj['LAUNCH_DATE'], obj['SITE'], obj['DECAY_DATE'],
                            obj['FILE'], obj['GP_ID'], obj['TLE_LINE0'], obj['TLE_LINE1'], obj['TLE_LINE2']
                        ))
                        inserted_count += 1 # Increment the counter                                                         # {obj_hash}
                        logging.info(f"Inserted NORAD_CAT_ID: {obj['NORAD_CAT_ID']} with SpaceTrack creation date in UTC: {obj['CREATION_DATE']}")
                    except psycopg2.IntegrityError as e:
                        logging.error(f"Error inserting NORAD_CAT_ID: {obj['NORAD_CAT_ID']}: {str(e)}")
                        conn.rollback()
                        continue
                else:
                    skipped_count += 1
                    #logging.warning(f"Skipped duplicate NORAD_CAT_ID: {obj['NORAD_CAT_ID']} with SpaceTrack creation date in UTC: {obj['CREATION_DATE']}")
            conn.commit()
        logging.info(f"Inserted {inserted_count} data points successfully.")
        logging.info(f"Skipped {skipped_count} duplicate data points.")

    except psycopg2.DatabaseError as e:
        logging.error(f"Database error occurred: {str(e)}")
        conn.rollback()
        raise






def populate():
    """
    Main function to populate the database with satellite data.
    """
    try:
        config = read_config()
        api_username = config.get('API', 'username')
        api_password = config.get('API', 'password')
        uriBase = "https://www.space-track.org"
        requestLogin = "/ajaxauth/login"
        requestCmdAction = "/basicspacedata/query"


        populate = f'/class/gp/DECAY_DATE/null-val/orderby/norad_cat_id/format/json' ### THE INITAL POPULATION, USED ONCE ONLY TO POPULATE THE DATABASE.
       

        gp_id = f'/class/gp/gp_id/%3E255143244/format/json/orderby/norad_cat_id' # gets the data since the given gp_id number.

        a = f'/class/gp/CREATION_DATE/%3Enow-1/orderby/CREATION_DATE%20asc/format/json' # gives data from the last 24 hours. in creation_date order.

        b = f'/class/gp/CREATION_DATE/%3Enow-0.5/orderby/CREATION_DATE%20asc/format/json' # gives data from the last 12 hours. in creation_date order.

        x = f'/class/gp/CREATION_DATE/%3Enow-0.125/orderby/CREATION_DATE%20asc/format/json' # gives data from the last 3 hours. in creation_date order.

        
        query = f'/class/gp/CREATION_DATE/%3Enow-0.0068/orderby/CREATION_DATE%20asc/format/json' # WORKS as of 22/04/24 22:13 



        siteCred = {'identity': api_username, 'password': api_password}

        


        session = login_to_space_track(uriBase, requestLogin, siteCred)         #  
        fetched_data = fetch_satellite_data(session, uriBase, requestCmdAction, query) ######## Insertion query here.
                                                                                #    

        host = config.get('tables', 'host')
        dbname = config.get('tables', 'dbname')
        user = config.get('tables', 'user')
        password = config.get('tables', 'password')
        port = config.get('tables', 'port')


        # Retry database connection if necessary
        for attempt in range(3):
            try:
                with psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port) as conn:
                    insert_data_into_database(conn, fetched_data)
                break  # Break out of loop if connection and insertion are successful
            except psycopg2.OperationalError as e:
                logging.error(f"Failed to connect to the database: {str(e)}")
                if attempt < 2:
                    logging.info("Waiting 10 seconds before retrying...")
                    time.sleep(10)
        else:
            logging.error("Failed to establish database connection after multiple attempts.")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")







if __name__ == "__main__":
    configure_logging()

    # Continuously run the populate function
    while True:
        try:
            populate()
           # Snoozing for 60 secs for rate limit reasons (max 20/min and 200/hr)
            time.sleep(60)
        except KeyboardInterrupt:
          
            logging.info("PROGRAM TERMINATED BY USER ###############################################")
            break
        except Exception as e:
            # Log any unexpected errors
            logging.error(f"An unexpected error occurred: {str(e)}")





###################################################################################################
###################################################################################################
# Function Definitions:

# Functions are defined for tasks like configuring logging, reading configuration settings,
# logging in to space-track.org, fetching satellite data, and inserting it into the database.
# Main Execution:

# The script's main block configures logging, then enters a loop to continuously fetch and insert data into the database. 
# It handles exceptions and interrupts gracefully.
# Error Handling:

# The script includes robust error handling to catch and log exceptions during execution.
# Logging:

# Extensive logging provides detailed information about the execution process, including errors and warnings.
# Configuration Management:

# Configuration settings are read from an external config file for flexibility.