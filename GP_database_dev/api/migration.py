




# detta är alltså vad som ska köras för att kopiera data från en tabell till en annan
#gp_file  >  gp_file_historical.
# detta gör efter att gp_file har populerats och kommer sanorlikt bara köras en gång. 

# Tanken är (logiken) att innan gp_file uppdareas så ska gp_file_historical uppdateras med datan baserat på ett kondition. 
# dagens datum. för att bara hämta datan som den själv inte har. 

# säg att båda tabellerna har updateras med samma query när de först skapas. 
# Då vill jag ju inte att gp_file_historical ska uppdateras med all data från gp_file igen eftersom all data inte updateras i gp_file när det ska köras automatiskt. 











# import psycopg2
# from psycopg2 import Error

# Function to fetch data from source table and insert into target table
# def copy_data(source_table, target_table):
#     try:
#         Connect to your PostgreSQL database
#         connection = psycopg2.connect(
#             host = "localhost",
#             dbname = "postgres",
#             user = "postgres",
#             password = "172121D",
#             port = "5432"
#         )
        
#         cursor = connection.cursor()

#         Fetch data from source table
#         cursor.execute(f"SELECT * FROM {source_table}")
#         rows = cursor.fetchall()

#         Insert fetched data into target table
#         for row in rows:
#             cursor.execute(f"INSERT INTO {target_table} VALUES (%s, %s, %s)", row)

#         Commit changes
#         connection.commit()
#         print("Data copied successfully!")

#     except (Exception, Error) as error:
#         print("Error:", error)
    
#     finally:
#         if connection:
#             cursor.close()
#             connection.close()
#             print("PostgreSQL connection is closed")

# Example usage
# if __name__ == "__main__":
#     source_table = "gp_file"
#     target_table = "gp_file_historical"
#     copy_data(source_table, target_table)




import psycopg2
from psycopg2 import Error
from datetime import datetime

# Function to fetch data from source table based on a condition and insert into target table
def copy_data_with_condition(source_table, target_table):
    try:
        # Connect to your PostgreSQL database
        connection = psycopg2.connect(
            host = "localhost",
            dbname = "gpdata2",
            user = "postgres",
            password = "172121D",
            port = "5432"
        )
        
        cursor = connection.cursor()

        # Get today's date
        today_date = datetime.now().date()

        # Fetch data from source table based on condition (e.g., date column matching today's date)
        cursor.execute(f"SELECT * FROM {source_table} WHERE date_column = %s", (today_date,))
        rows = cursor.fetchall()

        # Insert fetched data into target table
        for row in rows:
            cursor.execute(f"INSERT INTO {target_table} VALUES (%s, %s, %s)", row)

        # Commit changes
        connection.commit()
        print("Data copied successfully!")

    except (Exception, Error) as error:
        print("Error:", error)
    
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

# Example usage
if __name__ == "__main__":
    source_table = "gp_file"
    target_table = "gp_file_historical"
    copy_data_with_condition(source_table, target_table)
