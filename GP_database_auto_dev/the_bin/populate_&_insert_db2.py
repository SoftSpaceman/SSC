

# THIS SCRIPT RUNNS AND POPULATES THE DATABASE WITH DATA FROM SPACE-TRACK.ORG AND THEN IT RUNS A LOOP.
# THIS WILL NOT BE SUITABLE IF WE NEED TO RESTART THE LOOP. # SO WE NEED TO SPLIT UP POPULATE AND INSERT INTO TWO SEPERATE FILES 

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
LOG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'populate_&_insert2.log')
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


        # this query will get all data from the gp class that has a decay date that is null.
        # and will popualte the databse and use the same hashlib function. This is to minimize duplication of hashes. ( in therory ) 
        #requestDATApopulate = f'/class/gp/DECAY_DATE/null-val/orderby/NORAD_CAT_ID%20asc/emptyresult/show'


        # THIS ONE WILL RUN IN gpdata2 It get data that was create within 25 minutes of each request
        requestNOW = f'/class/gp/creation_date/%3Enow-0.02/orderby/norad_cat_id/format/json'


        # Define the request to fetch data from space-track.org
        #requestGPdataNOW = f'/class/gp/epoch/%3Enow/orderby/norad_cat_id/format/json'

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
            resp = session.get(uriBase + requestCmdAction + requestNOW)
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

        pass

    except Exception as e:
        logging.error(f"An error occurred during data population: {str(e)}")



# Schedule the populate function to run every minute
schedule.every().minute.do(populate)



# Populate the database once before starting the scheduler loop
populate_once()



try:
    # Infinite loop to run the scheduler
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    logging.info("Process terminated by keyboard interruption.")
except Exception as e:
    logging.error(f"An error occurred in the scheduler loop: {str(e)}")

# Log a message indicating that the loop broke
logging.info("Scheduler loop exited unexpectedly.")











# THIS IS THE SIMPLER SCRIPT OF THE ONE ABOVE! 
# import os
# import configparser
# import requests
# import psycopg2
# import hashlib
# import logging
# from psycopg2 import sql


# def populate():
#     try:
#         Read API credentials from config file
#         config = configparser.ConfigParser()
#         config_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'config', 'config.ini')
#         config.read(config_file_path)
#         api_username = config.get('API', 'username')
#         api_password = config.get('API', 'password')

#         Define URL components
#         uriBase = "https://www.space-track.org"
#         requestLogin = "/ajaxauth/login"
#         requestCmdAction = "/basicspacedata/query"
#         siteCred = {'identity': api_username, 'password': api_password}


#         this query will get all data from the gp class that has a decay date that is null.
#         and will popualte the databse and use the same hashlib function. This is to minimize duplication of hashes. ( in therory ) 
#         requestDATApopulate = f'/class/gp/DECAY_DATE/null-val/orderby/NORAD_CAT_ID%20asc/emptyresult/show'


#         Define the request to fetch data from space-track.org
#         requestGPdata = f'/class/gp/epoch/%3Enow/orderby/norad_cat_id/format/json'

       



#         Get database connection parameters
#         host = config.get('tables', 'host')
#         dbname = config.get('tables', 'dbname')
#         user = config.get('tables', 'user')
#         password = config.get('tables', 'password')
#         port = config.get('tables', 'port')

#         Main script
#         with requests.Session() as session:
#             Login to space-track.org
#             resp = session.post(uriBase + requestLogin, data=siteCred)
#             resp.raise_for_status()  # Raise an error for bad response status

#             Fetch satellite data
#             resp = session.get(uriBase + requestCmdAction + requestGPdata)
#             resp.raise_for_status()  # Raise an error for bad response status

#             Print fetched data
#             fetched_data = resp.json()

