"""App settings & environment variables"""

from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os


# import appropriate modules
env = os.getenv("ENV", "development")

# Load .env file only if not in production
if env != "production":
    load_dotenv(f".env.{env}")


class BaseSettingsConfig(BaseSettings):
    """
    Base Settings Configuration for the application.
    This class is used to define environment variables and application settings.
    It uses Pydantic's BaseSettings to load environment variables.
    """

    ENV: str
    DATABASE_URL: str

    class Config:
        case_sensitive = True


class DevelopmentSettings(BaseSettingsConfig):
    """
    Development Settings Configuration.
    This class inherits from BaseSettingsConfig and is used for development
      environment settings.
    """

    DEBUG: bool = True


class ProductionSettings(BaseSettingsConfig):
    """
    Production Settings Configuration.
    This class inherits from BaseSettingsConfig and is used for production
      environment settings.
    """

    DEBUG: bool = False


class TestingSettings(BaseSettingsConfig):
    """
    Testing Settings Configuration.
    This class inherits from BaseSettingsConfig and is used for testing
      environment settings.
    """

    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./test.db"  # Example for testing
