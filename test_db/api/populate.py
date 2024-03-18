import psycopg2
import requests
import logging
import datetime
import configparser



# login and request URL components to access the RESTful service at spce-track.org.
uriBase                = "https://www.space-track.org"
requestLogin           = "/ajaxauth/login"
requestCmdAction       = "/basicspacedata/query"


# Your credientials are stored in a file named APIconfig.ini. 
# these are needed to log in to the space-track.org RESTful service.
# Use configparser package to pull in the ini file (pip install configparser)
config = configparser.ConfigParser()
config.read(r'C:\Users\Bananberg\Desktop\Space_info\SSC\projects\SSC_database\test_db\api\APIconfig.ini')
configUsr = config.get("configuration","username")
configPwd = config.get("configuration","password")
siteCred = {'identity': configUsr, 'password': configPwd}


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MyError(Exception):
    """Custom exception class."""
    def __init__(self, args):
        """Initialize MyError instance."""
        super().__init__("My exception was raised with arguments {0}".format(args))
        self.args = args



########### STORAGE FUNCTION OF FETCHED DATA INTO POSTGRESQL DATABASE ####################


# reads the file with the database credentials.
config = configparser.ConfigParser()
config.read(r'C:\Users\Bananberg\Desktop\Space_info\SSC\projects\SSC_database\test_db\database\database_config.ini')

host = config.get("tables","host")
dbname = config.get('tables', 'dbname')
user = config.get('tables', 'user')
password = config.get('tables', 'password')
port = config.get('tables', 'port')



