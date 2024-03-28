# this script workes just fine! The databse has been successfully created. 01/03/2024
# the original file wa meant to be named database_functions.py Byt had to be renamed to create_tables.py


import os
import psycopg2
import configparser




# config = configparser.ConfigParser()
# config.read(r'C:\Users\Bananberg\Desktop\Space_info\SSC\projects\SSC_database\test_db\database\database_config.ini')

# host = config.get("tables","host")
# dbname = config.get('tables', 'dbname')
# user = config.get('tables', 'user')
# password = config.get('tables', 'password')
# port = config.get('tables', 'port')



def create_tables():


    # Get the directory path of the current script
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # Navigate to the parent directory (one level up from the current script directory)
    parent_dir = os.path.dirname(script_dir)

    # Construct the path to the config directory
    config_dir = os.path.join(parent_dir, 'config')

    # Construct the full path to the config.ini file
    config_file_path = os.path.join(config_dir, 'config.ini')

    # Initialize config parser
    config = configparser.ConfigParser()

    # Read the configuration file
    config.read(config_file_path)

    # Get database connection parameters
    host = config.get('tables', 'host')
    dbname = config.get('tables', 'dbname')
    user = config.get('tables', 'user')
    password = config.get('tables', 'password')
    port = config.get('tables', 'port')





    try:
        # Connect to the database
        conn = psycopg2.connect(
            # dbname='new_database_name',  
            # user='postgres', 
            # password='172121D', 
            # host='localhost', 
            # port='5432'
            host=host, 
            dbname=dbname, 
            user=user, 
            password=password, 
            port=port
        )

        conn.autocommit = True
        cursor = conn.cursor()

        # Define your table creation queries here
        # the logic in the database needs to be updated to reflect the changes in the data.
        # meening that the history table needs to be allowed to store all the data from the main table and duplicate NORAD_CAT_ID? 
        # Since the data is being updated and not deleted, the history table should be able to store all the data from the main table.
        # Also do spacetrack update only a few data when they have it r a block of data? 
        # There might need to be a function that tells what data related to the object that have been updated... 
        
        # after a successful update, the new data have to be comaared to the old data to see what data that usally gets updated... 
        # I think that spacetrack updates a block of data, meaning a block of NORAD_CAT_IDs and the corresponding data.
        table_queries = [
        """
            CREATE TABLE gp_file (
                gp_file_id SERIAL PRIMARY KEY,
                NORAD_CAT_ID INT UNIQUE,  -- Removed unsigned
                modification_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CCSDS_OMM_VERS varchar(3),
                COMMENT varchar(33),
                CREATION_DATE TIMESTAMP(6),
                EPOCH TIMESTAMP(6),
                ORIGINATOR varchar(7),
                OBJECT_NAME varchar(25),
                OBJECT_ID varchar(12),
                CENTER_NAME varchar(5),     -- Allows null values
                REF_FRAME varchar(4),       -- Allows null values
                TIME_SYSTEM varchar(3),     -- Allows null values
                MEAN_ELEMENT_THEORY varchar(4),  -- Allows null values
                MEAN_MOTION DECIMAL(13,8),
                ECCENTRICITY DECIMAL(13,8),
                INCLINATION DECIMAL(7,4),
                RA_OF_ASC_NODE DECIMAL(7,4),
                ARG_OF_PERICENTER DECIMAL(7,4),
                MEAN_ANOMALY DECIMAL(7,4),
                EPHEMERIS_TYPE SMALLINT,
                CLASSIFICATION_TYPE CHAR(1),
                ELEMENT_SET_NO SMALLINT,
                REV_AT_EPOCH INT,
                BSTAR DECIMAL(19,14),
                MEAN_MOTION_DOT DECIMAL(9,8),
                MEAN_MOTION_DDOT DECIMAL(22,13),
                SEMIMAJOR_AXIS DOUBLE PRECISION,
                PERIOD DOUBLE PRECISION,
                APOAPSIS DOUBLE PRECISION,
                PERIAPSIS DOUBLE PRECISION,
                OBJECT_TYPE varchar(12),
                RCS_SIZE CHAR(6),
                COUNTRY_CODE CHAR(6),
                LAUNCH_DATE DATE,
                SITE CHAR(5),
                DECAY_DATE DATE,
                FILE BIGINT, -- Removed unsigned
                GP_ID INT, -- Removed unsigned
                TLE_LINE0 varchar(27),
                TLE_LINE1 varchar(71),
                TLE_LINE2 varchar(71)
                 
);

        CREATE TABLE gp_file_historical (
            history_id SERIAL PRIMARY KEY,
            gp_file_id INT REFERENCES gp_file(gp_file_id),
            NORAD_CAT_ID INT,
            modification_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,      -- the time the data from gp_file got stored in the history table
            CCSDS_OMM_VERS varchar(3),
            COMMENT varchar(33),
            CREATION_DATE TIMESTAMP(6),
            EPOCH TIMESTAMP(6),
            ORIGINATOR varchar(7),
            OBJECT_NAME varchar(25),
            OBJECT_ID varchar(12),
            CENTER_NAME varchar(5),
            REF_FRAME varchar(4),
            TIME_SYSTEM varchar(3),
            MEAN_ELEMENT_THEORY varchar(4),
            MEAN_MOTION DECIMAL(13,8),
            ECCENTRICITY DECIMAL(13,8),
            INCLINATION DECIMAL(7,4),
            RA_OF_ASC_NODE DECIMAL(7,4),
            ARG_OF_PERICENTER DECIMAL(7,4),
            MEAN_ANOMALY DECIMAL(7,4),
            EPHEMERIS_TYPE SMALLINT,
            CLASSIFICATION_TYPE CHAR(1),
            ELEMENT_SET_NO SMALLINT,
            REV_AT_EPOCH INT,
            BSTAR DECIMAL(19,14),
            MEAN_MOTION_DOT DECIMAL(9,8),
            MEAN_MOTION_DDOT DECIMAL(22,13),
            SEMIMAJOR_AXIS DOUBLE PRECISION,
            PERIOD DOUBLE PRECISION,
            APOAPSIS DOUBLE PRECISION,
            PERIAPSIS DOUBLE PRECISION,
            OBJECT_TYPE varchar(12),
            RCS_SIZE CHAR(6),
            COUNTRY_CODE CHAR(6),
            LAUNCH_DATE DATE,
            SITE CHAR(5),
            DECAY_DATE DATE,
            FILE BIGINT,
            GP_ID INT,
            TLE_LINE0 varchar(27),
            TLE_LINE1 varchar(71),
            TLE_LINE2 varchar(71)

);

            """

            # Add more table creation queries as needed
        ]

        # Execute each table creation query
        for query in table_queries:
            cursor.execute(query)

        print("Tables created successfully!")

    except psycopg2.Error as e:
        print("Error while connecting to PostgreSQL:", e)

    finally:
        # Close database connection
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    create_tables()


