"""Admin bootstrap must not be reachable through an unauthenticated write route.

These tests use only an in-memory database. They never connect to Atlas.
"""

import copy
import inspect
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import server


class MemoryCollection:
    def __init__(self, rows=()):
        self.rows = copy.deepcopy(list(rows))
        self.writes = 0

    async def find_one(self, query, *args, **kwargs):
        for row in self.rows:
            if all(row.get(key) == value for key, value in query.items()):
                return copy.deepcopy(row)
        return None

    async def insert_one(self, document):
        self.rows.append(copy.deepcopy(document))
        self.writes += 1
        return SimpleNamespace(inserted_id=len(self.rows))

    async def update_one(self, query, update, *args, **kwargs):
        for row in self.rows:
            if all(row.get(key) == value for key, value in query.items()):
                row.update(copy.deepcopy(update.get("$set", {})))
                self.writes += 1
                return SimpleNamespace(matched_count=1)
        return SimpleNamespace(matched_count=0)


class MemoryDB:
    def __init__(self, existing_admin=False):
        self.admin_users = MemoryCollection(
            [{"email": "owner@example.test"}] if existing_admin else []
        )
        self.users = MemoryCollection(
            [{"id": "owner-1", "email": "owner@example.test", "password_hash": "unchanged"}]
            if existing_admin else []
        )

    def snapshot(self):
        return copy.deepcopy((self.admin_users.rows, self.users.rows))

    @property
    def writes(self):
        return self.admin_users.writes + self.users.writes


@pytest.fixture
def isolated_app(monkeypatch):
    db = MemoryDB()
    monkeypatch.setattr(server, "db", db)
    app = FastAPI()
    app.include_router(server.api_router)
    return app, db


def test_public_admin_setup_route_is_not_registered():
    assert not [
        (route.path, route.methods)
        for route in server.app.routes
        if route.path.endswith("/admin-setup-t2d") or route.name == "admin_setup"
    ]


def test_startup_does_not_reset_admin_credentials():
    startup_source = "\n".join(
        inspect.getsource(handler) for handler in server.app.router.on_startup
    )
    assert "admin_users" not in startup_source
    assert "admin_password" not in startup_source


@pytest.mark.parametrize("existing_admin", [False, True])
@pytest.mark.parametrize("logged_in", [False, True])
def test_get_cannot_create_or_reset_admin(monkeypatch, existing_admin, logged_in):
    db = MemoryDB(existing_admin=existing_admin)
    monkeypatch.setattr(server, "db", db)
    app = FastAPI()
    app.include_router(server.api_router)
    headers = {}
    if logged_in:
        token = server.create_token("student-1", "student@example.test")
        headers["Authorization"] = f"Bearer {token}"

    before = db.snapshot()
    response = TestClient(app).get("/api/admin-setup-t2d", headers=headers)

    assert response.status_code in (404, 405)
    assert db.snapshot() == before
    assert db.writes == 0


@pytest.mark.parametrize("path", [
    "/api/admin-setup-t2d",
    "/admin-setup-t2d",
    "/api/api/admin-setup-t2d",
])
@pytest.mark.parametrize("method", ["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
def test_all_known_paths_and_methods_are_write_free(isolated_app, path, method):
    app, db = isolated_app
    before = db.snapshot()

    response = TestClient(app).request(method, path)

    assert response.status_code in (404, 405)
    assert db.snapshot() == before
    assert db.writes == 0


def test_guarded_admin_add_still_works_with_test_only_secret(isolated_app, monkeypatch):
    app, db = isolated_app
    monkeypatch.setattr(server, "ADMIN_BOOTSTRAP_SECRET", "isolated-test-secret")
    client = TestClient(app)

    denied = client.post("/api/admin/add", json={"email": "owner@example.test"})
    assert denied.status_code == 403
    assert db.writes == 0

    allowed = client.post(
        "/api/admin/add",
        json={"email": "owner@example.test"},
        headers={"X-Admin-Secret": "isolated-test-secret"},
    )
    assert allowed.status_code == 200
    assert len(db.admin_users.rows) == 1
    assert db.admin_users.rows[0]["email"] == "owner@example.test"


def test_normal_login_is_unchanged(isolated_app, monkeypatch):
    app, db = isolated_app
    db.users.rows.append({
        "id": "student-1",
        "email": "student@example.test",
        "password_hash": server.pwd_context.hash("local-test-password"),
        "is_admin": False,
        "is_premium": False,
    })
    monkeypatch.setattr(server, "_migrate_guest_learning_to_user", AsyncMock())

    response = TestClient(app).post(
        "/api/auth/login",
        json={"email": "student@example.test", "password": "local-test-password"},
    )

    assert response.status_code == 200
    assert response.json()["user"]["id"] == "student-1"
