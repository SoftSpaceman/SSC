



import psycopg2
import os
import configparser

# Your credientials are stored in directory config and file named config.ini. 
# these are needed to log in to the space-track.org RESTful service.
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


# Get database connection parameters
host = config.get('tables', 'host')
dbname = config.get('tables', 'dbname')
user = config.get('tables', 'user')
password = config.get('tables', 'password')
port = config.get('tables', 'port')

def move_data_between_tables():
    try:
        # Connect to PostgreSQL database
        conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
        cursor = conn.cursor()

        # Execute the INSERT INTO SELECT statement
        cursor.execute("""
            INSERT INTO gp_file_historical (
                gp_file_id,
                NORAD_CAT_ID, 
                modification_timestamp,
                CCSDS_OMM_VERS, 
                COMMENT, 
                CREATION_DATE, 
                EPOCH, 
                ORIGINATOR, 
                OBJECT_NAME, 
                OBJECT_ID, 
                CENTER_NAME, 
                REF_FRAME, 
                TIME_SYSTEM, 
                MEAN_ELEMENT_THEORY, 
                MEAN_MOTION, 
                ECCENTRICITY, 
                INCLINATION, 
                RA_OF_ASC_NODE, 
                ARG_OF_PERICENTER, 
                MEAN_ANOMALY, 
                EPHEMERIS_TYPE, 
                CLASSIFICATION_TYPE, 
                ELEMENT_SET_NO, 
                REV_AT_EPOCH, 
                BSTAR, 
                MEAN_MOTION_DOT, 
                MEAN_MOTION_DDOT, 
                SEMIMAJOR_AXIS, 
                PERIOD, 
                APOAPSIS, 
                PERIAPSIS, 
                OBJECT_TYPE, 
                RCS_SIZE, 
                COUNTRY_CODE, 
                LAUNCH_DATE, 
                SITE, 
                DECAY_DATE, 
                FILE, 
                GP_ID, 
                TLE_LINE0, 
                TLE_LINE1, 
                TLE_LINE2
            )
            SELECT 
                gp_file_id,
                NORAD_CAT_ID, 
                modification_timestamp,
                CCSDS_OMM_VERS, 
                COMMENT, 
                CREATION_DATE, 
                EPOCH, 
                ORIGINATOR, 
                OBJECT_NAME, 
                OBJECT_ID, 
                CENTER_NAME, 
                REF_FRAME, 
                TIME_SYSTEM, 
                MEAN_ELEMENT_THEORY, 
                MEAN_MOTION, 
                ECCENTRICITY, 
                INCLINATION, 
                RA_OF_ASC_NODE, 
                ARG_OF_PERICENTER, 
                MEAN_ANOMALY, 
                EPHEMERIS_TYPE, 
                CLASSIFICATION_TYPE, 
                ELEMENT_SET_NO, 
                REV_AT_EPOCH, 
                BSTAR, 
                MEAN_MOTION_DOT, 
                MEAN_MOTION_DDOT, 
                SEMIMAJOR_AXIS, 
                PERIOD, 
                APOAPSIS, 
                PERIAPSIS, 
                OBJECT_TYPE, 
                RCS_SIZE, 
                COUNTRY_CODE, 
                LAUNCH_DATE, 
                SITE, 
                DECAY_DATE, 
                FILE, 
                GP_ID, 
                TLE_LINE0, 
                TLE_LINE1, 
                TLE_LINE2
            FROM 
                gp_file
        """)
        
        # Commit the transaction
        conn.commit()
        print("Data moved successfully.")
        
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error occurred:", error)
    finally:
        if conn is not None:
            cursor.close()
            conn.close()
            print("Database connection closed.")

# Call the function to move data
move_data_between_tables()



















# import os
# import requests
# import logging
# import datetime
# import configparser
# import psycopg2



# # # Set up logging
# # logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# # logger = logging.getLogger(__name__)

# # set up logging to file
# logging.basicConfig(filename='GP_populate.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# class MyError(Exception):
#     """Custom exception class."""
#     def __init__(self, args):
#         """Initialize MyError instance."""
#         super().__init__("My exception was raised with arguments {0}".format(args))
#         self.args = args



