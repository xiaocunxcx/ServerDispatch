from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from internal.db.models.npu_card import CardStatus, NPUCard
from internal.db.models.server import Server, ServerStatus


@dataclass
class DiscoveryResult:
    model: str
    card_count: int
    chip_id: str
    hbm_gb: int


class TopologyDiscoveryService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def discover(self, server: Server) -> DiscoveryResult:
        model = server.model or "910B"
        if model == "310":
            card_count = server.card_count or 2
            hbm_gb = server.hbm_gb or 8
        else:
            card_count = server.card_count or 8
            hbm_gb = server.hbm_gb or 32

        chip_id = server.chip_id or f"{model}-{server.id[:8]}"

        server.model = model
        server.card_count = card_count
        server.hbm_gb = hbm_gb
        server.chip_id = chip_id
        server.status = ServerStatus.online

        self._ensure_cards(server.id, card_count)
        self.db.add(server)
        self.db.commit()
        self.db.refresh(server)

        return DiscoveryResult(
            model=model,
            card_count=card_count,
            chip_id=chip_id,
            hbm_gb=hbm_gb,
        )

    def _ensure_cards(self, server_id: str, card_count: int) -> None:
        existing = self.db.query(NPUCard).filter(NPUCard.server_id == server_id).all()
        existing_indices = {card.index for card in existing}

        to_create = [
            NPUCard(server_id=server_id, index=index, status=CardStatus.free)
            for index in range(card_count)
            if index not in existing_indices
        ]
        if to_create:
            self.db.add_all(to_create)
