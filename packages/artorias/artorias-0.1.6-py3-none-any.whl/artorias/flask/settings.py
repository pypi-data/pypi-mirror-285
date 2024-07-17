from datetime import timedelta
from typing import Callable
from typing import Type

from flask.typing import ResponseReturnValue
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class DefaultSettings(EnvSettings):
    LOGGER_FORMAT_STRING: str = "%(asctime)s | %(levelname)7s | %(thread)s | %(module)30s : %(message)s"

    # Flask
    SECRET_KEY: str | None = None
    CUSTOM_ERROR_HANDLERS: dict[Type[Exception], Callable[[Exception], ResponseReturnValue]] = {}

    # DB
    SQLALCHEMY_ECHO: bool = False
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"

    # JWT
    JWT_ACCESS_TOKEN_EXPIRES: int | timedelta = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES: int | timedelta = timedelta(days=30)
