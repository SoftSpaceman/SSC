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


class MyError(Exception):
    def __init__(self,args):
        Exception.__init__(self,"my exception was raised with arguments {0}".format(args))
        self.args = args


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



def getGP():  # importing and feed in ex. date into the () of this function lets you specefi what date you want to get data from.
                # it hase to be added in the APIA request file as well. Se soruce code. 


    requestGPdata   = f'/class/gp/orderby/NORAD_CAT_ID%20desc/limit/10/emptyresult/show'
    # use requests package to drive the RESTful session with space-track.org
    with requests.Session() as session:
        try:
            # run the session in a with block to force session to close if we exit

            # need to log in first. note that we get a 200 to say the web site got the data, not that we are logged in
            resp = session.post(uriBase + requestLogin, data = siteCred)
            if resp.status_code != 200:
                raise MyError(resp, "POST fail on login")

            # this query picks up GPs for all satellites from the catalog. Note - a 401 failure shows you have bad credentials 
            resp = session.get(uriBase + requestCmdAction + requestGPdata)
            if resp.status_code != 200:
                print(resp)
                raise MyError(resp, "GET fail on request for satellites")

            # Store fetched data in a variable
            fetched_data = resp.json()
            return fetched_data	 
        
            #insert_json_data(fetched_data)

        except Exception as e:
            print("Error:", e)
            return None
        
        finally:   # makes sure the connection is cloes after the data is fetched.
            session.close()


# Call the function, here ex. date can be specified in the function call = ( ) to get data from a speceifc date... 
fetched_data = getGP()

# Check if data was fetched successfully and print it
if fetched_data:
    print(fetched_data)
else:
    print("No data fetched.")



# this script wors as of now. 08/03/2024.








    

#######################################################################################################################
### TESTS FUNCTIONSFOR MODIFICATIONS ################# 





## THIS was just a stupid function to see if I could the amount of data gatherd. I got the number of caracters.
# def print_data_amount():
#     satellites = getGP()
#     data_amount = len(satellites)
#     print(f"Amount of data gathered: {data_amount} characters")

# print_data_amount()