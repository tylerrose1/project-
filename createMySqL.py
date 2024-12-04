#hiike_db : admin username / password: Data123!!

import mysql.connector
from mysql.connector import Error

# Database configuration
db_config = {
    'host': 'filmquiz.cv0mcauishmo.us-east-2.rds.amazonaws.com',
    'user': 'admin',
    'password': 'Data123!!',
    'database': 'filmquiz'
}

try:
    # Establish a connection
    conn = mysql.connector.connect(**db_config)
    if conn.is_connected():
        print("Successfully connected to the database!")

    # Your database operations here
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES;")
    for table in cursor.fetchall():
        print(table)

except Error as e:
    print(f"Error while connecting to MySQL: {e}")

finally:
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()
        print("Database connection closed.")
