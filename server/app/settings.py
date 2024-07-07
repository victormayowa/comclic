# from secrets import token_hex
from datetime import timedelta

from decouple import config
from pydantic_settings import BaseSettings
from pydantic.types import Enum


class Mode(Enum):
    """app mode enum"""

    DEV = "dev"
    PROD = "prod"
    TEST = "test"


class Settings(BaseSettings):
    """common config vars"""

    MODE: str = config("MODE", default=Mode.DEV.value)
    SECRET_KEY: str = config("SECRET_KEY")
    APP_HOST: str = config("APP_HOST", default="localhost")
    APP_PORT: int = config("APP_PORT", default=8000, cast=int)
    ACCESS_TOKEN_DELTA: timedelta = timedelta(days=1)
    ACCESS_COOKIE_KEY: str = config("ACCESS_COOKIE_KEY", default="access_token_cookie")
    COOKIE_MAX_AGE: int = config("COOKIE_EXPIRE", default=24 * 60 * 60, cast=int)
    COOKIE_SAMESITE: str = "strict"

    # database configuration
    DATABASE_URL: str = config("DATABASE_URL", default="mongodb://localhost:27017")
    DB_PORT: int = config("DB_PORT", default=27017, cast=int)
    DB_NAME: str = config("DB_NAME", default="comclic")
    DB_HOST: str = config("DB_HOST", default="localhost")
    DB_USER: str | None = config("DB_USER", default=None)
    DB_PASSWD: str | None = config("DB_PORT", default=None)

    # email configuration
    SMTP_HOST: str = config("SMTP_HOST", default="localhost")
    SMTP_PORT: int = config("SMTP_PORT", default=587, cast=int)
    SMTP_USERNAME: str = config("SMTP_USERNAME")
    SMTP_PASSWORD: str = config("SMTP_PASSWORD")
    FROM_EMAIL: str = config("FROM_EMAIL")
    SMTP_USE_TLS: bool | None = config("SMTP_USE_TLS", default=None, cast=bool)
    SMTP_USE_SSL: bool | None= config("SMTP_USE_SSL", default=None, cast=bool)

# redis configuration
# REDIS_HOST: str = config("REDIS_HOST", default="localhost")
# REDIS_PORT: int = config("REDIS_PORT", default=6379, cast=int)
# REDIS_SOCKETIO_DB: int = config("REDIS_SOCKETIO_DB", default=1, cast=int)
# REDIS_SESSION_DB: int = config("REDIS_SESSION_DB", default=0, cast=int)
# REDIS_PASSWD: str | None = config("REDIS_PASSWD", default=None)
# REDIS_TTL: int = config("REDIS_TTL", default=60 * 60 * 24, cast=int)
# RABBITMQ_HOST: str = config("RABBITMQ_HOST", default="localhost")
# RABBITMQ_PORT: int = config("RABBITMQ_PORT", default=5672, cast=int)
# RABBITMQ_USER: str | None = config("RABBITMQ_USER", default=None)
# RABBITMQ_PASSWD: str | None = config("RABBITMQ_PASSWD", default=None)


settings = Settings()
