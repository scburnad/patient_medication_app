from sqlalchemy import text

from patient_medication_app.database.connections import engine


def test_db_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        assert result.scalar() == 1
