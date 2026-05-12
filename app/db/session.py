from sqlalchemy.orm import sessionmaker, Session
from .engine import engine
from typing import Generator
from contextlib import contextmanager

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

@contextmanager
def get_db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()