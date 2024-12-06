#hiike_db : admin username / password: Data123!!
import mysql.connector

# Establish connection to MySQL
db_connection = mysql.connector.connect(
    host="localhost",  # Replace with your MySQL server host
    user="your_username",  # Your MySQL username
    password="your_password",  # Your MySQL password
    database="my_database"  # The database you created
)

# Create a cursor object
cursor = db_connection.cursor()

# Example data to insert
name = "John Doe"
age = 30
email = "john.doe@example.com"

# SQL query to insert data
insert_query = "INSERT INTO my_table (name, age, email) VALUES (%s, %s, %s)"
values = (name, age, email)

# Execute the query
cursor.execute(insert_query, values)

# Commit the transaction
db_connection.commit()

# Print success message
print(f"Data inserted with ID: {cursor.lastrowid}")

# Close the connection
cursor.close()
db_connection.close()
