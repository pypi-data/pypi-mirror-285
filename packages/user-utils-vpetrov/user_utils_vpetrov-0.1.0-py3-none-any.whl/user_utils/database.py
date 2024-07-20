"""
Database configuration and session creation.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import get_settings

settings = get_settings()

if "sqlite" in settings.db_url:
    connect_args = {"check_same_thread": False}
else:
    connect_args = {}

engine = create_engine(
    settings.db_url,
    echo=settings.db_echo,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_recycle=settings.db_pool_recycle,
    pool_pre_ping=settings.db_pool_pre_ping,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


def get_db():
    """
    Returns a new session of the database.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
