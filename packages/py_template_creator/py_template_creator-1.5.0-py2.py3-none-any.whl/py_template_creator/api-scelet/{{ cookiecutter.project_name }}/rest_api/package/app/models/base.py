import contextlib
import logging
import os
import enum
import uuid
from typing import Any, AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import inspect, Identity, BigInteger
from sqlalchemy.orm import (
    DeclarativeBase,
    MappedAsDataclass,
    Mapped,
    mapped_column,
)


class Base(MappedAsDataclass, DeclarativeBase):
    id: Mapped[int] = mapped_column(
        BigInteger, Identity(always=True), init=False, primary_key=True
    )
    """subclasses will be converted to dataclasses"""

    def to_dict(self, recurse: bool = True, force_exclude: list = []) -> dict:
        """Convert an SQLAlchemy model instance to a dictionary."""
        if not hasattr(self, "__dict__"):
            return {}
        # Convert object attributes to dictionary
        result = {}
        for key, value in self.__dict__.items():
            if key != "_sa_instance_state" and key not in force_exclude:
                if isinstance(value, enum.Enum):
                    result[key] = value.value
                elif isinstance(value, uuid.UUID):
                    result[key] = str(value)
                else:
                    result[key] = value
        # Get relationships from the SQLAlchemy inspection system
        mapper = inspect(type(self))
        for relationship in mapper.relationships:
            if relationship.key not in result:
                continue
            value = getattr(self, relationship.key)

            if value is None:
                result[relationship.key] = None
            elif isinstance(value, list):
                if recurse:
                    result[relationship.key] = [
                        item.to_dict(recurse=recurse) for item in value
                    ]
                else:
                    result[relationship.key] = [item.id for item in value]
            else:
                if recurse:
                    result[relationship.key] = value.to_dict(recurse=recurse)
                else:
                    result[relationship.key] = value.id

        return result


logger = logging.getLogger(__name__)

DB_URL = "postgresql+psycopg://{}:{}@{}:{}/{}".format(
    os.getenv("POSTGRES_USER"),
    os.getenv("POSTGRES_PASSWORD"),
    os.getenv("POSTGRES_HOST"),
    os.getenv("POSTGRES_PORT"),
    os.getenv("POSTGRES_DB"),
)
logger.info(f"Connecting with conn string {DB_URL}")


class DatabaseSessionManager:
    def __init__(self, host: str, engine_kwargs: dict[str, Any] = {}):
        self._engine = create_async_engine(host, **engine_kwargs)
        self._sessionmaker = async_sessionmaker(
            autocommit=False, expire_on_commit=False, bind=self._engine
        )

    async def close(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(DB_URL)


async def get_db_session():
    async with sessionmanager.session() as session:
        yield session
