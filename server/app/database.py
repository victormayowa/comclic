"""
Defines the storage engine.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.models import (
    User,
    Patient,
    Immunization,
    Finance
)

from app.settings import settings


# def get_mongo_uri() -> str:
#     """returns the mongo uri"""
#     if settings.DB_USER and settings.DB_PASSWD:
#         return (
#             f"mongodb://{settings.DB_USER}:{settings.DB_PASSWD}"
#             f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
#         )

#     return f"{settings.DATABASE_URL}"  # mongodb://{settings.DB_HOST}:{settings.DB_PORT}/" f"{settings.DB_NAME}"

async def init_db(uri: str) -> None:
    """
    initializes the db

    :param uri: the db uri
    """

    client = AsyncIOMotorClient(uri)
    #print(client.address)
    await init_beanie(
        database=client[settings.DB_NAME],
        document_models=[
            User,
            Patient,
            Immunization,
            Finance,
        ]
    )