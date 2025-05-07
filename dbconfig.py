import mysql.connector
from mysql.connector import Error

db = None

try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",  # Default user for XAMPP MySQL
        password="",  # Empty for XAMPP
        database="flight_management"  # Database name
    )

    if db.is_connected():
        print("Successfully connected to the database!")

except Error as err:
    print(f"Error: {err}")
    db = None
