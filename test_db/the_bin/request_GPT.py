
# This script/module handles making requests to an external API and processing the data received from the API.
# It typically contains functions for sending HTTP requests (e.g., using requests library), processing responses 
# (e.g., parsing JSON data), and extracting relevant information from the API responses.
# This script is responsible for the interaction between your application and the external API.

## FROM GPT 
## THIS CHAT:: (https://chat.openai.com/share/79d643d7-7438-45ff-99e2-0776da564913)

# space_track_request.py
import requests
import psycopg2
from datetime import datetime


###################################################################################################
# we havent made this script work yet. the Yasawiris_request.py script works fine.                #        
# The                                                           #                                 #
# PART from this script will be tested in the YASAWIRIS_REQUEST.PY script.                        # 
###################################################################################################

# a query that get every NORAD_CAT_ID greater than 1.0000 : https://www.space-track.org/basicspacedata/query/class/gp/NORAD_CAT_ID/%3C10000/orderby/NORAD_CAT_ID%20asc/emptyresult/show 

# a query that only gets 1 NORAD_CAT_ID: https://www.space-track.org/basicspacedata/query/class/gp/NORAD_CAT_ID/%3C10000/orderby/NORAD_CAT_ID%20asc/limit/1/emptyresult/show


# Function to request data from Space-track
def fetch_data():
    # Make HTTP request to Space-track API
    response = requests.get("https://www.space-track.org/basicspacedata/query/class/gp/NORAD_CAT_ID/%3C10000/orderby/NORAD_CAT_ID%20asc/limit/1/emptyresult/show")
    print("Requesting data from:", response)

    # Process response and extract data
    data = response.json()
    return data

# Function to log time when data is transferred
def log_transfer_time():
    current_time = datetime.now()
    # Log the transfer time to a file or database
    with open("transfer_log.txt", "a") as file:
        file.write(f"Transfer time: {current_time}\n")



# Function to populate database with fetched data
def populate_database():
    conn = psycopg2.connect(
        dbname="space_track",
        user="your_username",
        password="your_password",
        host="your_host",
        port="your_port"
    )
    cur = conn.cursor()
    data = fetch_data()
    for item in data:
        # Insert data into database
        cur.execute("INSERT INTO data (column1, column2, ...) VALUES (%s, %s, ...)", (item['value1'], item['value2'], ...))
    conn.commit()
    cur.close()
    conn.close()

    

# Main function
def main():
    populate_database()
    log_transfer_time()

if __name__ == "__main__":
    main()
