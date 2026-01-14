from __future__ import annotations

import csv
import io
import json
from datetime import datetime

from fastapi import APIRouter, Depends, Query, Response
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from internal.auth.permissions import require_admin
from internal.db.models.user import User
from internal.db.session import get_db
from internal.audit.service import AuditService

router = APIRouter(prefix="/audit-logs", tags=["audit"])


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    actor_user_id: str
    action_type: str
    target_type: str | None
    target_id: str | None
    timestamp: datetime
    metadata: dict | None


class AuditLogListResponse(BaseModel):
    logs: list[AuditLogResponse]


def to_response(log: AuditLog) -> AuditLogResponse:
    return AuditLogResponse(
        id=log.id,
        actor_user_id=log.actor_user_id,
        action_type=log.action_type,
        target_type=log.target_type,
        target_id=log.target_id,
        timestamp=log.timestamp,
        metadata=log.meta,
    )


@router.get("", response_model=AuditLogListResponse)
def list_audit_logs(
    start_from: datetime | None = Query(default=None, alias="from"),
    end_to: datetime | None = Query(default=None, alias="to"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> AuditLogListResponse:
    _ = admin
    service = AuditService(db)
    logs = service.list_logs(start_from, end_to)
    return AuditLogListResponse(logs=[to_response(log) for log in logs])


@router.get("/export")
def export_audit_logs(
    start_from: datetime | None = Query(default=None, alias="from"),
    end_to: datetime | None = Query(default=None, alias="to"),
    format: str = Query(default="csv"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> Response:
    _ = admin
    service = AuditService(db)
    logs = service.list_logs(start_from, end_to)

    if format == "json":
        payload = [to_response(log).model_dump(mode="json") for log in logs]
        return Response(content=json.dumps(payload), media_type="application/json")
    if format != "csv":
        return Response(status_code=400, content="Unsupported format")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "id",
            "actor_user_id",
            "action_type",
            "target_type",
            "target_id",
            "timestamp",
            "metadata",
        ]
    )
    for log in logs:
        writer.writerow(
            [
                log.id,
                log.actor_user_id,
                log.action_type,
                log.target_type or "",
                log.target_id or "",
                log.timestamp.isoformat(),
                log.meta or {},
            ]
        )

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit-logs.csv"},
    )
