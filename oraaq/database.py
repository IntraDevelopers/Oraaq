import mysql.connector
from core.config import settings

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="sajjad",
        database="oraaqdb"
    )