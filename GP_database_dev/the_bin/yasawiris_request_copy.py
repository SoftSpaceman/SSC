# this script is at its core from the Yasawiris project. https://github.com/ysawiris/space_track/blob/master/spack_track.py
# See https://www.space-track.org/documentation for details on REST queries

# Modifications will be made to fit the current project.

# AS OF NOW: 06/03/2024 
## This script fetches data from spacetrack without puting it any where.





import requests
import json
import configparser
import time
# from datetime import datetime
import psycopg2





class MyError(Exception):
    """Custom exception class."""
    def __init__(self, args):
        """Initialize MyError instance."""
        super().__init__("My exception was raised with arguments {0}".format(args))
        self.args = args


# login and request URL components to access the RESTful service at spce-track.org.
# uriBase                = "https://www.space-track.org"
# requestLogin           = "/ajaxauth/login"
# requestCmdAction       = "/basicspacedata/query"


# # Your credientials are stored in a file named APIconfig.ini. 
# # these are needed to log in to the space-track.org RESTful service.
# # Use configparser package to pull in the ini file (pip install configparser)
# config = configparser.ConfigParser()
# config.read(r'C:\Users\Bananberg\Desktop\Space_info\SSC\projects\SSC_database\test_db\api\APIconfig.ini')
# configUsr = config.get("configuration","username")
# configPwd = config.get("configuration","password")
# siteCred = {'identity': configUsr, 'password': configPwd}






###############################################################
# FOR THE SCRIPT BELOW. 

# Load the data into the database. [ ]
    # try with only 50 data points. [ ]

    # This query: /class/gp/NORAD_CAT_ID/%3C20000/orderby/NORAD_CAT_ID%20asc/emptyresult/show
    # has no limit but takes all GP data in order of NORAD_CAT_IDs above 20000.


    #this query: https://www.space-track.org/basicspacedata/query/class/gp/NORAD_CAT_ID/%3C10000/orderby/NORAD_CAT_ID%20asc/limit/50/emptyresult/show
        # is limted to only load 50 NORAD_CAT_ID and its corresponding data . 

    # This Query: https://www.space-track.org/basicspacedata/query/class/gp/NORAD_CAT_ID/%3C50000/orderby/NORAD_CAT_ID%20asc/limit/10/emptyresult/show
    # only outputs 10 NORAD_CAT_IDs and correspondig with a number above 50000. So we get some relevant data, just so we could have some consistan data with probalby all fields filled out. 

    # this query: https://www.space-track.org/basicspacedata/query/class/gp/orderby/NORAD_CAT_ID%20desc/limit/10/emptyresult/show
    # only outputs the lates 10 NORAD_CAT_IDs and corresponding data . of today 06/03/2024. 


    # check with your old script to se how you loaded the thata to a database. 






