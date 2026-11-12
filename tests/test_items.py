import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.fixture
def client(db, mysql_engine, monkeypatch):
    from backend.server import main
    from backend.server.db import get_db

    monkeypatch.setattr(main, "engine", mysql_engine)

    def override_get_db():
        with Session(mysql_engine) as session:
            try:
                yield session
            except Exception:
                session.rollback()
                raise

    main.app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(main.app) as test_client:
            yield test_client
    finally:
        main.app.dependency_overrides.pop(get_db, None)


def test_create_item(client):
    response = client.post("/api/items/", json={"name": "Test Item", "description": "A test item"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["description"] == "A test item"
    assert "id" in data

def test_read_item(client):
    # First, create an item
    response = client.post("/api/items/", json={"name": "Read Item", "description": "Read description"})
    item_id = response.json()["id"]

    # Now, read the item
    response = client.get(f"/api/items/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item_id
    assert data["name"] == "Read Item"
    assert data["description"] == "Read description"

def test_read_items(client):
    # Create multiple items
    client.post("/api/items/", json={"name": "Item 1", "description": "Desc 1"})
    client.post("/api/items/", json={"name": "Item 2", "description": "Desc 2"})

    response = client.get("/api/items/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2

def test_update_item(client):
    # Create an item
    response = client.post("/api/items/", json={"name": "Old Name", "description": "Old description"})
    item_id = response.json()["id"]

    # Update the item
    response = client.put(f"/api/items/{item_id}", json={"name": "New Name", "description": "New description"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item_id
    assert data["name"] == "New Name"
    assert data["description"] == "New description"

def test_delete_item(client):
    # Create an item
    response = client.post("/api/items/", json={"name": "To Delete", "description": "To be deleted"})
    item_id = response.json()["id"]

    # Delete the item
    response = client.delete(f"/api/items/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True

    # Try to get the deleted item
    response = client.get(f"/api/items/{item_id}")
    assert response.status_code == 404

def test_update_nonexistent_item(client):
    non_existent_id = 9999  # Assuming this ID does not exist in the test database
    update_data = {"name": "Updated Name", "description": "Updated Description"}
    response = client.put(f"/api/items/{non_existent_id}", json=update_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}

def test_delete_nonexistent_item(client):
    non_existent_id = 9999  # Assuming this ID does not exist in the test database
    response = client.delete(f"/api/items/{non_existent_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}


def test_name_length_validation(client):
    for name in ("", "x" * 256):
        response = client.post("/api/items/", json={"name": name})
        assert response.status_code == 422


def test_unicode_and_pagination(client):
    for name in ("任务一 🚀", "任务二"):
        assert client.post("/api/items/", json={"name": name}).status_code == 200
    response = client.get("/api/items/?skip=1&limit=1")
    assert [item["name"] for item in response.json()] == ["任务二"]
    assert client.get("/api/items/?limit=101").status_code == 422
