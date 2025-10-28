from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from src.core.config import get_settings

# Create Base for models to inherit
Base = declarative_base()


def _create_engine():
    """Create SQLAlchemy engine based on settings; handle SQLite special case."""
    settings = get_settings()
    connect_args = {}
    if settings.DATABASE_URL.startswith("sqlite"):
        # Needed for SQLite to allow usage across threads in FastAPI
        connect_args = {"check_same_thread": False}
    engine = create_engine(settings.DATABASE_URL, echo=False, future=True, connect_args=connect_args)
    return engine


# Global engine and SessionLocal
engine = _create_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)


# PUBLIC_INTERFACE
def get_db() -> Generator[Session, None, None]:
    """Yield a database session for request-scoped usage in FastAPI dependencies."""
    db: Optional[Session] = None
    try:
        db = SessionLocal()
        yield db
    finally:
        if db is not None:
            db.close()


# PUBLIC_INTERFACE
def init_db() -> None:
    """Create database tables during development if they don't exist."""
    # Lazy import to avoid circular import
    from src.db import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
