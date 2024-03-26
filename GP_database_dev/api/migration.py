import psycopg2
from psycopg2 import sql







# Database connection parameters
DB_HOST = "your_database_host"
DB_NAME = "your_database_name"
DB_USER = "your_database_user"
DB_PASSWORD = "your_database_password"













# Define the trigger function SQL
trigger_function_sql = """
CREATE OR REPLACE FUNCTION move_to_historical()
RETURNS TRIGGER AS $$
BEGIN
    -- Move updated rows to historical table
    INSERT INTO historical_data (data_column, created_at)
    VALUES (NEW.data_column, NEW.created_at);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

# Define the trigger SQL
trigger_sql = """
CREATE TRIGGER data_update_trigger
AFTER INSERT OR UPDATE ON new_data
FOR EACH ROW
EXECUTE FUNCTION move_to_historical();
"""












# Connect to the database
try:
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST
    )
    cursor = conn.cursor()

    # Create trigger function
    cursor.execute(trigger_function_sql)

    # Create trigger
    cursor.execute(trigger_sql)

    # Commit the transaction
    conn.commit()
    print("Trigger created successfully.")

except psycopg2.Error as e:
    print("Error:", e)

finally:
    if conn is not None:
        conn.close()
