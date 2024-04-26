import asyncio
import configparser
import os
import asyncpg
from datetime import datetime, timedelta

# https://chat.openai.com/c/8d433ee2-1e7f-40b3-ac4f-e78f7c302723#

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
    pass



async def fetch_data(conn, query, *args):
    rows = await conn.fetch(query, *args)
    return rows
    pass

# Function to check for outdated creation dates and print NORAD_CAT_IDs
async def check_outdated_creation_dates():
    conn = await connect_to_database()
    
    while True:
        try:
            outdated_ids = set()  # Using set to store unique NORAD_CAT_IDs
            
            # Fetch latest creation date for each unique NORAD_CAT_ID
            query = "SELECT norad_cat_id, MAX(creation_date) AS latest_creation_date FROM gp GROUP BY norad_cat_id"
            rows = await fetch_data(conn, query)
            
            # Iterate over fetched rows
            for row in rows:
                norad_cat_id = row["norad_cat_id"]
                latest_creation_date = row["latest_creation_date"]
                
                # Check if the latest creation date is older than the threshold
                if datetime.now() - latest_creation_date > timedelta(days=4):
                    outdated_ids.add(norad_cat_id)
            
            # Print the outdated NORAD_CAT_IDs count and the NORAD_CAT_IDs themselves
            print(f"{len(outdated_ids)} NORAD_CAT_ID(s) have outdated creation dates:")
            for norad_cat_id in outdated_ids:
                print(norad_cat_id)
            
            await asyncio.sleep(3600)  # Sleep for 1 hour before checking again (adjust as needed)
        
        except Exception as e:
            print(f"Error occurred: {e}")
            await asyncio.sleep(60)  # Sleep for 1 minute before retrying (adjust as needed)

# Run the asyncio event loop
async def main():
    await check_outdated_creation_dates()

if __name__ == "__main__":
    asyncio.run(main())
