from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from internal.api.errors import ApiError
from internal.auth.permissions import require_admin
from internal.db.models.npu_card import CardStatus, NPUCard
from internal.db.models.server import Server, ServerStatus
from internal.db.models.user import User
from internal.db.session import get_db
from internal.inventory.discovery import TopologyDiscoveryService

router = APIRouter(prefix="/servers", tags=["inventory"])


class ServerCreateRequest(BaseModel):
    ip: str
    access_account: str
    hostname: str | None = None
    model: str | None = None
    card_count: int | None = None


class ServerResponse(BaseModel):
    id: str
    hostname: str | None
    ip: str
    status: str
    model: str | None
    card_count: int | None
    chip_id: str | None
    hbm_gb: int | None


class DiscoveryResponse(BaseModel):
    id: str
    hostname: str | None
    ip: str
    status: str
    model: str | None
    card_count: int | None
    chip_id: str | None
    hbm_gb: int | None


def to_response(server: Server) -> ServerResponse:
    return ServerResponse(
        id=server.id,
        hostname=server.hostname,
        ip=server.ip,
        status=server.status.value,
        model=server.model,
        card_count=server.card_count,
        chip_id=server.chip_id,
        hbm_gb=server.hbm_gb,
    )


@router.post("", response_model=ServerResponse, status_code=201)
def add_server(
    payload: ServerCreateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> ServerResponse:
    _ = admin
    existing = db.query(Server).filter(Server.ip == payload.ip).one_or_none()
    if existing:
        raise ApiError(code="server_exists", message="Server already exists", status_code=409)

    server = Server(
        hostname=payload.hostname,
        ip=payload.ip,
        access_account=payload.access_account,
        status=ServerStatus.unknown,
        model=payload.model,
        card_count=payload.card_count,
    )
    db.add(server)
    db.commit()
    db.refresh(server)

    if payload.card_count:
        cards = [
            NPUCard(server_id=server.id, index=index, status=CardStatus.free)
            for index in range(payload.card_count)
        ]
        db.add_all(cards)
        db.commit()

    return to_response(server)


@router.post("/{server_id}/discover", response_model=DiscoveryResponse)
def discover_server(
    server_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> DiscoveryResponse:
    _ = admin
    server = db.query(Server).filter(Server.id == server_id).one_or_none()
    if not server:
        raise ApiError(code="server_not_found", message="Server not found", status_code=404)

    discovery = TopologyDiscoveryService(db)
    discovery.discover(server)
    db.refresh(server)

    return DiscoveryResponse(
        id=server.id,
        hostname=server.hostname,
        ip=server.ip,
        status=server.status.value,
        model=server.model,
        card_count=server.card_count,
        chip_id=server.chip_id,
        hbm_gb=server.hbm_gb,
    )
