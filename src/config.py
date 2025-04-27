from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    DEBUG: bool
    DATABASE_PROD_URL: str
    DATABASE_DEV_URL: str
    AUTH_SECRET_KEY: str


settings = Settings()  # type: ignore
