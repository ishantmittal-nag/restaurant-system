from datetime import datetime, timedelta, timezone


def _future_time(hours_from_now: int = 2) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=hours_from_now)).isoformat()


def test_table_available_when_no_reservations(client):
    client.post("/tables/", json={"number": 20, "capacity": 4})

    response = client.get(
        "/availability/",
        params={"party_size": 2, "start": _future_time(), "duration_minutes": 60},
    )
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_table_excluded_when_capacity_too_small(client):
    client.post("/tables/", json={"number": 21, "capacity": 2})

    response = client.get(
        "/availability/",
        params={"party_size": 6, "start": _future_time(), "duration_minutes": 60},
    )
    assert response.status_code == 200
    assert response.json() == []


def test_table_excluded_when_reservation_overlaps(client):
    table_id = client.post("/tables/", json={"number": 22, "capacity": 4}).json()["id"]
    start = _future_time()
    client.post(
        "/reservations/",
        json={
            "table_id": table_id,
            "customer_name": "Devon Ray",
            "party_size": 2,
            "reservation_time": start,
            "duration_minutes": 60,
        },
    )

    response = client.get(
        "/availability/", params={"party_size": 2, "start": start, "duration_minutes": 60}
    )
    assert response.status_code == 200
    assert response.json() == []
