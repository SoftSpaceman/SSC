
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
from logging.handlers import RotatingFileHandler





def configure_logging():
    """
    Configure logging settings.
    """
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Define log file and format
    LOG_DIRECTORY = "fetch_log"
    if not os.path.exists(LOG_DIRECTORY):
        os.makedirs(LOG_DIRECTORY)
    LOG_FILE = os.path.join(LOG_DIRECTORY, 'automatic_insert_orbital_info_db.log')
    max_bytes = 10 * 1024 * 1024  # 10 MB in bytes (max log file size before rotation)
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=max_bytes, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
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






def fetch_satellite_data(session, uriBase, requestCmdAction, any): ############### the query parameter.

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

def retry_connection():
    """
    Function to retry establishing a database connection.
    """
   

    max_retries = 3  # Maximum number of retries
    retry_interval = 10  # Interval between retries in seconds

    for attempt in range(1, max_retries + 1):
        logging.info(f"Retrying database connection... Attempt {attempt}/{max_retries}")
        try:
            # Read the config file. 
            config = read_config()
            host = config.get('database', 'host')
            dbname = config.get('database', 'dbname')
            user = config.get('database', 'user')
            password = config.get('database', 'password')
            port = config.get('database', 'port')

            # Attempt to establish the database connection again
            conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
            logging.info("Database connection re-established.")
            return conn  # Return the connection object if successful
        except psycopg2.OperationalError as e:
            logging.error(f"Failed to connect to the database: {str(e)}")
            # Wait before the next retry
            time.sleep(retry_interval)
        except Exception as e:
            logging.error(f"An unexpected error occurred during connection retry: {str(e)}")
            # Wait before the next retry
            time.sleep(retry_interval)

    # If max retries exceeded without success, raise an error or handle it accordingly
    logging.error("Failed to establish database connection after multiple attempts.")
    raise RuntimeError("Failed to establish database connection after multiple attempts")

####################################################################################################
####################################################################################################






def insert_data_into_database(conn, fetched_data):
    """
    Insert fetched data into PostgreSQL database.
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
                        inserted_count += 1
                        logging.info(f"Inserted NORAD_CAT_ID: {obj['NORAD_CAT_ID']} with hash: {obj_hash}")
                    except psycopg2.IntegrityError as e:
                        logging.error(f"Error inserting NORAD_CAT_ID: {obj['NORAD_CAT_ID']}: {str(e)}")
                        conn.rollback()
                        continue
                else:
                    skipped_count += 1
                    logging.warning(f"Skipped duplicate NORAD_CAT_ID: {obj['NORAD_CAT_ID']} with hash: {obj_hash}")
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

       

        xx = f'/class/gp/creation_date/%3Enow-0.0006944/orderby/norad_cat_id/format/json' ######### 0.00069444 days = data from now and 1 minuts back. TRY IT OUT!
        #################################################################################
        x = f'/class/gp/creation_date/%3Enow-0.0069444/orderby/norad_cat_id/format/json' ######### 0.0069444 days = data from now and 10 minuts back. WORKS!
        #################################################################################
        y = f'/class/gp/creation_date/%3Enow-0.0208333/orderby/norad_cat_id/format/json'######### 0.0208333 days = data from now and 30 minuts back. WORKS! 
        #################################################################################
        a = f'/class/gp/creation_date/%3Enow-0.0416667/orderby/norad_cat_id/format/json'######### 0.0416667 days = data from now and 1 hour back. WORKS
        #################################################################################
        b = f'/class/gp/creation_date/%3Enow-0.125/orderby/norad_cat_id/format/json'######### 0.125 days = data from now and 3 hours back. WORKS!  
        #################################################################################
        c = f'/class/gp/creation_date/%3Enow-0.5/orderby/norad_cat_id/format/json'######### 0.5 = data from now and 12 hours back. WORKS! 
        #################################################################################
        d = f'/class/gp/creation_date/%3Enow-1/orderby/norad_cat_id/format/json'######### 1 = data from now and 24 hours back. WORKS! 
        #################################################################################
        z = f'/class/gp/DECAY_DATE/null-val/orderby/norad_cat_id/format/json' ### THE INITAL POPULATION, USED ONCE ONLY TO POPULATE THE DATABASE.
        ########################################################################  TAKES ALL DATA WITHOUT DECAY DATE. 

        siteCred = {'identity': api_username, 'password': api_password}

        


        session = login_to_space_track(uriBase, requestLogin, siteCred)         #  
        fetched_data = fetch_satellite_data(session, uriBase, requestCmdAction, y) ######## Insertion query here.
                                                                                #    

        host = config.get('tables', 'host')
        dbname = config.get('tables', 'dbname')
        user = config.get('tables', 'user')
        password = config.get('tables', 'password')
        port = config.get('tables', 'port')




        with psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port) as conn:
            insert_data_into_database(conn, fetched_data)

    except psycopg2.OperationalError as e:
        # Retry the connection or log an error message
        logging.error(f"Failed to connect to the database: {str(e)}")
        retry_connection()
    except Exception as e:    
        logging.error(f"An error occurred: {str(e)}")





if __name__ == "__main__":
    configure_logging()

    # Continuously run the populate function
    while True:
        try:
            populate()
            # Sleep for 60 x 8 = 480  seconds before running again = 8 minutes
            # 480 x 2 = 960 seconds = 16 minutes
            time.sleep(960)
        except KeyboardInterrupt:
            # Log message if program is terminated by user
            logging.info("########### PROGRAM TERMINATED BY USER ###########")
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