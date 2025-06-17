import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from patient_medication_app.app import app
from patient_medication_app.core.models import Base
from patient_medication_app.database.connections import get_session

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session):
    """Create a test client using the test database session."""

    def override_get_session():
        try:
            yield db_session
        finally:
            db_session.close()

    # Override the database session dependency
    app.dependency_overrides[get_session] = override_get_session

    # Create test client
    with TestClient(app) as test_client:
        yield test_client

    # Clear dependency overrides
    app.dependency_overrides.clear()
