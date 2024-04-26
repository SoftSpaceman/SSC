from database_operations import close_connection, connect_to_database, load_config, fetch_data, execute_query


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
import logging
import asyncpg
import bcrypt



from alert_system import router as send_alert_route
#from alert_system import router as set_alert_route
#from alert_system import router as receive_object_data_route
#from alert_system import router as get_object_data_route

# 127.0.0.1:8000/docs#/




app = FastAPI()

app.include_router(send_alert_route)
#app.include_router(set_alert_route)
#app.include_router(receive_object_data_route)
#app.include_router(get_object_data)


# Function to configure logger
def configure_logger():
    # Create a logger
    logger = logging.getLogger("orbital_data_logger")
    # Set logging level to DEBUG
    logger.setLevel(logging.DEBUG)
    # Define a file handler and set formatter
    file_handler = logging.handlers.RotatingFileHandler(
        "application.log",
        maxBytes=1024 * 1024,  # Set max size to 1 MB
        backupCount=4  # Keep up to 5 backup files
    )
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') 
    file_handler.setFormatter(formatter)
    # Add the file handler to the logger
    logger.addHandler(file_handler)
    return logger

# Get logger
logger = configure_logger()




################################################################################################
################# TESTING GROUNDS ##################### 15/05/2024 #############################







class SubsetRequest(BaseModel):
    NORAD_IDs: List[int]

@app.post("/subset_newest_data/")
async def create_subset(subset_request: SubsetRequest):
    try:
        conn = await connect_to_database()
        subset = []
        for norad_id in subset_request.NORAD_IDs:
            query = """
                SELECT *
                FROM gp
                WHERE (norad_cat_id, creation_date) IN (
                    SELECT norad_cat_id, MAX(creation_date) AS latest_creation_date
                    FROM gp
                    WHERE norad_cat_id = $1
                    GROUP BY norad_cat_id
                )
            """
            rows = await fetch_data(conn, query, norad_id)
            if rows:
                subset.extend(rows)
        return {"subset": subset}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        if conn:
            await close_connection(conn)





#####################################################################################
# http://127.0.0.1:8000/display_table

# Display table endpoint
@app.get("/display_table")
async def display_table():
    try:
        conn = await connect_to_database()
        data = await fetch_data(conn, """SELECT DISTINCT NORAD_CAT_ID, CREATION_DATE, OBJECT_NAME, epoch, tle_line1, tle_line2
                                            FROM gp 
                                            ORDER by CREATION_DATE desc , NORAD_CAT_ID  
                                            LIMIT 10; """)
        await close_connection(conn)
        return {"table_data": data}
    except Exception as e:
        logger.error(f"Error occurred during display_table: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")






#####################################################################################


# Custom subset creation endpoint
#@app.post("/custom_subset")
async def create_custom_subset(norad_ids: List[int]):
    try:
        # Validate input: Ensure the list of NORAD IDs is not empty
        if not norad_ids:
            raise HTTPException(status_code=400, detail="Please provide a non-empty list of NORAD IDs")

        # Connect to the database
        conn = await connect_to_database()

        # Convert the list of NORAD IDs to a tuple for SQL parameterization
        norad_ids_tuple = tuple(norad_ids)

        # Execute SQL query to fetch data for the specified NORAD IDs with the latest epoch
        query = """
            SELECT *
            FROM gp
            WHERE (norad_cat_id, epoch) IN (
                SELECT norad_cat_id, MAX(epoch) AS latest_epoch
                FROM gp
                WHERE norad_cat_id = ANY($1)
                GROUP BY norad_cat_id
            )
        """
        
        data = await fetch_data(conn, query, norad_ids_tuple)

        # Close the database connection
        await close_connection(conn)

        # Check if any result is found
        if data:
            return {"custom_subset": data}
        else:
            # If no result found, raise HTTPException with status code 404 (Not Found)
            raise HTTPException(status_code=404, detail="No objects found for the specified NORAD IDs")
    except HTTPException as he:
        logger.error(f"Error occurred during custom subset creation: {he.status_code}: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Error occurred during custom subset creation: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")







