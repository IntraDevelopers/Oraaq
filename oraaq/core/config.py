from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_HOST: str = "127.0.0.1"
    DB_USER: str = "root"
    DB_PASSWORD: str = "kh@n1234"
    DB_NAME: str = "oraaqdb"

    class Config:
        env_file = ".env"  # Load variables from .env file if exists

settings = Settings()
