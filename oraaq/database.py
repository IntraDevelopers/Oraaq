import mysql.connector
from core.config import settings
import pymysql
pymysql.install_as_MySQLdb()


# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host=settings.DB_HOST,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME
    )

DATABASE_URL = "mysql+pymysql://root:sajjad@localhost/oraaqdb"
