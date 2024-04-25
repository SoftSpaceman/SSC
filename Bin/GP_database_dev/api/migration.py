




# detta är alltså vad som ska köras för att kopiera data från en tabell till en annan
#gp_file  >  gp_file_historical.
# detta gör efter att gp_file har populerats och kommer sanorlikt bara köras en gång. 

# Tanken är (logiken) att innan gp_file uppdareas så ska gp_file_historical uppdateras med datan baserat på ett kondition. 
# dagens datum. för att bara hämta datan som den själv inte har. 

# säg att båda tabellerna har updateras med samma query när de först skapas. 
# Då vill jag ju inte att gp_file_historical ska uppdateras med all data från gp_file igen eftersom all data inte updateras i gp_file när det ska köras automatiskt. 

import os
import psycopg2
from psycopg2 import Error
from datetime import datetime
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

        # Get the latest modification_timestamp from gp_file
        cursor.execute("SELECT MAX(modification_timestamp) FROM gp_file")
        latest_timestamp = cursor.fetchone()[0]

        # Execute the INSERT INTO SELECT statement with a WHERE clause to select only the rows with the latest timestamp
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
            WHERE 
                modification_timestamp = %s
        """, (latest_timestamp,))
        
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









# import psycopg2
# from psycopg2 import Error
# from datetime import datetime

# # Function to fetch data from source table based on a condition and insert into target table
# def copy_data_with_condition(source_table, target_table):
#     try:
#         # Connect to your PostgreSQL database
#         connection = psycopg2.connect(
#             host = "localhost",
#             dbname = "gpdata2",
#             user = "postgres",
#             password = "172121D",
#             port = "5432"
#         )
        
#         cursor = connection.cursor()

#         # Get today's date
#         today_date = datetime.now().date()

#         # Fetch data from source table based on condition (e.g., date column matching today's date)
#         cursor.execute(f"SELECT * FROM {source_table} WHERE date_column = %s", (today_date,))
#         rows = cursor.fetchall()

#         # Insert fetched data into target table
#         for row in rows:
#             cursor.execute(f"INSERT INTO {target_table} VALUES (%s, %s, %s)", row)

#         # Commit changes
#         connection.commit()
#         print("Data copied successfully!")

#     except (Exception, Error) as error:
#         print("Error:", error)
    
#     finally:
#         if connection:
#             cursor.close()
#             connection.close()
#             print("PostgreSQL connection is closed")

# # Example usage
# if __name__ == "__main__":
#     source_table = "gp_file"
#     target_table = "gp_file_historical"
#     copy_data_with_condition(source_table, target_table)
