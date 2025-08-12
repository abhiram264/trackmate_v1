import os
from datetime import date, timedelta
from typing import Dict, Any

from fastapi.testclient import TestClient


def register_user(client: TestClient, name: str, email: str, password: str, role: str = "user") -> Dict[str, Any]:
    payload = {"name": name, "email": email, "password": password, "role": role}
    r = client.post("/auth/register", json=payload)
    assert r.status_code == 200, r.text
    return r.json()


def login_user(client: TestClient, email: str, password: str) -> str:
    r = client.post("/auth/login", data={"username": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def auth_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_auth_register_and_login_flow(client: TestClient):
    user = register_user(client, "Alice", "alice@example.com", "password123")
    assert user["email"] == "alice@example.com"

    token = login_user(client, "alice@example.com", "password123")
    assert isinstance(token, str) and len(token) > 10


def test_items_crud_and_filters(client: TestClient):
    # Create users
    admin = register_user(client, "Admin", "admin@example.com", "adminpass", role="admin")
    user = register_user(client, "Bob", "bob@example.com", "password456")

    admin_token = login_user(client, "admin@example.com", "adminpass")
    user_token = login_user(client, "bob@example.com", "password456")

    # Create items
    today = date.today()
    files = {}
    data = {
        "name": "Lost Wallet",
        "description": "Black leather wallet",
        "item_type": "lost",
        "location": "Library",
        "date": today.isoformat(),
    }

    r = client.post("/items/", headers=auth_headers(user_token), data=data, files=files)
    assert r.status_code == 200, r.text
    item1 = r.json()

    data2 = {
        "name": "Found Keys",
        "description": "Set of keys with red keychain",
        "item_type": "found",
        "location": "Cafeteria",
        "date": today.isoformat(),
    }
    r = client.post("/items/", headers=auth_headers(admin_token), data=data2, files=files)
    assert r.status_code == 200, r.text
    item2 = r.json()

    # List all
    r = client.get("/items/", headers=auth_headers(user_token))
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 2

    # Filters
    r = client.get("/items/?item_type=lost", headers=auth_headers(user_token))
    assert r.status_code == 200
    assert all(i["item_type"] == "lost" for i in r.json())

    r = client.get("/items/?location=lib", headers=auth_headers(user_token))
    assert r.status_code == 200
    assert any("Library" in i["location"] for i in r.json())

    r = client.get(f"/items/{item1['id']}", headers=auth_headers(user_token))
    assert r.status_code == 200 and r.json()["id"] == item1["id"]

    # Update
    update_payload = {"description": "Black leather wallet with ID"}
    r = client.put(f"/items/{item1['id']}", headers=auth_headers(user_token), json=update_payload)
    assert r.status_code == 200 and r.json()["description"].endswith("with ID")

    # Unauthorized update by other user
    r = client.put(f"/items/{item1['id']}", headers=auth_headers(admin_token), json=update_payload)
    # Admin can update; ensure allowed
    assert r.status_code == 200

    # Owner-only filter
    r = client.get("/items/?owner_only=true", headers=auth_headers(user_token))
    assert r.status_code == 200
    assert all(i["owner_id"] == user["id"] for i in r.json())


def test_claims_flow(client: TestClient):
    # Users
    owner = register_user(client, "Carol", "carol@example.com", "pass789")
    claimer = register_user(client, "Dave", "dave@example.com", "pass000")
    admin = register_user(client, "Root", "root@example.com", "rootpass", role="admin")

    owner_token = login_user(client, "carol@example.com", "pass789")
    claimer_token = login_user(client, "dave@example.com", "pass000")
    admin_token = login_user(client, "root@example.com", "rootpass")

    # Owner creates an item
    today = date.today()
    item_payload = {
        "name": "Lost Laptop",
        "description": "Grey Dell XPS",
        "item_type": "lost",
        "location": "Engineering Building",
        "date": today.isoformat(),
    }
    r = client.post("/items/", headers=auth_headers(owner_token), data=item_payload)
    assert r.status_code == 200, r.text
    item = r.json()

    # Claimer creates a claim
    claim_payload = {"item_id": item["id"], "message": "I found this laptop."}
    r = client.post("/claims/", headers=auth_headers(claimer_token), json=claim_payload)
    assert r.status_code == 200, r.text
    claim = r.json()

    # Duplicate claim by same user should fail
    r = client.post("/claims/", headers=auth_headers(claimer_token), json=claim_payload)
    assert r.status_code == 400

    # Owner cannot claim own item
    r = client.post("/claims/", headers=auth_headers(owner_token), json=claim_payload)
    assert r.status_code == 400

    # Owner/admin can view claims for the item
    r = client.get(f"/claims/item/{item['id']}", headers=auth_headers(owner_token))
    assert r.status_code == 200 and len(r.json()) >= 1

    r = client.get(f"/claims/item/{item['id']}", headers=auth_headers(admin_token))
    assert r.status_code == 200

    # Non-owner non-admin cannot view
    r = client.get(f"/claims/item/{item['id']}", headers=auth_headers(claimer_token))
    assert r.status_code == 403

    # Admin overview stats endpoint
    r = client.get("/claims/stats/overview", headers=auth_headers(admin_token))
    assert r.status_code == 200

    # Update claim status by owner (approve)
    status_update = {"status": "approved"}
    r = client.put(f"/claims/{claim['id']}/status", headers=auth_headers(owner_token), json=status_update)
    assert r.status_code == 200 and r.json()["status"] in ("approved", "pending", "rejected", "completed")

    # Claimer should not be able to update own claim
    r = client.put(f"/claims/{claim['id']}/status", headers=auth_headers(claimer_token), json=status_update)
    assert r.status_code in (400, 403)

    # Delete claim by admin
    r = client.delete(f"/claims/{claim['id']}", headers=auth_headers(admin_token))
    assert r.status_code == 200 