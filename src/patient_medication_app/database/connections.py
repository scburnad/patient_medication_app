"""Database connections for patient medication management."""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from patient_medication_app.settings import settings

# Create the database engine
if settings.database_url is None:
    raise ValueError("Database URL must not be None")
engine = create_engine(settings.database_url, echo=True)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session() -> Generator[Session, None, None]:
    """Dependency to get a database session."""
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
