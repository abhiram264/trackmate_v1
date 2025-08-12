import os
import pathlib
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine

from app.main import app
import app.database as db_module

TEST_DB_PATH = pathlib.Path("./test.db")
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH.as_posix()}"

# Create a separate SQLite engine for tests
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Ensure metadata uses the test engine
SQLModel.metadata.create_all(engine)


def override_get_session():
    with Session(engine) as session:
        yield session


# Override the app's DB engine and dependency before tests
app.dependency_overrides[db_module.get_session] = override_get_session
# Point the module-level engine to the test engine so startup hooks use it
db_module.engine = engine


@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown_db():
    SQLModel.metadata.create_all(engine)
    yield
    # Teardown: close connections and remove DB file
    try:
        # Best-effort cleanup
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()
    except Exception:
        pass


@pytest.fixture(autouse=True)
def clean_db_between_tests():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    yield


@pytest.fixture()
def client():
    return TestClient(app) 