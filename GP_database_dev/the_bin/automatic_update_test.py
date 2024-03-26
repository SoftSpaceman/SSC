
# https://chat.openai.com/share/0c61fcf1-2fce-46b7-93be-a7362db4e163

import psycopg2
import requests
import time
from datetime import datetime
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

requestGPdata = f'/class/gp/orderby/NORAD_CAT_ID%20desc/limit/10/emptyresult/show'



#################################################################
##################### TO CONNECT TO THE DATABASE ################

# reads the file with the database credentials.
config = configparser.ConfigParser()
config.read(r'C:\Users\Bananberg\Desktop\Space_info\SSC\projects\SSC_database\test_db\database\database_config.ini')

host = config.get("tables","host")
dbname = config.get('tables', 'dbname')
user = config.get('tables', 'user')
password = config.get('tables', 'password')
port = config.get('tables', 'port')




########### ERROR HANDELING 

class MyError(Exception):
    """Custom exception class."""
    def __init__(self, args):
        """Initialize MyError instance."""
        super().__init__("My exception was raised with arguments {0}".format(args))
        self.args = args









def fetch_data_from_api():

     # Establish a connection to the PostgreSQL database
    conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)

       # use requests package to drive the RESTful session with space-track.org
    with requests.Session() as session:
        try:
            # run the session in a with block to force session to close if we exit

            # need to log in first. note that we get a 200 to say the web site got the data, not that we are logged in
            resp = session.post(uriBase + requestLogin, data=siteCred)
            if resp.status_code != 200:
                raise MyError(resp, "POST fail on login")

            # this query picks up GPs for all satellites from the catalog. Note - a 401 failure shows you have bad credentials
            resp = session.get(uriBase + requestCmdAction + requestGPdata)
            if resp.status_code != 200:
                print(resp)
                raise MyError(resp, "GET fail on request for satellites")

            # Store fetched data in a variable
            fetched_data = resp.json()


        except requests.RequestException as e:
            print("Error fetching data from API:", e)
        return None





def insert_into_gp_file(data):
    try:
        conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
        cursor = conn.cursor()

        # Check if the data already exists in gp_file
        cursor.execute("SELECT COUNT(*) FROM gp_file WHERE NORAD_CAT_ID = %s", (data['NORAD_CAT_ID'],))
        count = cursor.fetchone()[0]

        if count == 0:
            # Insert new data into gp_file
            cursor.execute("""
                INSERT INTO gp_file (NORAD_CAT_ID, modification_timestamp, CCSDS_OMM_VERS, COMMENT, CREATION_DATE, 
                ORIGINATOR, OBJECT_NAME, OBJECT_ID, CENTER_NAME, REF_FRAME, TIME_SYSTEM, MEAN_ELEMENT_THEORY, EPOCH, 
                MEAN_MOTION, ECCENTRICITY, INCLINATION, RA_OF_ASC_NODE, ARG_OF_PERICENTER, MEAN_ANOMALY, EPHEMERIS_TYPE, 
                CLASSIFICATION_TYPE, ELEMENT_SET_NO, REV_AT_EPOCH, BSTAR, MEAN_MOTION_DOT, MEAN_MOTION_DDOT, SEMIMAJOR_AXIS, 
                PERIOD, APOAPSIS, PERIAPSIS, OBJECT_TYPE, RCS_SIZE, COUNTRY_CODE, LAUNCH_DATE, SITE, DECAY_DATE, FILE, GP_ID, 
                TLE_LINE0, TLE_LINE1, TLE_LINE2)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (data['NORAD_CAT_ID'], datetime.now(), data['CCSDS_OMM_VERS'], data['COMMENT'], data['CREATION_DATE'], 
                  data['ORIGINATOR'], data['OBJECT_NAME'], data['OBJECT_ID'], data['CENTER_NAME'], data['REF_FRAME'], 
                  data['TIME_SYSTEM'], data['MEAN_ELEMENT_THEORY'], data['EPOCH'], data['MEAN_MOTION'], data['ECCENTRICITY'], 
                  data['INCLINATION'], data['RA_OF_ASC_NODE'], data['ARG_OF_PERICENTER'], data['MEAN_ANOMALY'], 
                  data['EPHEMERIS_TYPE'], data['CLASSIFICATION_TYPE'], data['ELEMENT_SET_NO'], data['REV_AT_EPOCH'], 
                  data['BSTAR'], data['MEAN_MOTION_DOT'], data['MEAN_MOTION_DDOT'], data['SEMIMAJOR_AXIS'], data['PERIOD'], 
                  data['APOAPSIS'], data['PERIAPSIS'], data['OBJECT_TYPE'], data['RCS_SIZE'], data['COUNTRY_CODE'], 
                  data['LAUNCH_DATE'], data['SITE'], data['DECAY_DATE'], data['FILE'], data['GP_ID'], data['TLE_LINE0'], 
                  data['TLE_LINE1'], data['TLE_LINE2']))

            # Insert old data into gp_file_historical
            cursor.execute("""
                INSERT INTO gp_file_historical (NORAD_CAT_ID, gp_file_id, modification_timestamp, CCSDS_OMM_VERS, COMMENT, 
                CREATION_DATE, ORIGINATOR, OBJECT_NAME, OBJECT_ID, CENTER_NAME, REF_FRAME, TIME_SYSTEM, MEAN_ELEMENT_THEORY, 
                EPOCH, MEAN_MOTION, ECCENTRICITY, INCLINATION, RA_OF_ASC_NODE, ARG_OF_PERICENTER, MEAN_ANOMALY, EPHEMERIS_TYPE, 
                CLASSIFICATION_TYPE, ELEMENT_SET_NO, REV_AT_EPOCH, BSTAR, MEAN_MOTION_DOT, MEAN_MOTION_DDOT, SEMIMAJOR_AXIS, 
                PERIOD, APOAPSIS, PERIAPSIS, OBJECT_TYPE, RCS_SIZE, COUNTRY_CODE, LAUNCH_DATE, SITE, DECAY_DATE, FILE, GP_ID, 
                TLE_LINE0, TLE_LINE1, TLE_LINE2)
                SELECT * FROM gp_file WHERE NORAD_CAT_ID = %s
            """, (data['NORAD_CAT_ID'],))

            print("New data inserted into gp_file")
            conn.commit()
        else:
            print("Data already exists in gp_file")

    except psycopg2.Error as e:
        print("Error inserting data into gp_file:", e)
    finally:
        if conn is not None:
            conn.close()

def main():
    while True:
        data = fetch_data_from_api()
        if data is not None:
            insert_into_gp_file(data)
        time.sleep(5)

if __name__ == "__main__":
    main()
