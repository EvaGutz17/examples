from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker, Session
from apitesting.main_split import app, Base, get_db
from apitesting.operations import (
    DBItem,
    db_create_item,
    db_read_item,
    db_update_item,
    db_delete_item,
    ItemCreate,
    ItemUpdate,
)
import pytest

# Setup the TestClient
client = TestClient(app)

# Setup the in-memory SQLite database for testing
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to override the get_db dependency in the main app
def override_get_db():
    database = TestingSessionLocal()
    yield database
    database.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def session() -> Generator[Session, None, None]:
    # Create the tables in the test database
    Base.metadata.create_all(bind=engine)

    db_session = TestingSessionLocal()

    # create test items
    db_item = DBItem(id=100, name="Test Item", description="This is a test item")
    db_session.add(db_item)
    db_session.commit()

    yield db_session

    # Close the database and drop the tables in the test database
    db_session.close()
    Base.metadata.drop_all(bind=engine)


def test_create_item(session: Session) -> None:
    item = db_create_item(
        ItemCreate(name="Test Item", description="This is a test item"), session
    )
    assert item.name == "Test Item"
    assert item.description == "This is a test item"


def test_create_improper_item():
    response = client.post("/items/", json={"description": "This is a test item"})
    assert response.status_code == 422, response.text


def test_read_item(session: Session) -> None:
    # Create an item
    item = db_create_item(
        ItemCreate(name="Test Item", description="This is a test item"), session
    )
    item_id = item.id

    item = db_read_item(item_id, session)
    assert item.name == "Test Item"
    assert item.description == "This is a test item"
    assert item.id == item_id


def test_update_item(session: Session) -> None:
    # Create an item
    item = db_create_item(
        ItemCreate(name="Test Item", description="This is a test item"), session
    )
    item_id = item.id

    item = db_update_item(
        item_id, ItemUpdate(name="New Name", description=None), session
    )
    assert item.name == "New Name"


def test_delete_item(session: Session) -> None:
    # Create an item
    item = db_create_item(
        ItemCreate(name="Test Item", description="This is a test item"), session
    )
    item_id = item.id

    item = db_delete_item(item_id, session)
    assert item.name == "Test Item"
    assert item.id == item_id
    # Try to get the deleted item
    with pytest.raises(Exception):
        db_read_item(item_id, session)