# # Your credientials are stored in directory config and file named config.ini. 
# # these are needed to log in to the space-track.org RESTful service.
# # Read API credentials from config file
# config = configparser.ConfigParser()
# config_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'config', 'config.ini')
# config.read(config_file_path)
# api_username = config.get('API', 'username')
# api_password = config.get('API', 'password')

# # Define URL components
# uriBase = "https://www.space-track.org"
# requestLogin = "/ajaxauth/login"
# requestCmdAction = "/basicspacedata/query"
# siteCred = {'identity': api_username, 'password': api_password}

# # Get database connection parameters
# host = config.get('tables', 'host')
# dbname = config.get('tables', 'dbname')
# user = config.get('tables', 'user')
# password = config.get('tables', 'password')
# port = config.get('tables', 'port')

# ########### STORAGE FUNCTION OF FETCHED DATA INTO POSTGRESQL DATABASE ####################

# def store_data_in_postgresql(data):
#     num_inserted = 0
#     conn = None
#     try:
#         # Connect to PostgreSQL database
#         conn = psycopg2.connect( host=host, dbname=dbname, user=user, password=password, port=port)
#         cursor = conn.cursor()

#         # Insert data into PostgreSQL table
#         for item in data:
#             #print(item)  # print into the debugging line
            
#             try:
#                 cursor.execute("INSERT INTO gp_file_historical (CCSDS_OMM_VERS, COMMENT, CREATION_DATE, ORIGINATOR, OBJECT_NAME, OBJECT_ID, CENTER_NAME, REF_FRAME, TIME_SYSTEM, MEAN_ELEMENT_THEORY, EPOCH, MEAN_MOTION, ECCENTRICITY, INCLINATION, RA_OF_ASC_NODE, ARG_OF_PERICENTER, MEAN_ANOMALY, EPHEMERIS_TYPE, CLASSIFICATION_TYPE, NORAD_CAT_ID, ELEMENT_SET_NO, REV_AT_EPOCH, BSTAR, MEAN_MOTION_DOT, MEAN_MOTION_DDOT, SEMIMAJOR_AXIS, PERIOD, APOAPSIS, PERIAPSIS, OBJECT_TYPE, RCS_SIZE, COUNTRY_CODE, LAUNCH_DATE, SITE, DECAY_DATE, FILE, GP_ID, TLE_LINE0, TLE_LINE1, TLE_LINE2) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (item['CCSDS_OMM_VERS'], item['COMMENT'], item['CREATION_DATE'], item['ORIGINATOR'], item['OBJECT_NAME'], item['OBJECT_ID'], item['CENTER_NAME'], item['REF_FRAME'], item['TIME_SYSTEM'], item['MEAN_ELEMENT_THEORY'], item['EPOCH'], item['MEAN_MOTION'], item['ECCENTRICITY'], item['INCLINATION'], item['RA_OF_ASC_NODE'], item['ARG_OF_PERICENTER'], item['MEAN_ANOMALY'], item['EPHEMERIS_TYPE'], item['CLASSIFICATION_TYPE'], item['NORAD_CAT_ID'], item['ELEMENT_SET_NO'], item['REV_AT_EPOCH'], item['BSTAR'], item['MEAN_MOTION_DOT'], item['MEAN_MOTION_DDOT'], item['SEMIMAJOR_AXIS'], item['PERIOD'], item['APOAPSIS'], item['PERIAPSIS'], item['OBJECT_TYPE'], item['RCS_SIZE'], item['COUNTRY_CODE'], item['LAUNCH_DATE'], item['SITE'], item['DECAY_DATE'], item['FILE'], item['GP_ID'], item['TLE_LINE0'], item['TLE_LINE1'], item['TLE_LINE2']))
            
#                 num_inserted += 1
#             except Exception as e:
#                 print(f"Error occurred with item {item}: {e}")
#                 raise e
           
#         conn.commit()
#         logging.info("Data insertion into PostgreSQL database gp_file_historical, successful!")
#     except (Exception, psycopg2.DatabaseError) as error:
#         logging.error("Error occurred while inserting data into PostgreSQL: %s", error)

