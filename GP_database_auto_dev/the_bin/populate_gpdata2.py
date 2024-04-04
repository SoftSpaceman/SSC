import os
import logging
import schedule
import time
import configparser
import requests
import psycopg2
from psycopg2 import sql
import hashlib
from logging.handlers import RotatingFileHandler

# Create a logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create a file handler and set the formatter
LOG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'populate_gpdata2.log')
file_handler = RotatingFileHandler(LOG_FILE, backupCount=3)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the file handler to the root logger
logging.getLogger('').addHandler(file_handler)

# Log a message indicating that the logging process has started
logging.info("Logging process started.")

def populate_once():
    try:
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

        requestDATApopulate = f'/class/gp/DECAY_DATE/null-val/orderby/NORAD_CAT_ID%20asc/emptyresult/show'





        # Get database connection parameters
        host = config.get('tables2', 'host')
        dbname = config.get('tables2', 'dbname')
        user = config.get('tables2', 'user')
        password = config.get('tables2', 'password')
        port = config.get('tables2', 'port')

        # Main script
        with requests.Session() as session:
            # Login to space-track.org
            logging.info("Logging in to space-track.org...")
            resp = session.post(uriBase + requestLogin, data=siteCred)
            resp.raise_for_status()  # Raise an error for bad response status
            logging.info("Logged in successfully.")

            # Fetch satellite data
            logging.info("Fetching satellite data...")
            resp = session.get(uriBase + requestCmdAction + requestDATApopulate)
            resp.raise_for_status()  # Raise an error for bad response status
            logging.info("Satellite data fetched successfully.")

            # Print fetched data
            fetched_data = resp.json()

            # Establish connection to PostgreSQL database
            with psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port) as conn:
                # Create a cursor object
                with conn.cursor() as cur:
                    # Insert fetched data and their hashes into the existing table
                    inserted_count = 0
                    skipped_count = 0
                    for obj in fetched_data:
                        try:
                            obj_str = str(obj)
                            obj_hash = hashlib.sha256(obj_str.encode()).hexdigest()
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
                            if 'duplicate key value' in str(e):
                                skipped_count += 1
                                logging.warning(f"Skipped duplicate NORAD_CAT_ID: {obj['NORAD_CAT_ID']} with hash: {obj_hash}")
                            else:
                                logging.error(f"Error inserting NORAD_CAT_ID: {obj['NORAD_CAT_ID']}: {str(e)}")
                            conn.rollback()
                            #logging.warning(f"Skipped duplicate NORAD_CAT_ID: {obj['NORAD_CAT_ID']} with hash: {obj_hash}")
                    conn.commit()

        logging.info(f"Inserted {inserted_count} data points successfully.")
        logging.info(f"Skipped {skipped_count} duplicate data points.")

        # For testing the logging
        #logging.info("This is a test log message.")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        
        # Log a message indicating that database population is completed
        logging.info("Database population completed.")

