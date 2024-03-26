
# https://chat.openai.com/share/b9a0d2f2-12d4-4963-b656-f724bf691844



import psycopg2
import requests
import logging
import configparser
import time
import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MyError(Exception):
    """Custom exception class."""
    def __init__(self, args):
        """Initialize MyError instance."""
        super().__init__("My exception was raised with arguments {0}".format(args))
        self.args = args


# Global variables
uriBase = "https://www.space-track.org"
requestLogin = "/ajaxauth/login"
requestCmdAction = "/basicspacedata/query"
requestGPdata = f'/class/gp/orderby/NORAD_CAT_ID%20desc/limit/10/emptyresult/show'


config = configparser.ConfigParser()
config.read(r'C:\Users\Bananberg\Desktop\Space_info\SSC\projects\SSC_database\test_db\api\APIconfig.ini')
configUsr = config.get("configuration","username")
configPwd = config.get("configuration","password")
siteCred = {'identity': configUsr, 'password': configPwd}








# the session argument is defineded in the main function. 
# https://g.co/gemini/share/51e25e29d1dc
def fetch_data_from_api(session):
    try:
        resp = session.post(uriBase + requestLogin, data=siteCred)
        if resp.status_code != 200:
            raise Exception(f"POST fail on login. Status code: {resp.status_code}")

        resp = session.get(uriBase + requestCmdAction + requestGPdata)
        if resp.status_code != 200:
            raise Exception(f"GET fail on request for satellites. Status code: {resp.status_code}")

        data = resp.json()
        return data
    except requests.RequestException as e:
        print("Error fetching data from API:", e)
        return None


def update_gp_file(conn, data):
    #Updates the gp_file table with the provided data.
    # Handles potential errors during data conversion and database updates.

    try:
        cursor = conn.cursor()  # Create a cursor object to execute SQL queries
        for item in data:
            
            # Define each object name as a variable
            cursor.execute("""
                UPDATE gp_file 
                SET 
                    CCSDS_OMM_VERS = %s, COMMENT = %s, CREATION_DATE = %s, ORIGINATOR = %s, OBJECT_NAME = %s, OBJECT_ID = %s, CENTER_NAME = %s,
                    REF_FRAME = %s, TIME_SYSTEM = %s, MEAN_ELEMENT_THEORY = %s, EPOCH = %s, MEAN_MOTION = %s, ECCENTRICITY = %s,
                    INCLINATION = %s, RA_OF_ASC_NODE = %s, ARG_OF_PERICENTER = %s, MEAN_ANOMALY = %s, EPHEMERIS_TYPE = %s,
                    CLASSIFICATION_TYPE = %s, ELEMENT_SET_NO = %s, REV_AT_EPOCH = %s, BSTAR = %s, MEAN_MOTION_DOT = %s,
                    MEAN_MOTION_DDOT = %s, SEMIMAJOR_AXIS = %s, PERIOD = %s, APOAPSIS = %s, PERIAPSIS = %s,
                    OBJECT_TYPE = %s, RCS_SIZE = %s, COUNTRY_CODE = %s, LAUNCH_DATE = %s, SITE = %s,
                    DECAY_DATE = %s, FILE = %s, GP_ID = %s, TLE_LINE0 = %s, TLE_LINE1 = %s,
                    TLE_LINE2 = %s    
                WHERE NORAD_CAT_ID = %s
            """, ( item['CCSDS_OMM_VERS'], item['COMMENT'], item['CREATION_DATE'],
                  item['ORIGINATOR'], item['OBJECT_NAME'], item['NORAD_CAT_ID'], item['OBJECT_ID'], item['CENTER_NAME'], item['REF_FRAME'], item['TIME_SYSTEM'], item['MEAN_ELEMENT_THEORY'], item['EPOCH'], item['MEAN_MOTION'], item['ECCENTRICITY'], item['INCLINATION'], item['RA_OF_ASC_NODE'], item['ARG_OF_PERICENTER'], item['MEAN_ANOMALY'], item['EPHEMERIS_TYPE'], item['CLASSIFICATION_TYPE'], item['ELEMENT_SET_NO'], item['REV_AT_EPOCH'], item['BSTAR'], item['MEAN_MOTION_DOT'], item['MEAN_MOTION_DDOT'], item['SEMIMAJOR_AXIS'], item['PERIOD'], item['APOAPSIS'], item['PERIAPSIS'], item['OBJECT_TYPE'], item['RCS_SIZE'], item['COUNTRY_CODE'], item['LAUNCH_DATE'], item['SITE'], item['DECAY_DATE'], item['FILE'], item['GP_ID'], item['TLE_LINE0'], item['TLE_LINE1'], item['TLE_LINE2']))  #datetime.now(),

            ####### SOLVED #######
            # We have a weird issue here: Error updating data in gp_file: syntax error at or near "270288"
                # LINE 4: ...JECT_NAME = 'TBA - TO BE ASSIGNED', OBJECT_ID = ''270288'', ...
            # this error occurs when the trying to udate... 
            ####### SOLVED #######

            # now we got this: Error updating data in gp_file: invalid input syntax for type integer: "2 T0288  90.2493 347.9789 0031101 137.6422 222.7107 12.95455175187028"
            # LINE 12:                 WHERE NORAD_CAT_ID = '2 T0288  90.2493 347.9...
            # It is reading in a TLE so the statement is wrong. 


            print("Updated item with NORAD_CAT_ID:", item['NORAD_CAT_ID'])
            conn.commit()  # Commit the transaction

    except psycopg2.Error as e:
        print("Error updating data in gp_file:", e)


def main():
    config = configparser.ConfigParser()
    config.read(r'C:\Users\Bananberg\Desktop\Space_info\SSC\projects\SSC_database\test_db\database\database_config.ini')

    host = config.get("tables", "host")
    dbname = config.get('tables', 'dbname')
    user = config.get('tables', 'user')
    password = config.get('tables', 'password')
    port = config.get('tables', 'port')

    conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)

    session = requests.Session()
    siteCred = {'identity': user, 'password': password}

    while True:
        data = fetch_data_from_api(session)
        if data:
            update_gp_file(conn, data)
            print("Resting for 5 seconds...")
        time.sleep(5)

    conn.close()


if __name__ == "__main__":
    main()