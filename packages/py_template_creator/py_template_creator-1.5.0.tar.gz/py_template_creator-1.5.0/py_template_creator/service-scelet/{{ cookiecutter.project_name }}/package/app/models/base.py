import logging
import enum
import uuid

from package.app import settings
from sqlalchemy import create_engine, NullPool, inspect, Identity, BigInteger
from sqlalchemy.orm import (
    DeclarativeBase,
    sessionmaker,
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
    settings.POSTGRES_USER,
    settings.POSTGRES_PASSWORD,
    settings.POSTGRES_HOST,
    settings.POSTGRES_PORT,
    settings.POSTGRES_DB,
)
logger.info(f"Connecting with conn string {DB_URL}")


engine = create_engine(DB_URL, pool_pre_ping=True, poolclass=NullPool)
Session = sessionmaker(autocommit=False, autoflush=True, bind=engine)


def get_db_session():
    try:
        db = Session()
        yield db
    finally:
        db.close()
