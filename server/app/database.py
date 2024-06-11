"""
Defines the storage engine.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.models import User, Patient, Immunization, Finance

from app.settings import settings
from redis import Redis, asyncio as aioredis
from redis.retry import Retry
from redis.backoff import ExponentialBackoff


async def init_db(uri: str) -> None:
    """
    initializes the db

    :param uri: the db uri
    """

    client = AsyncIOMotorClient(uri)
    await init_beanie(
        database=client[settings.DB_NAME],
        document_models=[
            User,
            Patient,
            Immunization,
            Finance,
        ],
    )


def init_redis() -> Redis:
    RETRY = Retry(ExponentialBackoff(), retries=5)
    client = aioredis.from_url(
        settings.REDIS_URL, encoding="utf-8", decode_responses=True, retry=RETRY
    )

    return client


CACHE = init_redis()