#     finally:
#         if conn is not None:
#             cursor.close()
#             conn.close()
#             logging.info("Database connection closed.")
#     return num_inserted





# #######################################################################################
# ################# REQUESTS ### WITH SIMPLE UNDIFINED LOGGING ##########################

# # This query: /class/gp/NORAD_CAT_ID/%3C20000/orderby/NORAD_CAT_ID%20asc/emptyresult/show
#     # has no limit but takes all GP data in order of NORAD_CAT_IDs above 20000.

# # login and request URL components to access the RESTful service at spce-track.org.
# uriBase                = "https://www.space-track.org"
# requestLogin           = "/ajaxauth/login"
# requestCmdAction       = "/basicspacedata/query"
# # Get API credentials
# api_username = config.get('API', 'username')
# api_password = config.get('API', 'password')

# siteCred = {'identity': api_username, 'password': api_password}


# requestGPdata = f'/class/gp/orderby/NORAD_CAT_ID%20desc/emptyresult/show'



# # See https://www.space-track.org/documentation for details on REST queries
# # the "Find Starlinks" query searches all satellites with NORAD_CAT_ID > 40000, with OBJECT_NAME matching STARLINK*, 1 line per sat
# #/class/tle_latest/NORAD_CAT_ID/>40000/ORDINAL/1/OBJECT_NAME/STARLINK~~/format/json/orderby/NORAD_CAT_ID%20asc"
# #requestOMMStarlink1 = "/class/omm/NORAD_CAT_ID/"


# # https://www.space-track.org/basicspacedata/query/class/gp_history/orderby/NORAD_CAT_ID%20desc/emptyresult/show
# # This one will give all historical data from the catalog GP.




# # /class/gp/decay_date/null-val/epoch/%3Enow-30/orderby/norad_cat_id/format/json 
# # With this query we get all the data from the last 30 days. witch aperently is equal to 25980 unique NORAD_CAT_IDs.

# # /class/gp/orderby/NORAD_CAT_ID%20asc/emptyresult/show     
# # this gave me 57828 unique NORAD_CAT_IDs. So why are some missing? # this is probably due to the fact that the classified data is not shown. It exsists in other catalogs. 


# # Main script
# with requests.Session() as session:
#     try:
#         # Logging request URL and method
#         logging.info("Sending request to: %s", uriBase + requestLogin)
#         logging.info("Request method: POST")
        
#         # Login
#         start_time_login = datetime.datetime.now()
#         resp = session.post(uriBase + requestLogin, data=siteCred)
#         if resp.status_code != 200:
#             raise Exception(f"Login failed with status code: {resp.status_code}")
#         logging.info("Login successful")

#         # Logging request URL and method for fetching data
#         logging.info("Sending request to: %s", uriBase + requestCmdAction + requestGPdata)
#         logging.info("Request method: GET")
        
#         # Fetch satellite data
#         start_time_fetch = datetime.datetime.now()
#         resp = session.get(uriBase + requestCmdAction + requestGPdata)
#         if resp.status_code != 200:
#             raise Exception(f"Failed to fetch data with status code: {resp.status_code}")
#         logging.info("Data fetched successfully")

#         # Calculate data size
#         data_size = len(resp.content) if resp.content else 0
#         logging.info("Data size: %d bytes", data_size)

#         # Calculate time taken for the request
#         end_time = datetime.datetime.now()
#         time_taken_login = end_time - start_time_login
#         time_taken_fetch = end_time - start_time_fetch
#         logging.info("Time taken for login: %s", time_taken_login)
#         logging.info("Time taken for fetching data: %s", time_taken_fetch)

#         # Store fetched data
#         fetched_data = resp.json()

#         # Check if data was fetched successfully and print it
#         if fetched_data:
#             num_inserted = store_data_in_postgresql(fetched_data)
#             logging.info("Number of objects inserted: %d", num_inserted)
#         else:
#             logging.info("No data fetched.")

#     except Exception as e:
#         logging.error("Error occurred: %s", e)














        