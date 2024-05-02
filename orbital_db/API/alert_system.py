
from database_operations import connect_to_database, execute_query, fetch_data

from pydantic import BaseModel, Field, validator
from fastapi import HTTPException, APIRouter
from datetime import datetime, timedelta
from typing import List

router = APIRouter()


class ObjectData(BaseModel):
    NORAD_IDs: List[int]
    CREATION_DATE: datetime

# # @router.post("/old_creation_date_alert/")
# # async def receive_object_data(data: ObjectData, days_threshold: int = 4):
# #     conn = await connect_to_database()
# #     outdated_ids = set()  # Using set to store unique NORAD_CAT_IDs
# #     outdated_count = 0
    
# #     Fetch latest creation date for each unique NORAD_CAT_ID
# #     query = "SELECT norad_cat_id, MAX(creation_date) AS latest_creation_date FROM gp GROUP BY norad_cat_id"
# #     rows = await fetch_data(conn, query)
    
# #     Iterate over fetched rows
# #     for row in rows:
# #         norad_cat_id = row["norad_cat_id"]
# #         latest_creation_date = row["latest_creation_date"]
        
# #         Check if the latest creation date is older than the threshold
# #         if datetime.now() - latest_creation_date > timedelta(days=days_threshold):
# #             outdated_ids.add(norad_cat_id)
# #             outdated_count += 1
# #             send_alert(str(norad_cat_id), f"Latest creation date is older than {days_threshold} days for NORAD_CAT_ID: {norad_cat_id}")
    
# #     Log or store the outdated NORAD_CAT_IDs for further tracking
# #     log_outdated_ids(outdated_ids)
    
# #     return {"message": "Data received successfully", "outdated_count": outdated_count}

# Function to log or store outdated NORAD_CAT_IDs
# def log_outdated_ids(outdated_ids: set):
#     # Implement your logging or storage mechanism here
#     print("Outdated NORAD_CAT_IDs:", outdated_ids)

# Function to send alerts
def send_alert(object_id: str, message: str):
    # Implement your alerting mechanism here (e.g., email, SMS, etc.)
    print(f"Alert for object {object_id}: {message}")






# # Example endpoint to retrieve object data
# @router.get("/object-data/{object_id}")
# async def get_object_data(object_id: str):
#     conn = await connect_to_database()
#     query = "SELECT * FROM object_data WHERE object_id = $1"
#     rows = await fetch_data(conn, query, object_id)
#     if not rows:
#         raise HTTPException(status_code=404, detail="Object data not found")
#     row = rows[0]  # Assuming object_id is unique
#     return {"object_id": row["object_id"], "altitude": row["altitude"], "creation_date": row["creation_date"]}
