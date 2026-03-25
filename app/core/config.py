from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "Shell Oil & Gas Production Forecast API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    AZURE_STORAGE_CONN_STR: str = ""
    DEFAULT_FORECAST_MONTHS: int = 24

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