def store_data_in_postgresql(data):
    num_inserted = 0
    try:
        # Connect to PostgreSQL database
        conn = psycopg2.connect( host=host, dbname=dbname, user=user, password=password, port=port)
        cursor = conn.cursor()

        # Insert data into PostgreSQL table
        for item in data:
            #print(item)  # print into the debugging line
            
            try:
                cursor.execute("INSERT INTO gp_file (CCSDS_OMM_VERS, COMMENT, CREATION_DATE, ORIGINATOR, OBJECT_NAME, OBJECT_ID, CENTER_NAME, REF_FRAME, TIME_SYSTEM, MEAN_ELEMENT_THEORY, EPOCH, MEAN_MOTION, ECCENTRICITY, INCLINATION, RA_OF_ASC_NODE, ARG_OF_PERICENTER, MEAN_ANOMALY, EPHEMERIS_TYPE, CLASSIFICATION_TYPE, NORAD_CAT_ID, ELEMENT_SET_NO, REV_AT_EPOCH, BSTAR, MEAN_MOTION_DOT, MEAN_MOTION_DDOT, SEMIMAJOR_AXIS, PERIOD, APOAPSIS, PERIAPSIS, OBJECT_TYPE, RCS_SIZE, COUNTRY_CODE, LAUNCH_DATE, SITE, DECAY_DATE, FILE, GP_ID, TLE_LINE0, TLE_LINE1, TLE_LINE2) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (item['CCSDS_OMM_VERS'], item['COMMENT'], item['CREATION_DATE'], item['ORIGINATOR'], item['OBJECT_NAME'], item['OBJECT_ID'], item['CENTER_NAME'], item['REF_FRAME'], item['TIME_SYSTEM'], item['MEAN_ELEMENT_THEORY'], item['EPOCH'], item['MEAN_MOTION'], item['ECCENTRICITY'], item['INCLINATION'], item['RA_OF_ASC_NODE'], item['ARG_OF_PERICENTER'], item['MEAN_ANOMALY'], item['EPHEMERIS_TYPE'], item['CLASSIFICATION_TYPE'], item['NORAD_CAT_ID'], item['ELEMENT_SET_NO'], item['REV_AT_EPOCH'], item['BSTAR'], item['MEAN_MOTION_DOT'], item['MEAN_MOTION_DDOT'], item['SEMIMAJOR_AXIS'], item['PERIOD'], item['APOAPSIS'], item['PERIAPSIS'], item['OBJECT_TYPE'], item['RCS_SIZE'], item['COUNTRY_CODE'], item['LAUNCH_DATE'], item['SITE'], item['DECAY_DATE'], item['FILE'], item['GP_ID'], item['TLE_LINE0'], item['TLE_LINE1'], item['TLE_LINE2']))
            
                num_inserted += 1
            except Exception as e:
                print(f"Error occurred with item {item}: {e}")
                raise e
           
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error("Error occurred while inserting data into PostgreSQL: %s", error)

    finally:
        if conn is not None:
            cursor.close()
            conn.close()
            logging.info("Database connection closed.")
    return num_inserted





#######################################################################################
################# REQUESTS ### WITH SIMPLE UNDIFINED LOGGING ##########################

# This query: /class/gp/NORAD_CAT_ID/%3C20000/orderby/NORAD_CAT_ID%20asc/emptyresult/show
    # has no limit but takes all GP data in order of NORAD_CAT_IDs above 20000.


    #this query: https://www.space-track.org/basicspacedata/query/class/gp/NORAD_CAT_ID/%3C10000/orderby/NORAD_CAT_ID%20asc/limit/50/emptyresult/show
        # is limted to only load 50 NORAD_CAT_ID from 10000 and up and its corresponding data . 

    # This Query: https://www.space-track.org/basicspacedata/query/class/gp/NORAD_CAT_ID/%3C50000/orderby/NORAD_CAT_ID%20asc/limit/10/emptyresult/show
    # only outputs 10 NORAD_CAT_IDs and correspondig with a number above 50000. So we get some relevant data, just so we could have some consistan data with probalby all fields filled out. 

    # this query: https://www.space-track.org/basicspacedata/query/class/gp/orderby/NORAD_CAT_ID%20desc/limit/10/emptyresult/show
    # only outputs the lates 10 NORAD_CAT_IDs and corresponding data . of today 06/03/2024. 


    # check with your old script to se how you loaded the thata to a database. 


requestGPdata = f'/class/gp/NORAD_CAT_ID/%3E20000/orderby/NORAD_CAT_ID%20asc/emptyresult/show'

with requests.Session() as session:
    try:
        # Logging request URL and method
        logger.info("Sending request to: %s", uriBase + requestLogin)
        logger.info("Request method: POST")
        
        # Login
        start_time_login = datetime.datetime.now()
        resp = session.post(uriBase + requestLogin, data=siteCred)
        if resp.status_code != 200:
            raise Exception(f"Login failed with status code: {resp.status_code}")
        logger.info("Login successful")

        # Logging request URL and method for fetching data
        logger.info("Sending request to: %s", uriBase + requestCmdAction + requestGPdata)
        logger.info("Request method: GET")
        
        # Fetch satellite data
        start_time_fetch = datetime.datetime.now()
        resp = session.get(uriBase + requestCmdAction + requestGPdata)
        if resp.status_code != 200:
            raise Exception(f"Failed to fetch data with status code: {resp.status_code}")
        logger.info("Data fetched successfully")

        # Calculate data size
        data_size = len(resp.content) if resp.content else 0
        logger.info("Data size: %d bytes", data_size)

        # Calculate time taken for the request
        end_time = datetime.datetime.now()
        time_taken_login = end_time - start_time_login
        time_taken_fetch = end_time - start_time_fetch
        logger.info("Time taken for login: %s", time_taken_login)
        logger.info("Time taken for fetching data: %s", time_taken_fetch)

        # Store fetched data
        fetched_data = resp.json()

     
        # Check if data was fetched successfully and print it
        if fetched_data:
            #print(fetched_data)
            for item in fetched_data:
                print(f"NORAD ID: {item['NORAD_CAT_ID']}, Name: {item['OBJECT_NAME']}")
            num_inserted = store_data_in_postgresql(fetched_data)
            print(f"Number of objects inserted: {num_inserted}")
        else:
            print("No data fetched.")

    except Exception as e:
        logger.error("Error occurred: %s", e)
    # finally:
    #     session.close()












        