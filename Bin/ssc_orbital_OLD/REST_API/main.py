from fastapi import FastAPI
from database2 import close_connection, connect_to_database, fetch_data

app = FastAPI()

table_name = "gp"

@app.get("/display_table")
async def display_table():
    conn = await connect_to_database()
    data = await fetch_data(conn, "SELECT * FROM gp")
    await close_connection(conn)
    return {"table_data": data}
