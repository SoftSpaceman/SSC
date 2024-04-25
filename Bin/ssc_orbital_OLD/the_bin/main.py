



from fastapi import FastAPI
from database import fetch_data_from_table
from auth import authenticate_user
from functions import perform_some_task

app = FastAPI()

TABLE_NAME = "gp"


@app.get("/display_table")
async def display_table():
    data = await fetch_data_from_table(TABLE_NAME) # "gp"
    return {"table_data": data}  # Return the data fetched from the table 
# denna funkar men ger hela datan helt naken... gör det trögt och jävligt. 




# Example usage of authentication function
@app.post("/login")
async def login(username: str, password: str):
    if await authenticate_user(username, password):
        return {"message": "Login successful"}
    else:
        return {"message": "Login failed"}
    




# Example endpoint using other functionality
@app.get("/perform_task")
async def perform_task():
    result = await perform_some_task()
    return {"message": result}
