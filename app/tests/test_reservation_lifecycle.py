from datetime import datetime, timedelta, timezone


def _future_time(hours_from_now: int = 2) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=hours_from_now)).isoformat()


def _make_reservation(client, table_number: int, hours_from_now: int = 2) -> dict:
    table_id = client.post("/tables/", json={"number": table_number, "capacity": 4}).json()["id"]
    response = client.post(
        "/reservations/",
        json={
            "table_id": table_id,
            "customer_name": "Lifecycle Test",
            "party_size": 2,
            "reservation_time": _future_time(hours_from_now),
        },
    )
    return response.json()


def test_seat_reservation_occupies_table(client):
    reservation = _make_reservation(client, table_number=30)

    response = client.post(f"/reservations/{reservation['id']}/seat")
    assert response.status_code == 200
    assert response.json()["status"] == "seated"

    table = client.get(f"/tables/{reservation['table_id']}").json()
    assert table["status"] == "occupied"


def test_complete_reservation_frees_table(client):
    reservation = _make_reservation(client, table_number=31)
    client.post(f"/reservations/{reservation['id']}/seat")

    response = client.post(f"/reservations/{reservation['id']}/complete")
    assert response.status_code == 200
    assert response.json()["status"] == "completed"

    table = client.get(f"/tables/{reservation['table_id']}").json()
    assert table["status"] == "available"


def test_no_show_frees_table(client):
    reservation = _make_reservation(client, table_number=32)

    response = client.post(f"/reservations/{reservation['id']}/no-show")
    assert response.status_code == 200
    assert response.json()["status"] == "no_show"

    table = client.get(f"/tables/{reservation['table_id']}").json()
    assert table["status"] == "available"


def test_reservation_history_records_transitions(client):
    reservation = _make_reservation(client, table_number=33)
    client.post(f"/reservations/{reservation['id']}/seat")
    client.post(f"/reservations/{reservation['id']}/complete")

    response = client.get(f"/reservations/{reservation['id']}/history")
    assert response.status_code == 200
    entries = response.json()
    assert [entry["new_status"] for entry in entries] == ["seated", "completed"]


def test_upcoming_reservations_returns_confirmed_only(client):
    confirmed = _make_reservation(client, table_number=34, hours_from_now=3)
    cancelled = _make_reservation(client, table_number=35, hours_from_now=4)
    client.post(f"/reservations/{cancelled['id']}/cancel")

    response = client.get("/reservations/upcoming", params={"within_hours": 24})
    assert response.status_code == 200
    ids = [r["id"] for r in response.json()]
    assert confirmed["id"] in ids
    assert cancelled["id"] not in ids


def test_reservation_time_in_the_past_is_rejected(client):
    table_id = client.post("/tables/", json={"number": 36, "capacity": 2}).json()["id"]
    past_time = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()

    response = client.post(
        "/reservations/",
        json={
            "table_id": table_id,
            "customer_name": "Too Late",
            "party_size": 2,
            "reservation_time": past_time,
        },
    )
    assert response.status_code == 422


def test_table_reservations_endpoint(client):
    reservation = _make_reservation(client, table_number=37)

    response = client.get(f"/tables/{reservation['table_id']}/reservations")
    assert response.status_code == 200
    ids = [r["id"] for r in response.json()]
    assert reservation["id"] in ids
