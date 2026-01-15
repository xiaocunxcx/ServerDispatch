from __future__ import annotations

from sqlalchemy.orm import Session

from internal.api.errors import ApiError
from internal.auth.ldap import LdapClient
from internal.auth.passwords import verify_password
from internal.config.settings import get_settings
from internal.db.models.user import User, UserStatus


class AuthService:
    def __init__(self, db: Session, ldap_client: LdapClient) -> None:
        self.db = db
        self.ldap_client = ldap_client

    def authenticate_and_get_user(self, ldap_id: str, password: str) -> User:
        settings = get_settings()

        if settings.auth_mode == "ldap":
            if not self.ldap_client.authenticate(ldap_id, password):
                raise ApiError(
                    code="invalid_credentials",
                    message="LDAP authentication failed",
                    status_code=401,
                )
            user = self.get_whitelisted_user(ldap_id)
            if not user:
                raise ApiError(code="not_whitelisted", message="User not whitelisted", status_code=403)
            if user.status != UserStatus.active:
                raise ApiError(code="user_disabled", message="User disabled", status_code=403)
            return user

        user = self.get_whitelisted_user(ldap_id)
        if not user or not user.password_hash:
            raise ApiError(code="invalid_credentials", message="Invalid credentials", status_code=401)
        if user.status != UserStatus.active:
            raise ApiError(code="user_disabled", message="User disabled", status_code=403)
        if not verify_password(password, user.password_hash):
            raise ApiError(code="invalid_credentials", message="Invalid credentials", status_code=401)
        return user

    def get_whitelisted_user(self, ldap_id: str) -> User | None:
        return self.db.query(User).filter(User.ldap_id == ldap_id).one_or_none()
