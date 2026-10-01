import pytest
from fastapi.testclient import TestClient

from app.main import app
import app.database as database


@pytest.fixture
def client(tmp_path, monkeypatch):
    database_path = tmp_path / "test.db"
    monkeypatch.setattr(database, "DATABASE_PATH", database_path)

    with TestClient(app) as client:
        yield client


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_get_items(client):
    response = client.get("/api/v1/items")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert len(response.json()["data"]) == 10


def test_get_items_with_pagination(client):
    response = client.get("/api/v1/items?limit=2&offset=0")

    assert response.status_code == 200
    assert len(response.json()["data"]) == 2


def test_invalid_pagination(client):
    response = client.get("/api/v1/items?limit=0")

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_get_item(client):
    response = client.get("/api/v1/items")

    item_id = response.json()["data"][0]["id"]

    response = client.get(f"/api/v1/items/{item_id}")

    assert response.status_code == 200
    assert response.json()["data"]["id"] == item_id


def test_get_item_not_found(client):
    response = client.get("/api/v1/items/not-found")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_create_item(client):
    item = {
        "title": "Test item",
        "source": {
            "name": "Test source"
        },
        "publishedAt": "2026-09-30T12:00:00Z",
        "url": "https://example.com",
        "summary": "Test summary",
        "tags": ["test"]
    }

    response = client.post("/api/v1/items", json=item)

    assert response.status_code == 201
    assert response.json()["status"] == "ok"
    assert response.json()["data"]["title"] == "Test item"
    assert "id" in response.json()["data"]


def test_create_item_invalid(client):
    item = {
        "title": "",
        "source": {
            "name": "Test source"
        },
        "publishedAt": "not-a-date",
        "url": "https://example.com",
        "summary": "Test summary",
        "tags": []
    }

    response = client.post("/api/v1/items", json=item)

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_create_item_with_id(client):
    item = {
        "id": "123",
        "title": "Test item",
        "source": {
            "name": "Test source"
        },
        "publishedAt": "2026-09-30T12:00:00Z",
        "url": "https://example.com",
        "summary": "Test summary",
        "tags": []
    }

    response = client.post("/api/v1/items", json=item)

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_update_item(client):
    response = client.get("/api/v1/items")
    item_id = response.json()["data"][0]["id"]

    response = client.patch(
        f"/api/v1/items/{item_id}",
        json={"title": "Updated title"}
    )

    assert response.status_code == 200
    assert response.json()["data"]["title"] == "Updated title"


def test_update_item_not_found(client):
    response = client.patch(
        "/api/v1/items/not-found",
        json={"title": "Updated title"}
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_update_item_with_id(client):
    response = client.get("/api/v1/items")
    item_id = response.json()["data"][0]["id"]

    response = client.patch(
        f"/api/v1/items/{item_id}",
        json={"id": "new-id"}
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_delete_item(client):
    response = client.get("/api/v1/items")
    item_id = response.json()["data"][0]["id"]

    response = client.delete(f"/api/v1/items/{item_id}")

    assert response.status_code == 204
    assert response.content == b""


def test_delete_item_not_found(client):
    response = client.delete("/api/v1/items/not-found")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"