# db_utils.py

import mysql.connector

def open_connection():
    # Open a connection to the MySQL database.
    
    try:
        cnx = mysql.connector.connect(
            host="127.0.0.1",
            port="3306",
            user="root",
            password="root",
            database="healdb"
        )
        cursor = cnx.cursor(buffered=True)
        return cnx, cursor
    except mysql.connector.Error as e:
        print(f"Error connecting to the database: {e}")
        raise

def close_connection(cnx, cursor):
    # Close the connection to the MySQL database.
    
    if cursor:
        cursor.close()
    if cnx:
        cnx.close()
