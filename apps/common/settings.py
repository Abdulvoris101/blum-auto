from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    BOT_TOKEN: str
    PASSWORD: str

    ERROR_CHANNEL_ID: int = -1002216942894
    EVENT_CHANNEL_ID: int = -1002216942894
    WEB_URL: str
    DB_URL: str
    DB_ALEMBIC_URL: str
    ENV_DIR: str
    REDIS_URL: str
    POSTGRES_DB_USER: str
    POSTGRES_DB_PASSWORD: str
    REDIS_HOST: str
    POSTGRES_TIMEZONE: str = "Asia/Tashkent"
    BOT_USERNAME: str

    ADMIN_ID: int
    REQUIRED_CHANNEL_ID: int
    WORKDIR: str = "sessions/"
    API_ID: int = 27079535
    API_HASH: str = "73f9a52dddb9472709de963aa68aa0ed"

    REFERRAL_PRICE: float = 0.5
    PRICE: float = 1.99
    STARS_PRICE: int = 100
    ALLOWED_FREE_GAMES: int = 5
    CLIENT_ID: str
    CLIENT_SECRET: str
    APP_ID: str


    PROXY_KEY: str
    PROXY_BASE_URL: str = "https://proxy6.net/api"

    class Config:
        env_file = os.environ.get("ENV_DIR")
        env_file_encoding = 'utf-8'


settings = Settings()
