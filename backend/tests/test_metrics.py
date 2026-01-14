from datetime import timedelta

from internal.db.models.alert import Alert, AlertStatus, AlertType
from internal.db.models.metric_snapshot import MetricSnapshot
from internal.db.models.npu_card import CardStatus, NPUCard
from internal.db.models.reservation import Reservation, ReservationMode, ReservationStatus
from internal.db.models.server import Server, ServerStatus
from internal.metrics.alerts import AlertService
from internal.metrics.retention import purge_old_snapshots


def create_server_with_card(db_session):
    server = Server(
        hostname="server-1",
        ip="10.0.0.1",
        status=ServerStatus.online,
        model="910B",
        card_count=1,
    )
    db_session.add(server)
    db_session.flush()

    card = NPUCard(server_id=server.id, index=0, status=CardStatus.free)
    db_session.add(card)
    db_session.commit()
    db_session.refresh(server)
    db_session.refresh(card)
    return server, card


def test_metrics_ingest_persists_snapshot_and_alert(client, db_session, now):
    server, card = create_server_with_card(db_session)

    payload = {
        "server_id": server.id,
        "snapshots": [
            {
                "card_index": 0,
                "timestamp": now.isoformat(),
                "ai_core_util": 0.9,
                "hbm_used": 10.0,
                "hbm_total": 32.0,
                "temperature": 70.0,
            }
        ],
    }

    response = client.post("/metrics/ingest", json=payload)
    assert response.status_code == 200
    assert response.json()["ingested_count"] == 1

    snapshot = db_session.query(MetricSnapshot).one()
    assert snapshot.server_id == server.id
    assert snapshot.card_id == card.id

    alert = db_session.query(Alert).one()
    assert alert.type == AlertType.no_reservation_high_load
    assert alert.status == AlertStatus.open


def test_alert_service_resolves_when_load_recovers(db_session, test_user, now):
    server, card = create_server_with_card(db_session)

    reservation = Reservation(
        user_id=test_user.id,
        server_id=server.id,
        card_id=card.id,
        mode=ReservationMode.carpool,
        start_time=now - timedelta(minutes=5),
        end_time=now + timedelta(minutes=5),
        status=ReservationStatus.active,
    )
    db_session.add(reservation)
    db_session.commit()

    snapshot = MetricSnapshot(
        server_id=server.id,
        card_id=card.id,
        timestamp=now,
        ai_core_util=0.0,
    )
    db_session.add(snapshot)
    db_session.commit()

    alert_service = AlertService(db_session)
    alerts = alert_service.evaluate_snapshot(snapshot)
    db_session.commit()

    assert len(alerts) == 1
    alert = db_session.query(Alert).one()
    assert alert.type == AlertType.reservation_zero_load
    assert alert.status == AlertStatus.open

    snapshot.ai_core_util = 0.5
    alerts = alert_service.evaluate_snapshot(snapshot, timestamp=now + timedelta(minutes=1))
    db_session.commit()

    assert len(alerts) == 1
    alert = db_session.query(Alert).one()
    assert alert.status == AlertStatus.resolved


def test_dashboard_summary_marks_self_reservation(client, db_session, test_user, now):
    server = Server(
        hostname="server-2",
        ip="10.0.0.2",
        status=ServerStatus.online,
        model="910B",
        card_count=2,
    )
    db_session.add(server)
    db_session.flush()

    card0 = NPUCard(server_id=server.id, index=0, status=CardStatus.free)
    card1 = NPUCard(server_id=server.id, index=1, status=CardStatus.free)
    db_session.add_all([card0, card1])
    db_session.flush()

    reservation = Reservation(
        user_id=test_user.id,
        server_id=server.id,
        card_id=card0.id,
        mode=ReservationMode.carpool,
        start_time=now - timedelta(minutes=1),
        end_time=now + timedelta(minutes=10),
        status=ReservationStatus.active,
    )
    db_session.add(reservation)
    db_session.commit()

    response = client.get("/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    cards = data["servers"][0]["cards"]
    status_by_index = {card["card_index"]: card["status"] for card in cards}
    assert status_by_index[0] == "self"
    assert status_by_index[1] == "free"


def test_alerts_list_filters_open_by_default(client, db_session, now):
    server, card = create_server_with_card(db_session)

    open_alert = Alert(
        server_id=server.id,
        card_id=card.id,
        type=AlertType.no_reservation_high_load,
        status=AlertStatus.open,
        detected_at=now,
    )
    resolved_alert = Alert(
        server_id=server.id,
        card_id=card.id,
        type=AlertType.reservation_zero_load,
        status=AlertStatus.resolved,
        detected_at=now - timedelta(minutes=10),
        resolved_at=now,
    )
    db_session.add_all([open_alert, resolved_alert])
    db_session.commit()

    response = client.get("/alerts")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["alerts"]) == 1
    assert payload["alerts"][0]["status"] == "open"

    response = client.get("/alerts", params={"status": "resolved"})
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["alerts"]) == 1
    assert payload["alerts"][0]["status"] == "resolved"


def test_metrics_retention_purges_old_snapshots(db_session, now):
    server, card = create_server_with_card(db_session)

    old_snapshot = MetricSnapshot(
        server_id=server.id,
        card_id=card.id,
        timestamp=now - timedelta(days=40),
        ai_core_util=0.1,
    )
    recent_snapshot = MetricSnapshot(
        server_id=server.id,
        card_id=card.id,
        timestamp=now - timedelta(days=1),
        ai_core_util=0.2,
    )
    db_session.add_all([old_snapshot, recent_snapshot])
    db_session.commit()

    cutoff = now - timedelta(days=30)
    deleted = purge_old_snapshots(db_session, cutoff)
    assert deleted == 1
    remaining = db_session.query(MetricSnapshot).count()
    assert remaining == 1
