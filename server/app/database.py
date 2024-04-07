"""
Defines the storage engine.
"""
from typing import TypeVar

from decouple import config
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.models import (
    User,
    Patient,
    Immunization,
    Finance,
    UserBase,
    UserRegister,
    UserLogin,
    UserOut,
)

from app.settings import settings


def get_mongo_uri() -> str:
    """returns the mongo uri"""
    if settings.DB_USER and settings.DB_PASSWD:
        return (
            f"mongodb://{settings.DB_USER}:{settings.DB_PASSWD}"
            f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        )

    return f"{DATABASE_URL}"  # mongodb://{settings.DB_HOST}:{settings.DB_PORT}/" f"{settings.DB_NAME}"

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


async def initialize_database():
    """Initialize the database."""
    uri = get_mongo_uri()
    await init_db(uri)


db = initialize_database()