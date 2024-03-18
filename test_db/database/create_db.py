
# this script workes just fine! The databse has been successfully created. 01/03/2024

# QUESTIONS: 
# IS thera a point to fit the tabel creation queries in the create_database() function?
# so far we are going to put it in db_functions.py

import psycopg2
import configparser


config = configparser.ConfigParser()
config.read(r'C:\Users\Bananberg\Desktop\Space_info\SSC\projects\SSC_database\test_db\database\database_config.ini')

host = config.get("database","host")
dbname = config.get('database', 'dbname')
user = config.get('database', 'user')
password = config.get('database', 'password')
port = config.get('database', 'port')




def create_database():

    try:
        # Connect to the default 'postgres' database to create a new database
        conn = psycopg2.connect(
            # dbname='postgres', 
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

        # Execute SQL query to create a new database
        cursor.execute("CREATE DATABASE gpdata_with_history")

        print("Database created successfully!")

  
    except psycopg2.Error as e:
        print("Error while connecting to PostgreSQL:", e)

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


