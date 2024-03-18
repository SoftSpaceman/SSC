

# This script/module contains functions for interacting with a PostgreSQL database.
# It typically includes functions for creating tables, inserting data, querying data, updating data, 
# and any other database operations required by your application.
# This script abstracts away the database operations, making it easier to manage database-related tasks in your application.



## EXPLANATION OF THE SCRIPT ## 

# This script is designed to connect to a PostgreSQL database, perform an operation, and then close the connection.

# Here's a breakdown of its functions:

# Importing libraries:

# psycopg2: This library allows Python to interact with PostgreSQL databases.
# config.secrets: This module likely holds sensitive information like database credentials, which should be stored securely outside the script.


# connect_to_database function:
# Attempts to establish a connection to the database using the credentials stored in config.secrets.
# If successful, returns the connection object.
# If an error occurs, prints the error message and returns None.


# close_connection function:
# Takes a connection object as input.
# Checks if the connection is not None (meaning it's established).
# If the connection is active, closes it and prints a message indicating closure.


# perform_database_operation function:
# Calls connect_to_database to establish a connection.
# If connected, creates a cursor object to interact with the database.
# Executes the provided sql_query on the database.
# Commits the changes made by the query (if applicable).
# Prints a success message if the operation is successful.
# Catches any psycopg2 errors during execution and prints an error message.
# Always calls close_connection to ensure the connection is closed, even in case of errors (using a finally block).
# This script provides a basic structure for interacting with a PostgreSQL database from Python. It emphasizes proper connection handling and error management. However, it's important to note that:

# The script relies on external modules like psycopg2 and config.secrets to function.
# It doesn't handle specific SQL queries, and the actual query logic would be implemented within the perform_database_operation function.


import psycopg2



def insert_json_data(fetched_data):
  """Inserts JSON data into a PostgreSQL table named 'gpdata'.

  Args:
      fetched_data: A list of dictionaries containing satellite data.
  """
  # Connect to the PostgreSQL database
  conn = psycopg2.connect(
      database="your_database_name",
      user="your_username",
      password="your_password",
      host="your_host",
      port="your_port"
  )

  # Create a cursor object
  cursor = conn.cursor()

  # Create the table if it doesn't exist (omit this if table already exists)
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS satellite_data (

        sat_id SERIAL PRIMARY KEY,
        OBJECT_ID varchar(12) NOT NULL,
        OBJECT_NAME varchar(20) NOT NULL,
        OBJECT_TYPE varchar(12) NOT NULL,
        RCS_SIZE varchar(10),
        LAUNCH_DATE date,	
        ORIGINATOR char(8),
        site char(5),
        DECAY_DATE date, 
        EPOCH date, 		
        TIME_SYSTEM varchar(3),
        NORAD_CAT_ID int,  			
        CENTER_NAME varchar(5),
        REF_FRAME varchar(4),
        MEAN_ELEMENT_THEORY varchar(4),
        PERIOD double precision, 
        APOAPSIS double precision, 
        PERIAPSIS double precision, 
        SEMIMAJOR_AXIS double precision, 
        MEAN_MOTION decimal(13,8),
        ECCENTRICITY decimal(13,8),
        INCLINATION decimal(7,4),
        RA_OF_ASC_NODE decimal(7,4),
        ARG_OF_PERICENTER decimal(7,4),
        MEAN_ANOMALY decimal(7,4),
        EPHEMERIS_TYPE smallint, 
        CLASSIFICATION_TYPE char(1),
        ELEMENT_SET_NO smallint,	
        REV_AT_EPOCH smallint, 
        BSTAR decimal(19,14),
        MEAN_MOTION_DOT decimal(9,8),
        MEAN_MOTION_DDOT decimal(22,13),
        CCSDS_OMM_VERS varchar(3),
        COMMENT text,
        CREATION_DATE date,
        COUNTRY_CODE char(6),
        FILE bigint,	
        GP_ID int, 
        TLE_LINE0 varchar(27),
        TLE_LINE1 varchar(71),
        TLE_LINE2 varchar(71),

);
            """)
  
for satellite in fetched_data:
    data_tuple = (
        satellite['sat_id'],
        satellite['OBJECT_ID'],
        satellite['OBJECT_NAME'],
        satellite['OBJECT_TYPE'] 
        satellite['RCS_SIZE'],
        satellite['LAUNCH_DATE'],	
        satellite['ORIGINATOR'],
        satellite['site'],
        satellite['DECAY_DATE'], 
        satellite['TIME_SYSTEM'],
        satellite['NORAD_CAT_ID'],  			
        satellite['CENTER_NAME'],
        satellite['REF_FRAME'],
        satellite['MEAN_ELEMENT_THEORY'],
        satellite['PERIOD'], 
        satellite['APOAPSIS'], 
        satellite['PERIAPSIS'], 
        satellite['SEMIMAJOR_AXIS'], 
        satellite['MEAN_MOTION'],
        satellite['ECCENTRICITY'],
        satellite['INCLINATION'],
        satellite['RA_OF_ASC_NODE'],
        satellite['ARG_OF_PERICENTER'],
        satellite['MEAN_ANOMALY'],
        satellite['EPHEMERIS_TYPE'], 
        satellite['CLASSIFICATION_TYPE'],
        satellite['ELEMENT_SET_NO'],	
        satellite['REV_AT_EPOCH'], 
        satellite['BSTAR'],
        satellite['MEAN_MOTION_DOT'],
        satellite['MEAN_MOTION_DDOT'],
        satellite['CCSDS_OMM_VERS'],
        satellite['COMMENT'],
        satellite['CREATION_DATE'],
        satellite['COUNTRY_CODE'],
        satellite['FILE'],	
        satellite['GP_ID'], 
        satellite['TLE_LINE0'],
        satellite['TLE_LINE1'],
        satellite['TLE_LINE2'],
    )

    cursor.execute("""
    INSERT INTO SATCAT (
        INTLDES, NORAD_CAT_ID, OBJECT_TYPE, SATNAME, COUNTRY, LAUNCH, SITE, DECAY, PERIOD, 
        INCLINATION, APOGEE, PERIGEE, COMMENT, COMMENTCODE, RCSVALUE, RCS_SIZE, FILE, 
        LAUNCH_YEAR, LAUNCH_NUM, LAUNCH_PIECE, CURRENT, OBJECT_NAME, OBJECT_ID, OBJECT_NUMBER
    )
    VALUES (%(INTLDES)s, %(NORAD_CAT_ID)s, %(OBJECT_TYPE)s, %(SATNAME)s, %(COUNTRY)s, 
            %(LAUNCH)s, %(SITE)s, %(DECAY)s, %(PERIOD)s, %(INCLINATION)s, %(APOGEE)s, 
            %(PERIGEE)s, %(COMMENT)s, %(COMMENTCODE)s, %(RCSVALUE)s, %(RCS_SIZE)s, 
            %(FILE)s, %(LAUNCH_YEAR)s, %(LAUNCH_NUM)s, %(LAUNCH_PIECE)s, %(CURRENT)s, 
            %(OBJECT_NAME)s, %(OBJECT_ID)s, %(OBJECT_NUMBER)s)
    """, satellite)

  # Commit the changes and close the connection
  conn.commit()
  conn.close()

