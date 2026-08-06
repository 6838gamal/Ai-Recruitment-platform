"""Database configuration and session management."""
import os
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


# ─── SQLAlchemy Engine ─────────────────────────────────────────────────────────

def get_database_url() -> str:
    """Get database URL, preferring environment variable."""
    # Replit provides DATABASE_URL environment variable
    url = os.environ.get("DATABASE_URL") or settings.DATABASE_URL
    # Ensure we use psycopg2 dialect
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


engine = create_engine(
    get_database_url(),
    pool_pre_ping=True,           # test connection before using from pool
    pool_size=5,                   # max persistent connections
    max_overflow=10,               # max extra connections during peak
    pool_recycle=1800,             # recycle connections after 30 min
    echo=settings.DEBUG,           # log SQL in debug mode
)


# ─── Session Factory ───────────────────────────────────────────────────────────

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ─── Declarative Base ─────────────────────────────────────────────────────────

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


# ─── Dependency ───────────────────────────────────────────────────────────────

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.
    Automatically closes the session after the request.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
