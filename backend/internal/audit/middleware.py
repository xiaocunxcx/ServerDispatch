from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from internal.audit.service import AuditService
from internal.db import session as db_session

LOG_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
SKIP_PATHS = {"/metrics/ingest"}


def parse_target(path: str) -> tuple[str | None, str | None]:
    parts = [part for part in path.strip("/").split("/") if part]
    if not parts:
        return None, None
    target_type = parts[0]
    target_id = parts[1] if len(parts) > 1 else None
    return target_type, target_id


class AuditLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if request.url.path in SKIP_PATHS:
            return response
        if request.method not in LOG_METHODS and request.url.path != "/audit-logs/export":
            return response

        user = getattr(request.state, "user", None)
        if not user:
            return response

        target_type, target_id = parse_target(request.url.path)
        metadata = {
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "query": dict(request.query_params),
        }

        try:
            with db_session.SessionLocal() as db:
                service = AuditService(db)
                service.log_action(
                    actor_user_id=user.id,
                    action_type=f"{request.method} {request.url.path}",
                    target_type=target_type,
                    target_id=target_id,
                    metadata=metadata,
                    timestamp=datetime.now(timezone.utc),
                )
                db.commit()
        except Exception:  # pragma: no cover - audit should not break requests
            logging.exception("Failed to write audit log")

        return response
