import importlib
import sys

import pytest
from sqlalchemy import text

from patient_medication_app.database.connections import engine, get_session


def test_db_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        assert result.scalar() == 1


def test_get_session_closes():
    gen = get_session()
    session = next(gen)
    assert session is not None
    gen.close()


def test_missing_database_url(monkeypatch):
    # Remove the module from sys.modules to force reload
    sys.modules.pop("patient_medication_app.database.connections", None)
    # Patch the settings to have database_url as None
    from patient_medication_app import settings as settings_module

    monkeypatch.setattr(settings_module.settings, "database_url", None)
    with pytest.raises(ValueError, match="Database URL must not be None"):
        import patient_medication_app.database.connections

        importlib.reload(patient_medication_app.database.connections)