#             Establish connection to PostgreSQL database
#             with psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port) as conn:
#                 Create a cursor object
#                 with conn.cursor() as cur:
#                     Insert fetched data and their hashes into the existing table
#                     inserted_count = 0
#                     skipped_count = 0
#                     for obj in fetched_data:
#                         try:
#                             obj_str = str(obj)
#                             obj_hash = hashlib.sha256(obj_str.encode()).hexdigest()
#                             cur.execute(sql.SQL("""
#                             INSERT INTO gp (
#                             insertion_date, data_hash, NORAD_CAT_ID, CREATION_DATE, EPOCH, ORIGINATOR, OBJECT_NAME,
#                             OBJECT_ID, CENTER_NAME, REF_FRAME, TIME_SYSTEM, MEAN_ELEMENT_THEORY, MEAN_MOTION,
#                             ECCENTRICITY, INCLINATION, RA_OF_ASC_NODE, ARG_OF_PERICENTER, MEAN_ANOMALY, EPHEMERIS_TYPE,
#                             CLASSIFICATION_TYPE, CCSDS_OMM_VERS, COMMENT, ELEMENT_SET_NO, REV_AT_EPOCH, BSTAR,
#                             MEAN_MOTION_DOT, MEAN_MOTION_DDOT, SEMIMAJOR_AXIS, PERIOD, APOAPSIS, PERIAPSIS,
#                             OBJECT_TYPE, RCS_SIZE, COUNTRY_CODE, LAUNCH_DATE, SITE, DECAY_DATE, FILE, GP_ID,
#                             TLE_LINE0, TLE_LINE1, TLE_LINE2
#                         ) VALUES (
#                             CURRENT_TIMESTAMP, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
#                             %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
#                         )
#                     """), (
#                                 obj_hash, obj['NORAD_CAT_ID'], obj['CREATION_DATE'], obj['EPOCH'], obj['ORIGINATOR'],
#                                 obj['OBJECT_NAME'], obj['OBJECT_ID'], obj['CENTER_NAME'], obj['REF_FRAME'],
#                                 obj['TIME_SYSTEM'], obj['MEAN_ELEMENT_THEORY'], obj['MEAN_MOTION'], obj['ECCENTRICITY'],
#                                 obj['INCLINATION'], obj['RA_OF_ASC_NODE'], obj['ARG_OF_PERICENTER'], obj['MEAN_ANOMALY'],
#                                 obj['EPHEMERIS_TYPE'], obj['CLASSIFICATION_TYPE'], obj['CCSDS_OMM_VERS'], obj['COMMENT'],
#                                 obj['ELEMENT_SET_NO'], obj['REV_AT_EPOCH'], obj['BSTAR'], obj['MEAN_MOTION_DOT'], obj['MEAN_MOTION_DDOT'],
#                                 obj['SEMIMAJOR_AXIS'], obj['PERIOD'], obj['APOAPSIS'], obj['PERIAPSIS'], obj['OBJECT_TYPE'],
#                                 obj['RCS_SIZE'], obj['COUNTRY_CODE'], obj['LAUNCH_DATE'], obj['SITE'], obj['DECAY_DATE'],
#                                 obj['FILE'], obj['GP_ID'], obj['TLE_LINE0'], obj['TLE_LINE1'], obj['TLE_LINE2']
#                             ))
#                             inserted_count += 1
#                             print(f"Inserted NORAD_CAT_ID: {obj['NORAD_CAT_ID']} with hash: {obj_hash}")
#                         except psycopg2.IntegrityError as e:
#                             skipped_count += 1
#                             conn.rollback()
#                             print(f"Skipped duplicate NORAD_CAT_ID: {obj['NORAD_CAT_ID']} with hash: {obj_hash}")
#                     conn.commit()

#         print(f"Inserted {inserted_count} data points successfully.")
#         print(f"Skipped {skipped_count} duplicate data points.")

#     except Exception as e:
#         print(f"An error occurred: {str(e)}")

# if __name__ == "__main__":
#     populate()





## This is without modification. the code runs smoothy and is only used as a rllback. 
#
# def populate():
#     try:
#         # Read API credentials from config file
#         config = configparser.ConfigParser()
#         config_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'config', 'config.ini')
#         config.read(config_file_path)
#         api_username = config.get('API', 'username')
#         api_password = config.get('API', 'password')

#         # Define URL components
#         uriBase = "https://www.space-track.org"
#         requestLogin = "/ajaxauth/login"
#         requestCmdAction = "/basicspacedata/query"
#         siteCred = {'identity': api_username, 'password': api_password}




#         # # Define the request to fetch data from space-track.org
#         # this query will get all data from the gp class that has a decay date that is null.
#         # requestGPdata = f'/class/gp/DECAY_DATE/null-val/orderby/NORAD_CAT_ID%20asc/emptyresult/show'

#         # https://www.space-track.org/basicspacedata/query/class/gp/epoch/%3Enow-1/orderby/norad_cat_id/format/json
#         # this query will et all data from the last 24 hours. that has a epoch date from yesterad to today.
#         # according to spacetrack this will fetch the latest propagatable data. 

