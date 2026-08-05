from datetime import datetime, timedelta, timezone


def _future_time(hours_from_now: int = 2) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=hours_from_now)).isoformat()


def test_create_and_get_reservation(client):
    table_id = client.post("/tables/", json={"number": 10, "capacity": 4}).json()["id"]

    response = client.post(
        "/reservations/",
        json={
            "table_id": table_id,
            "customer_name": "Alex Rivera",
            "party_size": 2,
            "reservation_time": _future_time(),
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "confirmed"
    assert data["customer_name"] == "Alex Rivera"
    assert data["duration_minutes"] == 90

    reservation_id = data["id"]
    response = client.get(f"/reservations/{reservation_id}")
    assert response.status_code == 200
    assert response.json()["id"] == reservation_id


def test_reservation_for_missing_table_returns_404(client):
    response = client.post(
        "/reservations/",
        json={
            "table_id": 999,
            "customer_name": "Nobody",
            "party_size": 2,
            "reservation_time": _future_time(),
        },
    )
    assert response.status_code == 404


def test_reservation_exceeding_table_capacity_is_rejected(client):
    table_id = client.post("/tables/", json={"number": 12, "capacity": 2}).json()["id"]

    response = client.post(
        "/reservations/",
        json={
            "table_id": table_id,
            "customer_name": "Large Party",
            "party_size": 6,
            "reservation_time": _future_time(),
        },
    )
    assert response.status_code == 400


def test_second_reservation_at_same_time_is_rejected(client):
    table_id = client.post("/tables/", json={"number": 11, "capacity": 4}).json()["id"]
    reservation_time = _future_time()

    first = client.post(
        "/reservations/",
        json={
            "table_id": table_id,
            "customer_name": "Priya Nair",
            "party_size": 2,
            "reservation_time": reservation_time,
        },
    )
    assert first.status_code == 201

    second = client.post(
        "/reservations/",
        json={
            "table_id": table_id,
            "customer_name": "Sam Lee",
            "party_size": 2,
            "reservation_time": reservation_time,
        },
    )
    assert second.status_code == 400


def test_update_reservation_party_size(client):
    table_id = client.post("/tables/", json={"number": 12, "capacity": 6}).json()["id"]
    reservation_id = client.post(
        "/reservations/",
        json={
            "table_id": table_id,
            "customer_name": "Priya Nair",
            "party_size": 2,
            "reservation_time": _future_time(),
        },
    ).json()["id"]

    response = client.patch(f"/reservations/{reservation_id}", json={"party_size": 4})
    assert response.status_code == 200
    assert response.json()["party_size"] == 4


def test_cancel_reservation(client):
    table_id = client.post("/tables/", json={"number": 13, "capacity": 2}).json()["id"]
    reservation_id = client.post(
        "/reservations/",
        json={
            "table_id": table_id,
            "customer_name": "Sam Lee",
            "party_size": 2,
            "reservation_time": _future_time(),
        },
    ).json()["id"]

    response = client.post(f"/reservations/{reservation_id}/cancel")
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


def test_list_reservations_filtered_by_table(client):
    table_id = client.post("/tables/", json={"number": 14, "capacity": 2}).json()["id"]
    other_table_id = client.post("/tables/", json={"number": 15, "capacity": 2}).json()["id"]
    client.post(
        "/reservations/",
        json={
            "table_id": table_id,
            "customer_name": "Jordan Kim",
            "party_size": 2,
            "reservation_time": _future_time(),
        },
    )
    client.post(
        "/reservations/",
        json={
            "table_id": other_table_id,
            "customer_name": "Morgan Diaz",
            "party_size": 2,
            "reservation_time": _future_time(),
        },
    )

    response = client.get("/reservations/", params={"table_id": table_id})
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["table_id"] == table_id


def test_list_reservations_filtered_by_date_range(client):
    table_id = client.post("/tables/", json={"number": 17, "capacity": 2}).json()["id"]
    near = client.post(
        "/reservations/",
        json={
            "table_id": table_id,
            "customer_name": "Near Term",
            "party_size": 2,
            "reservation_time": _future_time(hours_from_now=2),
        },
    ).json()
    far = client.post(
        "/reservations/",
        json={
            "table_id": table_id,
            "customer_name": "Far Term",
            "party_size": 2,
            "reservation_time": _future_time(hours_from_now=240),
        },
    ).json()

    near_date = datetime.fromisoformat(near["reservation_time"]).date().isoformat()
    response = client.get("/reservations/", params={"date_from": near_date, "date_to": near_date})
    assert response.status_code == 200
    ids = [r["id"] for r in response.json()]
    assert near["id"] in ids
    assert far["id"] not in ids


def test_reservation_summary(client):
    table_id = client.post("/tables/", json={"number": 16, "capacity": 4}).json()["id"]
    reservation_time = _future_time(hours_from_now=5)
    client.post(
        "/reservations/",
        json={
            "table_id": table_id,
            "customer_name": "Taylor Wong",
            "party_size": 3,
            "reservation_time": reservation_time,
        },
    )

    target_date = datetime.fromisoformat(reservation_time).date().isoformat()
    response = client.get("/reservations/summary", params={"target_date": target_date})
    assert response.status_code == 200
    data = response.json()
    assert data["total_reservations"] == 1
    assert data["total_covers"] == 3
