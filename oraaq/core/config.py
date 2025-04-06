from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_USER: str = "root"
    DB_PASSWORD: str = "Khi@2025"
    DB_NAME: str = "oraaqdb"

    # class Config:
    #     env_file = ".env"  # Load variables from .env file if exists

settings = Settings()
