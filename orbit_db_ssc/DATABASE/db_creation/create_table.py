


# This script creates the tables in the database. 
# The tables are created based on the configuration file (config.ini) in the CONFIG directory.



import os
import psycopg2
import configparser
import logging

def setup_logging():
    log_format = '%(asctime)s - %(levelname)s - %(message)s - %(filename)s - line: %(lineno)d'
    logging.basicConfig(filename='database_creation.log', level=logging.DEBUG, format=log_format)




def create_tables():
    setup_logging()

    # Get the directory path of the current script
    script_dir = os.path.dirname(os.path.dirname(__file__))

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
            host=host,
            dbname=dbname,
            user=user,
            password=password,
            port=port
        )

        conn.autocommit = True
        cursor = conn.cursor()


        # Define your table creation queries here
        ########## Definition of each column is located in documentation file. #############

        table_queries = [
            """
        CREATE TABLE IF NOT EXISTS gp (
            -- Define table columns here (abbreviated for brevity)
            id SERIAL PRIMARY KEY,
            insertion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            NORAD_CAT_ID INT NOT NULL,
            CREATION_DATE TIMESTAMP,
            data_decay INT,
            EPOCH TIMESTAMP,
            ORIGINATOR VARCHAR(7) NOT NULL,
            OBJECT_NAME VARCHAR(25),
            OBJECT_ID VARCHAR(12),
            OBJECT_TYPE VARCHAR(12),
            RCS_SIZE CHAR(6),
            COUNTRY_CODE CHAR(6),
            LAUNCH_DATE DATE,
            SITE CHAR(5),
            DECAY_DATE DATE,
            FILE BIGINT,
            COMMENT VARCHAR(33) NOT NULL,
            CENTER_NAME VARCHAR(5) NOT NULL,
            REF_FRAME VARCHAR(4) NOT NULL,
            TIME_SYSTEM VARCHAR(3) NOT NULL,
            MEAN_ELEMENT_THEORY VARCHAR(4) NOT NULL,
            MEAN_MOTION DECIMAL(13,8),
            ECCENTRICITY DECIMAL(13,8),
            INCLINATION DECIMAL(7,4),
            RA_OF_ASC_NODE DECIMAL(7,4),
            ARG_OF_PERICENTER DECIMAL(7,4),
            MEAN_ANOMALY DECIMAL(7,4),
            EPHEMERIS_TYPE SMALLINT,
            CLASSIFICATION_TYPE CHAR(1),
            CCSDS_OMM_VERS VARCHAR(3) NOT NULL,
            ELEMENT_SET_NO SMALLINT,
            REV_AT_EPOCH INT,
            BSTAR DECIMAL(19,14),
            MEAN_MOTION_DOT DECIMAL(9,8),
            MEAN_MOTION_DDOT DECIMAL(22,13),
            SEMIMAJOR_AXIS DOUBLE PRECISION,
            PERIOD DOUBLE PRECISION,
            APOAPSIS DOUBLE PRECISION,
            PERIAPSIS DOUBLE PRECISION,
            GP_ID INT NOT NULL,
            TLE_LINE0 VARCHAR(27),
            TLE_LINE1 VARCHAR(71),
            TLE_LINE2 VARCHAR(71),
            data_hash VARCHAR(64) UNIQUE NOT NULL
            );
            """
        ]

        # Execute each table creation query
        for query in table_queries:
            cursor.execute(query)

        logging.info("Tables created successfully!")

    except psycopg2.Error as e:
        logging.error("Error while connecting to PostgreSQL: %s", e)

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
