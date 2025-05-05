from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    DEBUG: bool
    DATABASE_PROD_URL: str
    DATABASE_DEV_URL: str
    AUTH_SECRET_KEY: str
    
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    
    CELERY_BROKER_URL: str


settings = Settings()  # type: ignore
