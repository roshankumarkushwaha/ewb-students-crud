
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.main as main_module
from app import crud
from app.database import Base


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Give every test its own temporary database.
    db_file = tmp_path / "test_students.db"
    test_engine = create_engine(
        f"sqlite:///{db_file.as_posix()}",
        connect_args={"check_same_thread": False},
    )

    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
    )

    # Create the schema in the temporary database.
    Base.metadata.create_all(bind=test_engine)

    # Make CRUD operations use the temporary database.
    monkeypatch.setattr(crud, "SessionLocal", TestingSessionLocal)

    # Prevent application startup from initializing the real database.
    monkeypatch.setattr(
        main_module,
        "init_db",
        lambda: Base.metadata.create_all(bind=test_engine),
    )

    try:
        with TestClient(main_module.app) as test_client:
            yield test_client
    finally:
        test_engine.dispose()
