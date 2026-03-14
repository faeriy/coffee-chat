from typing import Generator, TypeVar

from app.config import settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

T = TypeVar("T")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_and_refresh(db: Session, instance: T) -> T:
    """Add instance to the session, commit, refresh, and return it."""
    db.add(instance)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(instance)
    return instance
