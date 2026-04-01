from contextlib import asynccontextmanager
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://db:27017"
    mongodb_db: str = "atendimentos_db"
    collection_name: str = "atendimentos"

    model_config = ConfigDict(env_file=".env", extra="ignore")


settings = Settings()
_client: AsyncIOMotorClient | None = None


def get_db() -> AsyncIOMotorDatabase[Any]:
    if _client is None:
        raise RuntimeError("Cliente MongoDB nao inicializado")
    return _client[settings.mongodb_db]


@asynccontextmanager
async def lifespan(app):
    global _client
    _client = AsyncIOMotorClient(settings.mongodb_uri)
    yield
    if _client is not None:
        _client.close()
        _client = None
