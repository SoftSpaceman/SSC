import asyncpg
import configparser

import os

# Load authentication credentials from config.ini
def load_config(filename='config.ini'):
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', filename)
    config = configparser.ConfigParser()
    config.read(config_path)
    return config['tables']



async def connect_to_database():
    # Load database connection details from config.ini
    db_config = load_config()
    
    conn = await asyncpg.connect(user=db_config['user'], password=db_config['password'],
                                 database=db_config['dbname'], host=db_config['host'])
    return conn



async def execute_query(conn, query):
    result = await conn.execute(query)
    return result




async def fetch_data(conn, query, *args):
    rows = await conn.fetch(query, *args)
    return rows




async def close_connection(conn):
    await conn.close()
