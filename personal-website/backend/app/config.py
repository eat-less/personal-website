from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    APP_NAME: str = "Personal Website"
    DEBUG: bool = True
    DB_TYPE: str = "sqlite"
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "root"
    DB_NAME: str = "personal_website"

    @property
    def DATABASE_URL(self) -> str:
        if self.DB_TYPE == "sqlite" or os.environ.get("DB_TYPE") == "sqlite":
            return "sqlite:///./personal_website.db"
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

settings = Settings()