"""Global app settings"""

from datetime import timedelta

from decouple import config
from pydantic_settings import BaseSettings
from pydantic.types import Enum
from redis import Redis


class Mode(Enum):
    """app mode enum"""

    DEV = "dev"
    PROD = "prod"
    TEST = "test"


class Settings(BaseSettings):
    """common config vars"""

    MODE: str = config("MODE", default=Mode.DEV.value)
    SECRET_KEY: str = config("SECRET_KEY")
    HOST: str = config("APP_HOST", default="localhost")
    PORT: int = config("APP_PORT", default=8000, cast=int)
    ACCESS_TOKEN_DELTA: timedelta = timedelta(days=1)
    ACCESS_COOKIE_KEY: str = config("ACCESS_COOKIE_KEY", default="access_token_cookie")
    COOKIE_MAX_AGE: int = config("COOKIE_EXPIRE", default=24 * 60 * 60, cast=int)
    COOKIE_SAMESITE: str = "strict"
    DATABASE_URL: str = config("DATABASE_URL", default="mongodb://localhost:27017")
    DB_PORT: int = config("DB_PORT", default=27017, cast=int)
    DB_NAME: str = config("DB_NAME", default="comclic")
    DB_HOST: str = config("DB_HOST", default="localhost")
    DB_USER: str | None = config("DB_USER", default=None)
    DB_PASSWD: str | None = config("DB_PORT", default=None)
    REDIS_URL: str = config("REDIS_URL", default="redis://0.0.0.0:6379")
    REDIS_TTL: int = config("REDIS_TTL", default=60 * 60 * 24, cast=int)
    # REDIS_HOST: str = config("REDIS_HOST", default="localhost")
    # REDIS_PORT: int = config("REDIS_PORT", default=6379, cast=int)
    # REDIS_PASSWD: str | None = config("REDIS_PASSWD", default=None)


settings = Settings()
