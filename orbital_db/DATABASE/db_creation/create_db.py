
# this script workes just fine! The databse has been successfully created. 01/03/2024

# QUESTIONS: 
# IS thera a point to fit the tabel creation queries in the create_database() function?
# so far we are going to put it in the create_tables() function.

import os
import psycopg2
import configparser
import logging

def setup_logging():        # join to join the current directory with the log file name
    log_filename = os.path.join(os.getcwd(), 'database_creation.log')
    log_format = '%(asctime)s - %(levelname)s - %(message)s - %(filename)s - line: %(lineno)d'
    logging.basicConfig(filename=log_filename, level=logging.DEBUG, format=log_format)



def create_database():
    setup_logging()
    ############################################################################################################
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
    host = config.get('database', 'host')
    dbname = config.get('database', 'dbname')
    user = config.get('database', 'user')
    password = config.get('database', 'password')
    port = config.get('database', 'port')

    ############################################################################################################

    try:
        # Connect to the default 'postgres' database to create a new database
        conn = psycopg2.connect(
            host=host,
            dbname=dbname,
            user=user,
            password=password,
            port=port
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Execute SQL query to create a new database
        cursor.execute("CREATE DATABASE orbital_db") # gpdata_with_history

        logging.info("Database created successfully!")

    except psycopg2.Error as e:
        logging.error("Error while connecting to PostgreSQL: %s", e)

    finally:
        # Close database connection
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    create_database()









###################### THE BIN ############################################
    
## A SCRIPT TO CREATE TABELS IN A DATABASE. 
        #     # Connect to the newly created database
        # conn = psycopg2.connect(
        #     dbname='new_database_name', user='postgres', password='172121D', host='localhost', port='5432'
        # )
        # cursor = conn.cursor()

        # # Create tables within the new database
        # cursor.execute("CREATE TABLE my_table (id serial PRIMARY KEY, name varchar(50))")
        # # Add more table creation queries as needed




####### THE POSTGRESQL TBLE CREATION QUERIES ################################
 #   It is testsed and modifie in the query tool on PGAdmin. 
    # its from a early verson of the database.


