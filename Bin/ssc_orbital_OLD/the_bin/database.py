import asyncpg




# Replace these with your database connection details
DATABASE_URL = "postgresql://postgres:172121D@localhost:5432/orbital_info_db"


async def connect_to_database():
    return await asyncpg.connect(DATABASE_URL)


async def fetch_data_from_table(table_name):
    conn = await connect_to_database()
    rows = await conn.fetch(f"SELECT * FROM {table_name}")
    await conn.close()
    return rows