def getGP(uriBase, requestLogin, requestCmdAction, siteCred):
    requestGPdata = f'/class/gp/orderby/NORAD_CAT_ID%20desc/limit/10/emptyresult/show'

    # reads the file with the database credentials.
    config = configparser.ConfigParser()
    config.read(r'C:\Users\Bananberg\Desktop\Space_info\SSC\projects\SSC_database\test_db\database\table_config.ini')

    host = config.get("tables","host")
    dbname = config.get('tables', 'dbname')
    user = config.get('tables', 'user')
    password = config.get('tables', 'password')
    port = config.get('tables', 'port')

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

            # Prepare SQL query to insert fetched data into the database
            cursor = conn.cursor()
            for item in fetched_data:
                if not all(key in item for key in ('OBJECT_ID', 'OBJECT_NAME', 'OBJECT_TYPE', 'RCS_SIZE', 'LAUNCH_DATE', 'ORIGINATOR', 'SITE', 'DECAY_DATE', 'EPOCH', 'TIME_SYSTEM', 'NORAD_CAT_ID', 'CENTER_NAME', 'REF_FRAME', 'MEAN_ELEMENT_THEORY', 'PERIOD', 'APOAPSIS', 'PERIAPSIS', 'SEMIMAJOR_AXIS', 'MEAN_MOTION', 'ECCENTRICITY', 'INCLINATION', 'RA_OF_ASC_NODE', 'ARG_OF_PERICENTER', 'MEAN_ANOMALY', 'EPHEMERIS_TYPE', 'CLASSIFICATION_TYPE', 'ELEMENT_SET_NO', 'REV_AT_EPOCH', 'BSTAR', 'MEAN_MOTION_DOT', 'MEAN_MOTION_DDOT', 'CCSDS_OMM_VERS', 'COMMENT', 'CREATION_DATE', 'COUNTRY_CODE', 'FILE', 'GP_ID', 'TLE_LINE0', 'TLE_LINE1', 'TLE_LINE2'
                )):
                    print(f"Skipping item: Missing keys. Data: {item}")
                    continue  # Skip this item and move to the next

                cursor.execute("INSERT INTO satellite_data (OBJECT_ID, OBJECT_NAME, OBJECT_TYPE, RCS_SIZE, LAUNCH_DATE, ORIGINATOR, SITE, DECAY_DATE, EPOCH, TIME_SYSTEM, NORAD_CAT_ID, CENTER_NAME, REF_FRAME, MEAN_ELEMENT_THEORY, PERIOD, APOAPSIS, PERIAPSIS, SEMIMAJOR_AXIS, MEAN_MOTION, ECCENTRICITY, INCLINATION, RA_OF_ASC_NODE, ARG_OF_PERICENTER, MEAN_ANOMALY, EPHEMERIS_TYPE, CLASSIFICATION_TYPE, ELEMENT_SET_NO, REV_AT_EPOCH, BSTAR, MEAN_MOTION_DOT, MEAN_MOTION_DDOT, CCSDS_OMM_VERS, COMMENT, CREATION_DATE, COUNTRY_CODE, FILE, GP_ID, TLE_LINE0, TLE_LINE1, TLE_LINE2) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )", (['OBJECT_ID'],item['OBJECT_NAME'],item['OBJECT_TYPE'],item['RCS_SIZE'],item['LAUNCH_DATE'],item['ORIGINATOR'],item['SITE'],item['DECAY_DATE'],item['EPOCH'],item['TIME_SYSTEM'],item['NORAD_CAT_ID'],item['CENTER_NAME'],item['REF_FRAME'],item['MEAN_ELEMENT_THEORY'],item['PERIOD'],item['APOAPSIS'],item['PERIAPSIS'],item['SEMIMAJOR_AXIS'],item['MEAN_MOTION'],item['ECCENTRICITY'],item['INCLINATION'],item['RA_OF_ASC_NODE'],item['ARG_OF_PERICENTER'],item['MEAN_ANOMALY'],item['EPHEMERIS_TYPE'],item['CLASSIFICATION_TYPE'],item['ELEMENT_SET_NO'],item['REV_AT_EPOCH'],item['BSTAR'],item['MEAN_MOTION_DOT'],item['MEAN_MOTION_DDOT'],item['CCSDS_OMM_VERS'],item['COMMENT'],item['CREATION_DATE'],item['COUNTRY_CODE'],item['FILE'],item['GP_ID'],item['TLE_LINE0'],item['TLE_LINE1'],item['TLE_LINE2']))

            # Commit the transaction
            conn.commit()

            # Close cursor and connection
            cursor.close()

            return fetched_data
        
        except (psycopg2.Error, requests.RequestException) as e:
            print("Error:", e)
            return None

        except Exception as e:
            print("Error:", e)
            return None


        finally:  # makes sure the connection is closed after the data is fetched.
            session.close()
            conn.close()


# Call the function with appropriate parameters
uriBase                = "https://www.space-track.org"
requestLogin           = "/ajaxauth/login"
requestCmdAction       = "/basicspacedata/query"

config = configparser.ConfigParser()
config.read(r'C:\Users\Bananberg\Desktop\Space_info\SSC\projects\SSC_database\test_db\api\APIconfig.ini')
configUsr = config.get("configuration","username")
configPwd = config.get("configuration","password")
siteCred = {'identity': configUsr, 'password': configPwd}

fetched_data = getGP(uriBase, requestLogin, requestCmdAction, siteCred)

# Check if data was fetched successfully and print it
if fetched_data:
    print(fetched_data)
else:
    print("No data fetched.")








# tuple(item.values(['OBJECT_ID'],item['OBJECT_NAME'],item['OBJECT_TYPE'],item['RCS_SIZE'],item['LAUNCH_DATE'],item['ORIGINATOR'],item['SITE'],item['DECAY_DATE'],item['EPOCH'],item['TIME_SYSTEM'],item['NORAD_CAT_ID'],item['CENTER_NAME'],item['REF_FRAME'],item['MEAN_ELEMENT_THEORY'],item['PERIOD'],item['APOAPSIS'],item['PERIAPSIS'],item['SEMIMAJOR_AXIS'],item['MEAN_MOTION'],item['ECCENTRICITY'],item['INCLINATION'],item['RA_OF_ASC_NODE'],item['ARG_OF_PERICENTER'],item['MEAN_ANOMALY'],item['EPHEMERIS_TYPE'],item['CLASSIFICATION_TYPE'],item['ELEMENT_SET_NO'],item['REV_AT_EPOCH'],item['BSTAR'],item['MEAN_MOTION_DOT'],item['MEAN_MOTION_DDOT'],item['CCSDS_OMM_VERS'],item['COMMENT'],item['CREATION_DATE'],item['COUNTRY_CODE'],item['FILE'],item['GP_ID'],item['TLE_LINE0'],item['TLE_LINE1'],item['TLE_LINE2'])))


    

#######################################################################################################################
### TESTS FUNCTIONSFOR MODIFICATIONS ################# 





## THIS was just a stupid function to see if I could the amount of data gatherd. I got the number of caracters.
# def print_data_amount():
#     satellites = getGP()
#     data_amount = len(satellites)
#     print(f"Amount of data gathered: {data_amount} characters")

# print_data_amount()