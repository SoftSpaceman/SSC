

# THIS SCRIPT IS BUILT ON THE SAME FRAMEWORK AS fetch_insert.py 
## this has insertion2.1 as logfile. 

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



# Set up logging
LOG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'insertion3.log')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler = RotatingFileHandler(LOG_FILE, backupCount=3)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)



def load_config():
    config = configparser.ConfigParser()
    config_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'config', 'config.ini')
    config.read(config_file_path)
    return config



def connect_to_database(config):
    try:
        conn = psycopg2.connect(
            host=config.get('tables3', 'host'),
            dbname=config.get('tables3', 'dbname'),
            user=config.get('tables3', 'user'),
            password=config.get('tables3', 'password'),
            port=config.get('tables3', 'port')
        )
        #logger.info("Connected to database successfully.")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Error connecting to database: {e}")
        raise



def fetch_satellite_data(session, uriBase, requestCmdAction, requestGPdataNOW):
    try:
        resp = session.get(uriBase + requestCmdAction + requestGPdataNOW)
        resp.raise_for_status()
        # logger.info("Fetched satellite data successfully.")
        return resp.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching satellite data: {e}")
        raise



def insert_data_into_database(data, conn):
    try:
        with conn.cursor() as cur:
            # Inserting fetched data and their hashes into the existing table
            inserted_count = 0
            skipped_count = 0
            for obj in data:
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
                        ) VALUES ( CURRENT_TIMESTAMP, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
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
                    logger.info(f"Inserted NORAD_CAT_ID: {obj['NORAD_CAT_ID']} with hash: {obj_hash}")
                except psycopg2.IntegrityError as e:
                    if 'duplicate key value' in str(e):
                        skipped_count += 1
                        logger.warning(f"Skipped duplicate NORAD_CAT_ID: {obj['NORAD_CAT_ID']} with hash: {obj_hash}")
                    else:
                        logger.error(f"Error inserting NORAD_CAT_ID: {obj['NORAD_CAT_ID']}: {str(e)}")
                    conn.rollback()

            conn.commit()
            logger.info(f"Inserted {inserted_count} data points successfully.")
            logger.info(f"Skipped {skipped_count} duplicate data points.")
    except psycopg2.Error as e:
        logger.error(f"Error inserting data into database: {e}")
        raise



def populate():
    try:
        
        config = load_config()
        api_username = config.get('API', 'username')
        api_password = config.get('API', 'password')
        uriBase = "https://www.space-track.org"
        requestLogin = "/ajaxauth/login"
        requestCmdAction = "/basicspacedata/query"
        requestGPdataNOW = f'/class/gp/creation_date/%3Enow-0.125/orderby/norad_cat_id/format/json' # THE QUERY FROM SPACETRACK.ORG

        siteCred = {'identity': api_username, 'password': api_password}

        

        with requests.Session() as session:
            resp = session.post(uriBase + requestLogin, data=siteCred)
            resp.raise_for_status()
            logger.info("Logged in to space-track.org successfully.")
            fetched_data = fetch_satellite_data(session, uriBase, requestCmdAction, requestGPdataNOW)
            logger.info("fetch_satellite_data function executed successfully.")


        logger.info("populationg database...")
        conn = connect_to_database(config)
        insert_data_into_database(fetched_data, conn)
        logger.info("Database population completed.")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")


schedule.every().minute.do(populate)



try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    logger.info("Process terminated by keyboard interruption.")
except Exception as e:
    logger.error(f"An error occurred in the scheduler loop: {str(e)}")
logger.info("Scheduler loop exited unexpectedly.")





