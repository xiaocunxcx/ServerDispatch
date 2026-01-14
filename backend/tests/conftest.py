import os
import sys
from datetime import datetime, timezone

import importlib.util
import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.append(ROOT)

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("LDAP_URI", "ldap://localhost")
os.environ.setdefault("LDAP_BASE_DN", "dc=example,dc=internal")
os.environ.setdefault("LDAP_BIND_DN", "cn=admin,dc=example,dc=internal")
os.environ.setdefault("LDAP_BIND_PASSWORD", "password")
os.environ.setdefault("LDAP_USER_DN_TEMPLATE", "uid={ldap_id},ou=People,dc=example,dc=internal")
os.environ.setdefault("ADMIN_LDAP_IDS", "[\"admin\"]")
os.environ.setdefault("RATE_LIMIT_LOGIN_PER_MINUTE", "2")
os.environ.setdefault("RATE_LIMIT_RESERVATION_PER_MINUTE", "2")
os.environ.setdefault("RATE_LIMIT_WINDOW_SECONDS", "60")

from internal.auth.deps import get_current_user
from internal.db.base import Base
from internal.db.models.user import User, UserStatus
from internal.db.session import get_db


def load_create_app():
    module_path = os.path.join(ROOT, "cmd", "api", "main.py")
    spec = importlib.util.spec_from_file_location("backend_api_main", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["backend_api_main"] = module
    spec.loader.exec_module(module)
    return module.create_app


@pytest.fixture()
def engine():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    import internal.db.session as db_session_module

    db_session_module.engine = engine
    db_session_module.SessionLocal = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, future=True
    )
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture()
def db_session(engine):
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture()
def test_user(db_session):
    user = User(
        ldap_id="user1",
        ssh_login="user1",
        ssh_public_key="ssh-rsa AAA",
        display_name="User One",
        status=UserStatus.active,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def admin_user(db_session):
    user = User(
        ldap_id="admin",
        ssh_login="admin",
        ssh_public_key="ssh-rsa ADMIN",
        display_name="Admin User",
        status=UserStatus.active,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def client(db_session, test_user):
    app = load_create_app()()

    def override_get_db():
        yield db_session

    def override_get_current_user(request: Request):
        request.state.user = test_user
        return test_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    return TestClient(app)


@pytest.fixture()
def admin_client(db_session, admin_user):
    app = load_create_app()()

    def override_get_db():
        yield db_session

    def override_get_current_user(request: Request):
        request.state.user = admin_user
        return admin_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    return TestClient(app)


@pytest.fixture()
def now():
    return datetime.now(timezone.utc)
