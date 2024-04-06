#!/usr/bin/env python3

"""
Defines the storage engine.
"""
from typing import TypeVar

# from redis import Redis, ConnectionPool
# from redis.retry import Retry
# from redis.backoff import ExponentialBackoff
from decouple import config
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.models import (User)

from app.settings import settings


T = TypeVar("T", User)


def get_mongo_uri() -> str:
    """returns the mongo uri"""
    if settings.DB_USER and settings.DB_PASSWD:
        return (
            f"mongodb://{settings.DB_USER}:{settings.DB_PASSWD}"
            f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        )

    return f"mongodb://{settings.DB_HOST}:{settings.DB_PORT}/" f"{settings.DB_NAME}"


# def get_rabbitmq_uri() -> str:
#     """returns the rabbitmq uri"""
#     if settings.RABBITMQ_USER and settings.RABBITMQ_PASSWD:
#         return (
#             f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWD}"
#             f"@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}/"
#         )

#     return f"amqp://guest:guest@{settings.RABBITMQ_HOST}" f":{settings.RABBITMQ_PORT}/"


async def init_db(uri: str) -> None:
    """
    initializes the db

    :param uri: the db uri
    """

    client = AsyncIOMotorClient(uri)

    await init_beanie(
        database=client[settings.DB_NAME],
        document_models=[User],
    )


# class Cache:
#     """
#     a redis cache for storing session keys
#     """

#     HOST = settings.REDIS_HOST
#     PORT = settings.REDIS_PORT
#     PASSWD = settings.REDIS_PASSWD
#     RETRY_POLICY = Retry(
#         ExponentialBackoff(),
#         retries=5,
#     )

#     def __init__(self, db: int, ttl: int) -> None:
#         """initializes the redis client"""

#         conn = ConnectionPool(
#             host=self.HOST,
#             port=self.PORT,
#             db=db,
#             password=self.PASSWD,
#             decode_responses=True,
#             retry=self.RETRY_POLICY,
#         )
#         self.redis = Redis(connection_pool=conn)
#         self.TTL = ttl

#     def ping(self) -> bool:
#         """checks if the cache is available"""
#         return self.redis.ping()

#     def get(self, key: str) -> str | None:
#         """fetches a value from the cache"""
#         if key is None:
#             return None

#         return self.redis.get(key)

#     def setv(self, key: str, value: str) -> None:
#         """
#         sets a value in the cache with a ttl
#         """
#         if key is None or value is None:
#             return None

#         self.redis.set(key, value)

#     def setex(self, key: str, value: str) -> None:
#         """
#         sets a value in the cache with a ttl
#         """
#         if key is None or value is None:
#             return None

#         self.redis.setex(key, self.TTL, value)

#     def delete(self, key: str) -> None:
#         """deletes a value from the cache"""
#         if key is None:
#             return None

#         self.redis.delete(key)

# SESSION_CACHE = Cache(
#     ttl=settings.REDIS_TTL,
#     db=settings.REDIS_SESSION_DB,
# )
# SOCKETIO_CACHE = Cache(
#     ttl=settings.REDIS_TTL,
#     db=settings.REDIS_SOCKETIO_DB,
# )
# if not SESSION_CACHE.ping() or not SOCKETIO_CACHE.ping():
#     raise ConnectionError("redis cache is not available")
