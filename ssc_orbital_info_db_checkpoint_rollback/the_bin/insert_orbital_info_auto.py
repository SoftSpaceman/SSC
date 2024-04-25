
############################################################################################################
# THIS SCRIPT FETCHES DATA FROM 12h back. 


import os
import requests
import psycopg2
import hashlib
import logging
import configparser
from psycopg2 import sql
from logging.handlers import RotatingFileHandler


# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

LOG_DIRECTORY = "log"
if not os.path.exists(LOG_DIRECTORY):
    os.makedirs(LOG_DIRECTORY)

LOG_FILE = os.path.join(LOG_DIRECTORY, 'automatic_insert_orbital_info_db.log')
file_handler = RotatingFileHandler(LOG_FILE, backupCount=3)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)



def populate():
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


        
        # THESE QUERYS GIVES THE LATES CREATIOND DATE FROM THE PAST 12, 3 or 10 minutes.
        # Using these will start historical data storage for the future.
        # gives the lates data from the past 12 h 
        a =  f'/class/gp/creation_date/%3Enow-0.5/orderby/norad_cat_id/format/json'

        # This will get data taht ahs been create within 3h of teh reques . 
        b = f'/class/gp/creation_date/%3Enow-0.125/orderby/norad_cat_id/format/json'
        
        # latest data from the past 10 minutes
        c =  f'/class/gp/creation_date/%3Enow-0.0069/orderby/norad_cat_id/format/json'

        # lates data from 5 minuts ago. 
        d = f'/class/gp/creation_date/%3Enow-0.0035/orderby/norad_cat_id/format/json'

        # THESE QUERYS GIVES CREATION DATE FROM THE PAST 12, 3 or 10 minutes. OF OBEJECTS THAT HAS NO DECAY DATE. 
        # THIS IS ONLY TO POULATE THE DATABSE IF NEEDED..   Not having decay_date in the query will leave updates that include decay date out.




        # Get database connection parameters
        host = config.get('tables', 'host')
        dbname = config.get('tables', 'dbname')
        user = config.get('tables', 'user')
        password = config.get('tables', 'password')
        port = config.get('tables', 'port')



        # Main script
        with requests.Session() as session:
            # Login to space-track.org
            logging.info("Logging in to space-track.org...")
            resp = session.post(uriBase + requestLogin, data=siteCred)
            resp.raise_for_status()  # Raise an error for bad response status
            logging.info("Logged in successfully.")

            # Fetch satellite data
            logging.info("Fetching satellite data...")
            ################################################################################
            resp = session.get(uriBase + requestCmdAction + b)  ############################ Insertion query here. 
            ################################################################################
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
                        obj_str = str(obj)
                        obj_hash = hashlib.sha256(obj_str.encode()).hexdigest()
                        # Check if the hash already exists in the database
                        cur.execute(sql.SQL("SELECT COUNT(*) FROM gp WHERE data_hash = %s"), (obj_hash,))
                        count = cur.fetchone()[0]
                        if count == 0:  # Insert data only if the hash is not found in the database
                            try:
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

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    populate()
