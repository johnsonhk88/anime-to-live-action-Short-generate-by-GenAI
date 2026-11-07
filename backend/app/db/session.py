from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.db.models import Base

_engine = None
SessionLocal = None


def _make_engine(url: str):
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        if url.startswith("sqlite:///") and not url.startswith("sqlite:///:memory:"):
            db_path = url.replace("sqlite:///", "", 1)
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    return create_engine(url, future=True, connect_args=connect_args)


def configure(url: str | None = None) -> None:
    global _engine, SessionLocal
    settings_url = url or get_settings().database_url
    _engine = _make_engine(settings_url)
    SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False, future=True)


def get_engine():
    if _engine is None:
        configure()
    return _engine


def init_db() -> None:
    configure()
    Base.metadata.create_all(bind=get_engine())


def get_db():
    if SessionLocal is None:
        init_db()
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
