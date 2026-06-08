"""
Database connection management.
Provides SQLAlchemy engine, session factory, and context manager.
"""

from contextlib import contextmanager
from collections.abc import Generator

from sqlalchemy import create_engine, Engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from database.models import Base


def _make_engine() -> Engine:
    """Create a SQLAlchemy engine from settings."""
    settings = get_settings()
    url = settings.database_url

    # SQLite-specific: allow usage across threads
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    return create_engine(url, connect_args=connect_args, echo=False)


# Module-level engine singleton
_engine: Engine | None = None


def get_engine() -> Engine:
    """Get the shared database engine (created once)."""
    global _engine
    if _engine is None:
        _engine = _make_engine()
    return _engine


def init_db() -> None:
    """
    Create all database tables if they don't exist.
    Call this once at application startup.
    """
    Base.metadata.create_all(bind=get_engine())
    migrate_db()


def migrate_db() -> None:
    """
    Apply additive column migrations to existing SQLite databases.
    Uses PRAGMA to detect missing columns and ALTER TABLE to add them.
    Idempotent — safe to run multiple times.

    New columns per phase:
        Phase 3: source, trend_score, raw_title, source_url
    """
    engine = get_engine()
    settings = get_settings()

    # Alembic handles PostgreSQL — only run SQLite migrations here
    if not settings.database_url.startswith("sqlite"):
        return

    phase3_columns: dict[str, str] = {
        "source":      "VARCHAR(50) DEFAULT 'manual'",
        "trend_score": "FLOAT",
        "raw_title":   "VARCHAR(500)",
        "source_url":  "VARCHAR(1000)",
    }

    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(topics)"))
        existing_cols = {row[1] for row in result.fetchall()}

        for col_name, col_ddl in phase3_columns.items():
            if col_name not in existing_cols:
                conn.execute(text(f"ALTER TABLE topics ADD COLUMN {col_name} {col_ddl}"))

        conn.commit()


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Context manager that provides a database session.

    Usage:
        with get_session() as session:
            session.add(topic)
    """
    factory = sessionmaker(autocommit=False, autoflush=False, bind=get_engine(), expire_on_commit=False)
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
