from datetime import datetime, timedelta, timezone

from internal.audit.retention import purge_old_logs
from internal.audit.service import AuditService
from internal.db.models.alert import Alert, AlertStatus, AlertType
from internal.db.models.audit_log import AuditLog
from internal.db.models.npu_card import CardStatus, NPUCard
from internal.db.models.reservation import Reservation, ReservationMode, ReservationStatus
from internal.db.models.server import Server, ServerStatus


def create_server_with_card(db_session):
    server = Server(
        hostname="server-admin",
        ip="10.0.0.10",
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


def test_admin_whitelist_flow(admin_client, db_session):
    payload = {"ldap_id": "newuser", "ssh_login": "newuser", "display_name": "New User"}
    response = admin_client.post("/admin/whitelist", json=payload)
    assert response.status_code == 201
    assert response.json()["ldap_id"] == "newuser"

    response = admin_client.get("/admin/whitelist")
    assert response.status_code == 200
    users = {user["ldap_id"]: user for user in response.json()["users"]}
    assert "newuser" in users

    response = admin_client.delete("/admin/whitelist/newuser")
    assert response.status_code == 200
    assert response.json()["status"] == "disabled"


def test_admin_server_add_and_discover(admin_client, db_session):
    response = admin_client.post(
        "/servers",
        json={"ip": "10.0.0.20", "access_account": "root"},
    )
    assert response.status_code == 201
    server_id = response.json()["id"]

    response = admin_client.post(f"/servers/{server_id}/discover")
    assert response.status_code == 200
    payload = response.json()
    assert payload["card_count"] in (2, 8)

    cards = db_session.query(NPUCard).filter(NPUCard.server_id == server_id).all()
    assert len(cards) == payload["card_count"]


def test_force_release_reservation(admin_client, db_session, now, test_user):
    server, card = create_server_with_card(db_session)

    reservation = Reservation(
        user_id=test_user.id,
        server_id=server.id,
        card_id=card.id,
        mode=ReservationMode.carpool,
        start_time=now - timedelta(minutes=5),
        end_time=now + timedelta(minutes=30),
        status=ReservationStatus.active,
    )
    db_session.add(reservation)
    db_session.commit()

    response = admin_client.post(f"/reservations/{reservation.id}/force-release")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "forced_release"

    refreshed = db_session.query(Reservation).filter(Reservation.id == reservation.id).one()
    assert refreshed.status == ReservationStatus.forced_release
    end_time = refreshed.end_time
    if end_time.tzinfo is None:
        end_time = end_time.replace(tzinfo=timezone.utc)
    assert end_time <= datetime.now(timezone.utc)


def test_alert_resolve(admin_client, db_session, now):
    server, card = create_server_with_card(db_session)

    alert = Alert(
        server_id=server.id,
        card_id=card.id,
        type=AlertType.no_reservation_high_load,
        status=AlertStatus.open,
        detected_at=now,
    )
    db_session.add(alert)
    db_session.commit()

    response = admin_client.post(f"/alerts/{alert.id}/resolve")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "resolved"


def test_audit_middleware_logs_action(admin_client, db_session, admin_user):
    response = admin_client.post(
        "/servers",
        json={"ip": "10.0.0.30", "access_account": "root"},
    )
    assert response.status_code == 201

    logs = db_session.query(AuditLog).all()
    assert len(logs) == 1
    assert logs[0].actor_user_id == admin_user.id


def test_audit_list_and_export(admin_client, db_session, admin_user, now):
    service = AuditService(db_session)
    service.log_action(
        actor_user_id=admin_user.id,
        action_type="TEST",
        target_type="servers",
        target_id="srv-1",
        metadata={"note": "test"},
        timestamp=now,
    )
    db_session.commit()

    response = admin_client.get("/audit-logs")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["logs"]) == 1

    response = admin_client.get("/audit-logs/export", params={"format": "csv"})
    assert response.status_code == 200
    assert "actor_user_id" in response.text


def test_audit_retention_purges_old_logs(db_session, admin_user, now):
    service = AuditService(db_session)
    old_timestamp = now - timedelta(days=40)
    service.log_action(
        actor_user_id=admin_user.id,
        action_type="OLD",
        timestamp=old_timestamp,
    )
    service.log_action(
        actor_user_id=admin_user.id,
        action_type="NEW",
        timestamp=now,
    )
    db_session.commit()

    cutoff = now - timedelta(days=30)
    deleted = purge_old_logs(db_session, cutoff)
    assert deleted == 1
    remaining = db_session.query(AuditLog).count()
    assert remaining == 1
