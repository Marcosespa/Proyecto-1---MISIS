import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./test.db"
    jwt_secret_key: str = "super-secret-key"
    upload_folder: str = "./uploads"

    class Config:
        env_file = ".env"

settings = Settings()
