from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from internal.api.errors import ApiError
from internal.auth.passwords import hash_password
from internal.auth.permissions import require_admin
from internal.config.settings import get_settings
from internal.db.models.user import User, UserStatus
from internal.db.session import get_db

router = APIRouter(prefix="/admin/whitelist", tags=["admin"])


class WhitelistUserRequest(BaseModel):
    ldap_id: str
    ssh_login: str | None = None
    display_name: str | None = None
    team_id: str | None = None
    password: str | None = None


class WhitelistUserResponse(BaseModel):
    id: str
    ldap_id: str
    ssh_login: str
    display_name: str | None
    team_id: str | None
    status: str


class WhitelistListResponse(BaseModel):
    users: list[WhitelistUserResponse]


def to_response(user: User) -> WhitelistUserResponse:
    return WhitelistUserResponse(
        id=user.id,
        ldap_id=user.ldap_id,
        ssh_login=user.ssh_login,
        display_name=user.display_name,
        team_id=user.team_id,
        status=user.status.value,
    )


@router.get("", response_model=WhitelistListResponse)
def list_whitelist(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> WhitelistListResponse:
    _ = admin
    users = db.query(User).order_by(User.ldap_id.asc()).all()
    return WhitelistListResponse(users=[to_response(user) for user in users])


@router.post("", response_model=WhitelistUserResponse, status_code=201)
def add_whitelist_user(
    payload: WhitelistUserRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> WhitelistUserResponse:
    _ = admin
    settings = get_settings()
    password = payload.password.strip() if payload.password is not None else None
    if password == "":
        password = None

    user = db.query(User).filter(User.ldap_id == payload.ldap_id).one_or_none()
    if user:
        user.status = UserStatus.active
        if payload.ssh_login:
            user.ssh_login = payload.ssh_login
        if payload.display_name is not None:
            user.display_name = payload.display_name
        if payload.team_id is not None:
            user.team_id = payload.team_id
        if password is not None:
            user.password_hash = hash_password(password)
    else:
        if settings.auth_mode == "local" and not password:
            raise ApiError(code="password_required", message="Password required", status_code=400)
        user = User(
            ldap_id=payload.ldap_id,
            ssh_login=payload.ssh_login or payload.ldap_id,
            display_name=payload.display_name,
            team_id=payload.team_id,
            status=UserStatus.active,
            password_hash=hash_password(password) if password else None,
        )
        db.add(user)

    db.commit()
    db.refresh(user)
    return to_response(user)


@router.delete("/{ldap_id}", response_model=WhitelistUserResponse)
def disable_whitelist_user(
    ldap_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> WhitelistUserResponse:
    _ = admin
    user = db.query(User).filter(User.ldap_id == ldap_id).one_or_none()
    if not user:
        from internal.api.errors import ApiError

        raise ApiError(code="user_not_found", message="User not found", status_code=404)
    user.status = UserStatus.disabled
    db.add(user)
    db.commit()
    db.refresh(user)
    return to_response(user)
