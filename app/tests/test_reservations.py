def test_create_reservation(client):
    table_id = client.post("/tables/", json={"number": 10, "capacity": 4}).json()["id"]

    response = client.post(
        "/reservations/",
        json={
            "table_id": table_id,
            "customer_name": "Alex Rivera",
            "party_size": 2,
            "reserved_for": "2026-08-20T19:00:00",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "confirmed"
    assert data["customer_name"] == "Alex Rivera"


def test_create_reservation_for_missing_table_returns_404(client):
    response = client.post(
        "/reservations/",
        json={
            "table_id": 999,
            "customer_name": "Alex Rivera",
            "party_size": 2,
            "reserved_for": "2026-08-20T19:00:00",
        },
    )
    assert response.status_code == 404


def test_update_reservation_status(client):
    table_id = client.post("/tables/", json={"number": 11, "capacity": 4}).json()["id"]
    reservation_id = client.post(
        "/reservations/",
        json={
            "table_id": table_id,
            "customer_name": "Jamie Chen",
            "party_size": 3,
            "reserved_for": "2026-08-20T20:00:00",
        },
    ).json()["id"]

    response = client.patch(f"/reservations/{reservation_id}/status", json={"status": "seated"})
    assert response.status_code == 200
    assert response.json()["status"] == "seated"


def test_list_upcoming_for_table(client):
    table_id = client.post("/tables/", json={"number": 12, "capacity": 4}).json()["id"]
    client.post(
        "/reservations/",
        json={
            "table_id": table_id,
            "customer_name": "Sam Patel",
            "party_size": 2,
            "reserved_for": "2026-08-20T18:00:00",
        },
    )

    response = client.get(f"/reservations/table/{table_id}/upcoming")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["customer_name"] == "Sam Patel"
