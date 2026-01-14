
def test_reservation_rate_limit(client):
    response = client.get("/reservations")
    assert response.status_code == 200

    response = client.get("/reservations")
    assert response.status_code == 200

    response = client.get("/reservations")
    assert response.status_code == 429
    payload = response.json()
    assert payload["code"] == "rate_limited"
