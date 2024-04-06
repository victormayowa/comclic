"""
defines configuration classes
"""

from datetime import timedelta
from secrets import token_hex
from pydantic import BaseSettings


class Settings(BaseSettings):
    """common config vars"""

    authjwt_secret_key: str = token_hex(32)
    authjwt_token_location: set[str] = {"cookies"}
    authjwt_access_token_expires: timedelta = timedelta(days=1)
    authjwt_access_cookie_key = "_comclic_auth"
    authjwt_cookie_max_age = 24 * 60 * 60
    authjwt_cookie_samesite = "strict"

    class Config:
        """config class"""

        env_file = ".env"
        env_file_encoding = "utf-8"


class DBSettings(BaseSettings):
    """db config vars"""

    DB_NAME: str = "comclic"
    DB_PORT: int = 27017
    DB_HOST: str = "localhost"
    DB_USER: str = None
    DB_PASSWD: str = None

    class Config:
        """summary_line
        Keyword arguments:
        argument -- description
        Return: return_description
        """
        env_file = ".env"
        env_file_encoding = "utf-8"


class RedisSettings(BaseSettings):
    """summary_line
    Keyword arguments:
    argument -- description
    Return: return_description
    
    redis cache config vars"""

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWD: str = None
    REDIS_TTL: int = 60 * 60 * 12

    class Config:
        """config class"""

        env_file = ".env"
        env_file_encoding = "utf-8"
