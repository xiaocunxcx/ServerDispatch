from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from internal.api.errors import ApiError
from internal.auth.permissions import require_admin
from internal.db.models.alert import Alert, AlertStatus
from internal.db.models.user import User
from internal.db.session import get_db

router = APIRouter(prefix="/alerts", tags=["metrics"])


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    server_id: str
    card_id: str | None
    type: str
    status: str
    detected_at: datetime
    resolved_at: datetime | None


@router.post("/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> AlertResponse:
    _ = admin
    alert = db.query(Alert).filter(Alert.id == alert_id).one_or_none()
    if not alert:
        raise ApiError(code="alert_not_found", message="Alert not found", status_code=404)

    if alert.status != AlertStatus.resolved:
        alert.status = AlertStatus.resolved
        alert.resolved_at = datetime.now(timezone.utc)
        db.add(alert)
        db.commit()
        db.refresh(alert)

    return AlertResponse.model_validate(alert)
