import mysql.connector
from pydantic_settings import BaseSettings
import logging

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_USER: str = "root"
    DB_PASSWORD: str = "Khi@2025"
    DB_NAME: str = "oraaqdb"

    # class Config:
    #     env_file = ".env"  # Load variables from .env file if it exists

settings = Settings()

def validate_connection():
    print("Attempting to validate MySQL connection...")  # Debugging print
    try:
        logger.debug(f"Connecting to MySQL database with user {settings.DB_USER} at {settings.DB_HOST}")
        
        # Try to connect directly with mysql-connector-python
        conn = mysql.connector.connect(
            host=settings.DB_HOST,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            # database=settings.DB_NAME,
            connection_timeout=10  # Timeout after 10 seconds
        )
        
        if conn.is_connected():
            print("Database connection successful!")
            logger.debug("Successfully connected to the database.")
        else:
            print("Database connection failed!")
            logger.debug("Failed to connect to the database.")
        
        conn.close()  # Always close the connection after use
    except mysql.connector.Error as e:
        print(f"Error: {e}")
        logger.error(f"Error during connection attempt: {e}")

if __name__ == "__main__":
    print("Starting MySQL connection validation...")
    validate_connection()