#         requestGPdata = f'/class/gp/epoch/%3Enow-1/orderby/norad_cat_id/format/json'


#         # Get database connection parameters
#         host = config.get('tables', 'host')
#         dbname = config.get('tables', 'dbname')
#         user = config.get('tables', 'user')
#         password = config.get('tables', 'password')
#         port = config.get('tables', 'port')

#         # Main script
#         with requests.Session() as session:
#             # Login to space-track.org
#             resp = session.post(uriBase + requestLogin, data=siteCred)
#             resp.raise_for_status()  # Raise an error for bad response status

#             # Fetch satellite data
#             resp = session.get(uriBase + requestCmdAction + requestGPdata)
#             resp.raise_for_status()  # Raise an error for bad response status

#             # Print fetched data
#             fetched_data = resp.json()

#             # Establish connection to PostgreSQL database
#             with psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port) as conn:
#                 # Create a cursor object
#                 with conn.cursor() as cur:
#                     # Insert fetched data and their hashes into the existing table
#                     inserted_count = 0
#                     for obj in fetched_data:
#                         obj_str = str(obj)
#                         obj_hash = hashlib.sha256(obj_str.encode()).hexdigest()
#                         cur.execute(sql.SQL("""
#                         INSERT INTO gp (
#                         insertion_date, data_hash, NORAD_CAT_ID, CREATION_DATE, EPOCH, ORIGINATOR, OBJECT_NAME,
#                         OBJECT_ID, CENTER_NAME, REF_FRAME, TIME_SYSTEM, MEAN_ELEMENT_THEORY, MEAN_MOTION,
#                         ECCENTRICITY, INCLINATION, RA_OF_ASC_NODE, ARG_OF_PERICENTER, MEAN_ANOMALY, EPHEMERIS_TYPE,
#                         CLASSIFICATION_TYPE, CCSDS_OMM_VERS, COMMENT, ELEMENT_SET_NO, REV_AT_EPOCH, BSTAR,
#                         MEAN_MOTION_DOT, MEAN_MOTION_DDOT, SEMIMAJOR_AXIS, PERIOD, APOAPSIS, PERIAPSIS,
#                         OBJECT_TYPE, RCS_SIZE, COUNTRY_CODE, LAUNCH_DATE, SITE, DECAY_DATE, FILE, GP_ID,
#                         TLE_LINE0, TLE_LINE1, TLE_LINE2
#                     ) VALUES (
#                         CURRENT_TIMESTAMP, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
#                         %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
#                     )
#                 """), (
#                     obj_hash, obj['NORAD_CAT_ID'], obj['CREATION_DATE'], obj['EPOCH'], obj['ORIGINATOR'],
#                     obj['OBJECT_NAME'], obj['OBJECT_ID'], obj['CENTER_NAME'], obj['REF_FRAME'], obj['TIME_SYSTEM'],
#                     obj['MEAN_ELEMENT_THEORY'], obj['MEAN_MOTION'], obj['ECCENTRICITY'], obj['INCLINATION'],
#                     obj['RA_OF_ASC_NODE'], obj['ARG_OF_PERICENTER'], obj['MEAN_ANOMALY'], obj['EPHEMERIS_TYPE'],
#                     obj['CLASSIFICATION_TYPE'], obj['CCSDS_OMM_VERS'], obj['COMMENT'], obj['ELEMENT_SET_NO'],
#                     obj['REV_AT_EPOCH'], obj['BSTAR'], obj['MEAN_MOTION_DOT'], obj['MEAN_MOTION_DDOT'],
#                     obj['SEMIMAJOR_AXIS'], obj['PERIOD'], obj['APOAPSIS'], obj['PERIAPSIS'], obj['OBJECT_TYPE'],
#                     obj['RCS_SIZE'], obj['COUNTRY_CODE'], obj['LAUNCH_DATE'], obj['SITE'], obj['DECAY_DATE'],
#                     obj['FILE'], obj['GP_ID'], obj['TLE_LINE0'], obj['TLE_LINE1'], obj['TLE_LINE2']
#                 ))
#                         inserted_count += 1
#                     conn.commit()

#         print(f"Inserted {inserted_count} data points successfully.")
#         print(f"Data inserted into gpfile3 database with hash: {obj_hash}")

#     except Exception as e:
#         print(f"An error occurred: {str(e)}")

# if __name__ == "__main__":
#     populate()





