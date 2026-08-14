# db_utils.py

import mysql.connector
from sqlalchemy import create_engine

def open_connection():
    # Open a connection to the MySQL database.
    
    try:
        cnx = mysql.connector.connect(
            host="xxx.x.x.x",
            port="xxxx",
            user="root",
            password="root",
            database="healdb"
        )
        cursor = cnx.cursor(buffered=True)
        return cnx, cursor
    except mysql.connector.Error as e:
        print(f"Error connecting to the database: {e}")
        raise
    return

def close_connection(cnx, cursor):
    # Close the connection to the MySQL database.
    
    if cursor:
        cursor.close()
    if cnx:
        cnx.close()
    return

def open_connection_alchemy():
    # Open a connection to the MySQL database using the library sqlalchemy
   
    try:
        host="xxx.x.x.x"
        port="xxxx"   
        user="root"
        password="root"
        database="healdb"
        
        connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
        engine = create_engine(connection_string)
        return engine
    except Exception as e:
        print(f"Erro ao conectar via SQLAlchemy: {e}")
        raise

def close_connection_alchemy(engine):
    # Close the engine to SQLAlchemy, releasing the connection pool
    if engine:
        engine.dispose()
    return
