from fastapi import FastAPI, HTTPException
import asyncpg
from database_operations import close_connection, connect_to_database, load_config, fetch_data, execute_query
import bcrypt
import logging











app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Load database connection details from config.ini
db_config = load_config()

table_name = "gp"









# Function to configure logger
def configure_logger():
    # Create a logger
    logger = logging.getLogger("orbital_data_logger")
    # Set logging level to DEBUG
    logger.setLevel(logging.DEBUG)
    # Define a file handler and set formatter
    file_handler = logging.FileHandler("application.log")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    # Add the file handler to the logger
    logger.addHandler(file_handler)
    return logger

# Get logger
logger = configure_logger()





# Login endpoint
@app.post("/login")
async def login(username: str, password: str):
    try:
        # Connect to the database
        conn = await asyncpg.connect(user=db_config['user'], password=db_config['password'],
                                      database=db_config['dbname'], host=db_config['host'])
        
        # Query the database to check if the username and password match
        query = "SELECT * FROM users WHERE username = $1 AND password = $2"
        result = await conn.fetchrow(query, username, password)
        
        # Close the database connection
        await conn.close()

        # If user is found in the database, return success message
        if result:
            logger.info(f"Login successful for user: {username}")
            return {"message": "Login successful"}
        else:
            # If user is not found, raise HTTPException with status code 401 (Unauthorized)
            raise HTTPException(status_code=401, detail="Invalid username or password")
    except Exception as e:
        # Handle any exceptions that occur during database connection or query execution
        logger.error(f"Error occurred during login: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")






# User registration endpoint
@app.post("/register")
async def register(username: str, password: str, email: str):
    try:
        # Connect to the database
        conn = await connect_to_database()
        
        # Hash the password securely
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Insert the new user into the database
        query = "INSERT INTO users (username, password, email) VALUES ($1, $2, $3)"
        await execute_query(conn, query, username, hashed_password, email)
        
        # Close the database connection
        await close_connection(conn)
        
        logger.info(f"User registered successfully: {username}")
        return {"message": "User registered successfully"}
    except asyncpg.exceptions.UniqueViolationError:
        logger.warning(f"Username or email already exists: {username}, {email}")
        raise HTTPException(status_code=400, detail="Username or email already exists")
    except Exception as e:
        logger.error(f"Error occurred during user registration: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")



                            # SELECT * FROM gp 
                            # ORDER BY CREATION_DATE DESC 
                            # LIMIT 10;


# Display table endpoint
@app.get("/display_table")
async def display_table():
    try:
        conn = await connect_to_database()
        data = await fetch_data(conn, """SELECT DISTINCT NORAD_CAT_ID, CREATION_DATE, OBJECT_NAME, tle_line1, tle_line2
                                            FROM gp 
                                            ORDER by CREATION_DATE desc , NORAD_CAT_ID  
                                            LIMIT 10; """)
        await close_connection(conn)
        return {"table_data": data}
    except Exception as e:
        logger.error(f"Error occurred during display_table: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")






# Search endpoint
@app.get("/search")
async def search_object(norad_cat_id: int):
    try:
        # Connect to the database
        conn = await connect_to_database()
        
        # Execute SQL query to search for the object
        query = "SELECT * FROM gp WHERE norad_cat_id = $1"
        result = await fetch_data(conn, query, norad_cat_id)
        
        # Close the database connection
        await conn.close()

        # Check if any result is found
        if result:
            logger.info(f"Search successful for NORAD_CAT_ID: {norad_cat_id}")
            return result
        else:
            # If no result found, raise HTTPException with status code 404 (Not Found)
            raise HTTPException(status_code=404, detail="Object not found")
    except Exception as e:
        # Handle any exceptions that occur during database interaction
        logger.error(f"Error occurred during search: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
