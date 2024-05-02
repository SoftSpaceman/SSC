from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database_operations import connect_to_database, execute_query, fetch_data

app = FastAPI()

# Define a model for the data you expect to receive
class ObjectData(BaseModel):
    object_id: str
    altitude: float
    # Add other fields as needed

# Endpoint to receive object data and store it in the database
@app.post("/object-data/")
async def receive_object_data(data: ObjectData):
    conn = await connect_to_database()
    query = "INSERT INTO object_data (object_id, altitude) VALUES ($1, $2)"
    await execute_query(conn, query, data.object_id, data.altitude)
    # Implement logic to check conditions and trigger alerts
    if data.altitude < 1000:  # Example condition, replace with your logic
        # Trigger alert
        send_alert(data.object_id, "Altitude below 1000 meters!")
    return {"message": "Data received successfully"}

# Function to send alerts
def send_alert(object_id: str, message: str):
    # Implement your alerting mechanism here (e.g., email, SMS, etc.)
    print(f"Alert for object {object_id}: {message}")

# Example endpoint to retrieve object data
@app.get("/object-data/{object_id}")
async def get_object_data(object_id: str):
    conn = await connect_to_database()
    query = "SELECT * FROM object_data WHERE object_id = $1"
    rows = await fetch_data(conn, query, object_id)
    if not rows:
        raise HTTPException(status_code=404, detail="Object data not found")
    row = rows[0]  # Assuming object_id is unique
    return {"object_id": row["object_id"], "altitude": row["altitude"]}
