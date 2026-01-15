from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from conftest import load_create_app
from internal.auth.passwords import hash_password
from internal.config import settings as settings_module
from internal.db.models.user import User, UserStatus
from internal.db.session import get_db


@pytest.fixture()
def auth_client(db_session, monkeypatch):
    monkeypatch.setenv("AUTH_MODE", "local")
    settings_module.get_settings.cache_clear()
    app = load_create_app()()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def test_local_login_success(auth_client: TestClient, db_session):
    user = User(
        ldap_id="user1",
        ssh_login="user1",
        status=UserStatus.active,
        password_hash=hash_password("secret123"),
    )
    db_session.add(user)
    db_session.commit()

    response = auth_client.post(
        "/auth/login",
        json={"ldap_id": "user1", "password": "secret123"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["token"]
    assert payload["user"]["ldap_id"] == "user1"


def test_local_login_invalid_password(auth_client: TestClient, db_session):
    user = User(
        ldap_id="user2",
        ssh_login="user2",
        status=UserStatus.active,
        password_hash=hash_password("secret123"),
    )
    db_session.add(user)
    db_session.commit()

    response = auth_client.post(
        "/auth/login",
        json={"ldap_id": "user2", "password": "wrong"},
    )

    assert response.status_code == 401
