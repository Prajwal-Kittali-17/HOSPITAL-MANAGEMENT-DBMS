# db_config.py
import mysql.connector
from mysql.connector import Error

def get_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="@Prajwal2728",   # your MySQL password
            database="hospital_management",   # database name
            auth_plugin="mysql_native_password"
        )
        return conn
    except Error as e:
        raise