#####################################################################################
# http://127.0.0.1:8000/count_rows            
@app.get("/count_rows")
async def count_rows():
    try:
        conn = await connect_to_database()
        query = """SELECT COUNT(DISTINCT NORAD_CAT_ID) 
                    AS unique_count
                    FROM gp;"""
        count_result = await conn.fetchval(query)
        await close_connection(conn)
        return {"Unique objects managed in database": count_result}
    except Exception as e:
        return {"error": str(e)}





#####################################################################################
# Search endpoint
from datetime import datetime

@app.get("/search")
async def search_object(norad_cat_id: int, start_date: Optional[str] = None, end_date: Optional[str] = None):
    try:
        # Connect to the database
        conn = await connect_to_database()
        
        # Construct the base SQL query
        query = """
            SELECT * 
            FROM gp 
            WHERE norad_cat_id = $1 
        """
        
        # If start_date and end_date are provided, add a condition to filter by creation_date within the specified timeframe
        if start_date and end_date:
            try:
                start_date = datetime.fromisoformat(start_date)
                end_date = datetime.fromisoformat(end_date)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Please use ISO format (YYYY-MM-DD)")

            query += "AND creation_date BETWEEN $2 AND $3 "
        
        # Add ORDER BY clause to sort by insertion_date in descending order
        query += "ORDER BY insertion_date DESC"
        
        # Execute the SQL query with appropriate parameters
        if start_date and end_date:
            result = await fetch_data(conn, query, norad_cat_id, start_date, end_date)
        else:
            result = await fetch_data(conn, query, norad_cat_id)
        
        # Close the database connection
        await close_connection(conn)

        # Check if any result is found
        if result:
            logger.info(f"Search successful for NORAD_CAT_ID: {norad_cat_id}")
            return result
        else:
            # If no result found, raise HTTPException with status code 404 (Not Found)
            raise HTTPException(status_code=404, detail="Object not found in database")
    except HTTPException as he:
        logger.error(f"Error occurred during search: {he.status_code}: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Error occurred during search: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


















#####################################################################################################
#####################################################################################################
######################## THIS IS NOT TESTED ########################################################

# from fastapi import FastAPI, HTTPException, Depends
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# security = HTTPBearer()

# # Middleware to check authentication token
# async def check_authentication(credentials: HTTPAuthorizationCredentials = Depends(security)):
#     # Assuming you have a function `verify_token` that verifies the token
#     # If the token is valid, return True; otherwise, raise HTTPException
#     if verify_token(credentials.credentials):
#         return True
#     else:
#         raise HTTPException(status_code=401, detail="Invalid or missing authentication token")

# app = FastAPI()

# # Apply the authentication middleware to the specific endpoints
# @app.post("/login")
# async def login(username: str, password: str):
#     # Your login implementation

# @app.post("/register")
# async def register(username: str, password: str, email: str):
#     # Your registration implementation

# @app.get("/display_table", dependencies=[Depends(check_authentication)])
# async def display_table():
#     # Your display table implementation

#####################################################################################################
#####################################################################################################



#####################################################################################################
####################### THIS IS NOT NEEDED YET ######################################################
# # Login endpoint


# @app.post("/login")
# async def login(username: str, password: str):
#     try:
#         # Connect to the database
#         conn = await asyncpg.connect(user=db_config['user'], password=db_config['password'],
#                                       database=db_config['dbname'], host=db_config['host'])
        
#         # Query the database to check if the username and password match
#         query = "SELECT * FROM users WHERE username = $1 AND password = $2"
#         result = await conn.fetchrow(query, username, password)
        
#         # Close the database connection
#         await conn.close()

#         # If user is found in the database, return success message
#         if result:
#             logger.info(f"Login successful for user: {username}")
#             return {"message": "Login successful"}
#         else:
#             # If user is not found, raise HTTPException with status code 401 (Unauthorized)
#             raise HTTPException(status_code=401, detail="Invalid username or password")
#     except Exception as e:
#         # Handle any exceptions that occur during database connection or query execution
#         logger.error(f"Error occurred during login: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")


#####################################################################################################
#####################################################################################################




#####################################################################################################
####################### THIS IS NOT NEEDED YET ######################################################
# # User registration endpoint


# @app.post("/register")
# async def register(username: str, password: str, email: str):
#     try:
#         # Connect to the database
#         conn = await connect_to_database()
        
#         # Hash the password securely
#         hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
#         # Insert the new user into the database
#         query = "INSERT INTO users (username, password, email) VALUES ($1, $2, $3)"
#         await execute_query(conn, query, username, hashed_password, email)
        
#         # Close the database connection
#         await close_connection(conn)
        
#         logger.info(f"User registered successfully: {username}")
#         return {"message": "User registered successfully"}
#     except asyncpg.exceptions.UniqueViolationError:
#         logger.warning(f"Username or email already exists: {username}, {email}")
#         raise HTTPException(status_code=400, detail="Username or email already exists")
#     except Exception as e:
#         logger.error(f"Error occurred during user registration: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")

#####################################################################################################
#####################################################################################################





######################################################################################################
###########################BELOW THIS LINE IS THE NEW CODE############################################
## THESE HAVE NOT BEEN TESTED YET


# from fastapi import FastAPI, HTTPException
# from database_operations import connect_to_database, execute_query

# app = FastAPI()

# # Function to check for conditions and trigger alerts
# async def check_alerts():
#     try:
#         conn = await connect_to_database()
        
#         # Query to check for conditions (example: changes in object altitude)
#         query = "SELECT altitude FROM objects ORDER BY timestamp_column DESC LIMIT 2"
#         results = await execute_query(conn, query)
#         if len(results) == 2:
#             current_altitude, previous_altitude = results[0], results[1]
#             if current_altitude != previous_altitude:
#                 # Trigger alert based on altitude change
#                 # You can customize this part based on your specific alerting logic
#                 # For demonstration purposes, we're raising an HTTPException with a message
#                 raise HTTPException(status_code=200, detail="Alert: Change in object altitude detected")
        
#         await conn.close()
#     except Exception as e:
#         # Handle any exceptions gracefully
#         print(f"Error checking alerts: {e}")

# # Endpoint to trigger alerts
# @app.get("/trigger_alerts")
# async def trigger_alerts():
#     await check_alerts()
#     return {"message": "Alerts triggered successfully"}





# import time

# @app.get("/metrics")
# async def get_metrics():
#     try:
#         conn = await connect_to_database()
        
#         # Query to get data quantity
#         data_quantity_query = "SELECT COUNT(*) FROM your_table"
#         data_quantity = await execute_query(conn, data_quantity_query)
        
#         # Query to get update rates (assuming you have a timestamp column)
#         current_time = int(time.time())
#         one_hour_ago = current_time - 3600  # One hour ago
#         update_rate_query = f"SELECT COUNT(*) FROM your_table WHERE timestamp_column >= {one_hour_ago}"
#         update_rate = await execute_query(conn, update_rate_query)
        
#         # Calculate latency between fetch and loading into the database (assuming you have relevant timestamps)
#         latency_query = "SELECT fetch_timestamp, load_timestamp FROM your_table WHERE fetch_timestamp IS NOT NULL AND load_timestamp IS NOT NULL"
#         latency_results = await execute_query(conn, latency_query)
#         latencies = [(load_ts - fetch_ts) for fetch_ts, load_ts in latency_results if fetch_ts and load_ts]
#         avg_latency = sum(latencies) / len(latencies) if latencies else 0
        
#         await conn.close()
        
#         return {
#             "data_quantity": data_quantity[0],
#             "update_rate": update_rate[0],
#             "avg_latency": avg_latency
#         }
#     except Exception as e:
#         return {"error": str(e)}

##############################################################################################################################
##############################################################################################################################










