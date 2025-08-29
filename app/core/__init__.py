## This file is part of the application core module.

from .settings import DevelopmentSettings, ProductionSettings, TestingSettings
from os import getenv


def get_settings():
    """
    Get the application settings based on the environment.
    Returns:
        BaseSettingsConfig: The settings configuration for the current environment.
    """
    env = getenv("ENV", "development").lower()
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    return DevelopmentSettings()


settings = get_settings()
