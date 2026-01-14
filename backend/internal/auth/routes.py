from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from jose import jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session

from internal.api.errors import ApiError
from internal.auth.deps import get_current_user
from internal.auth.ldap import LdapClient
from internal.auth.service import AuthService
from internal.config.settings import get_settings
from internal.db.models.user import User
from internal.db.session import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    ldap_id: str
    password: str


class UserResponse(BaseModel):
    id: str
    ldap_id: str
    ssh_login: str
    display_name: str | None
    team_id: str | None
    status: str


class LoginResponse(BaseModel):
    token: str
    user: UserResponse


class SshKeyUpdateRequest(BaseModel):
    ssh_public_key: str


def build_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        ldap_id=user.ldap_id,
        ssh_login=user.ssh_login,
        display_name=user.display_name,
        team_id=user.team_id,
        status=user.status.value,
    )


def create_access_token(user: User) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": user.id,
        "ldap_id": user.ldap_id,
        "iat": int(now.timestamp()),
        "exp": int(expires.timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    settings = get_settings()
    auth_service = AuthService(db, LdapClient(settings))
    user = auth_service.authenticate_and_get_user(payload.ldap_id, payload.password)
    token = create_access_token(user)
    return LoginResponse(token=token, user=build_user_response(user))


@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)) -> UserResponse:
    return build_user_response(user)


@router.put("/me/ssh-key", response_model=UserResponse)
def update_ssh_key(
    payload: SshKeyUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> UserResponse:
    ssh_key = payload.ssh_public_key.strip()
    if not ssh_key:
        raise ApiError(code="invalid_ssh_key", message="SSH public key required")

    user.ssh_public_key = ssh_key
    db.add(user)
    db.commit()
    db.refresh(user)
    return build_user_response(user)
