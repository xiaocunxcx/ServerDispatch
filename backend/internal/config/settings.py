from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "sqlite+pysqlite:///./serverdispatch.db"
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    auth_mode: str = "local"
    ldap_uri: str = ""
    ldap_base_dn: str = ""
    ldap_bind_dn: str = ""
    ldap_bind_password: str = ""
    ldap_user_dn_template: str = ""
    admin_ldap_ids: List[str] | str = ""
    app_timezone: str = "Asia/Shanghai"
    log_level: str = "INFO"
    audit_retention_days: int = 30
    metrics_retention_days: int = 30
    rate_limit_login_per_minute: int = 10
    rate_limit_reservation_per_minute: int = 30
    rate_limit_window_seconds: int = 60
    cors_allow_origins: List[str] | str = "*"
    cors_allow_methods: List[str] | str = "*"
    cors_allow_headers: List[str] | str = "*"

    @field_validator("admin_ldap_ids", mode="before")
    @classmethod
    def split_admin_ids(cls, value: str | List[str]) -> List[str]:
        if isinstance(value, list):
            return value
        if not value:
            return []
        return [item.strip() for item in value.split(",") if item.strip()]

    @field_validator("auth_mode", mode="before")
    @classmethod
    def normalize_auth_mode(cls, value: str | None) -> str:
        if not value:
            return "local"
        normalized = value.strip().lower()
        if normalized not in {"local", "ldap"}:
            raise ValueError("auth_mode must be 'local' or 'ldap'")
        return normalized

    @field_validator(
        "cors_allow_origins",
        "cors_allow_methods",
        "cors_allow_headers",
        mode="before",
    )
    @classmethod
    def split_cors_values(cls, value: str | List[str]) -> List[str]:
        if isinstance(value, list):
            return value
        if not value:
            return ["*"]
        items = [item.strip() for item in str(value).split(",") if item.strip()]
        return items or ["*"]

    @model_validator(mode="after")
    def validate_ldap_settings(self) -> "Settings":
        if self.auth_mode != "ldap":
            return self
        missing = [
            name
            for name in (
                "ldap_uri",
                "ldap_base_dn",
                "ldap_bind_dn",
                "ldap_bind_password",
                "ldap_user_dn_template",
            )
            if not getattr(self, name)
        ]
        if missing:
            raise ValueError(f"Missing LDAP settings: {', '.join(missing)}")
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