#     CREATE TABLE satellite_data (

#   sat_id SERIAL PRIMARY KEY,
#   OBJECT_ID varchar(12) NOT NULL,
#   OBJECT_NAME varchar(20) NOT NULL,
#   OBJECT_TYPE varchar(12) NOT NULL,
#   RCS_SIZE varchar(10),
#   LAUNCH_DATE date,	--datetime
#   ORIGINATOR char(8),
#   site char(5),
#   DECAY_DATE date, --datetime
#   -- Add version column
#   version int DEFAULT 1 NOT NULL,
#   EPOCH date, 		-- datatime
#   TIME_SYSTEM varchar(3),
#   NORAD_CAT_ID int,  			--(10)
#   CENTER_NAME varchar(5),
#   REF_FRAME varchar(4),
#   MEAN_ELEMENT_THEORY varchar(4),
#   PERIOD double precision, --(12,3)
#   APOAPSIS double precision, --(12,3)
#   PERIAPSIS double precision, --(12,3)
#   SEMIMAJOR_AXIS double precision, --(12,3)
#   MEAN_MOTION decimal(13,8),
#   ECCENTRICITY decimal(13,8),
#   INCLINATION decimal(7,4),
#   RA_OF_ASC_NODE decimal(7,4),
#   ARG_OF_PERICENTER decimal(7,4),
#   MEAN_ANOMALY decimal(7,4),
#   EPHEMERIS_TYPE smallint,  -- tinyint(4)
#   CLASSIFICATION_TYPE char(1),
#   ELEMENT_SET_NO smallint,	--(5)
#   REV_AT_EPOCH smallint, -- mediumint(8)
#   BSTAR decimal(19,14),
#   MEAN_MOTION_DOT decimal(9,8),
#   MEAN_MOTION_DDOT decimal(22,13),
#   CCSDS_OMM_VERS varchar(3),
#   COMMENT text,
#   CREATION_DATE date,
#   COUNTRY_CODE char(6),
#   FILE bigint,	--(20)
#   GP_ID int, -- (10)
#   TLE_LINE0 varchar(27),
#   TLE_LINE1 varchar(71),
#   TLE_LINE2 varchar(71),
#   start_date date,
#   end_date date
# );
