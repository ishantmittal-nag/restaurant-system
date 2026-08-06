def test_create_and_get_waitlist_entry(client):
    response = client.post(
        "/waitlist/", json={"customer_name": "Casey Fox", "party_size": 3, "phone_number": "555-0100"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "waiting"

    entry_id = data["id"]
    response = client.get(f"/waitlist/{entry_id}")
    assert response.status_code == 200
    assert response.json()["id"] == entry_id


def test_list_waitlist_entries_filtered_by_status(client):
    client.post("/waitlist/", json={"customer_name": "Riley Stone", "party_size": 2})
    seated = client.post("/waitlist/", json={"customer_name": "Drew Park", "party_size": 2}).json()
    client.patch(f"/waitlist/{seated['id']}", json={"status": "seated"})

    response = client.get("/waitlist/", params={"status_filter": "waiting"})
    assert response.status_code == 200
    names = [entry["customer_name"] for entry in response.json()]
    assert "Riley Stone" in names
    assert "Drew Park" not in names


def test_update_waitlist_status(client):
    entry_id = client.post(
        "/waitlist/", json={"customer_name": "Jamie Cruz", "party_size": 4}
    ).json()["id"]

    response = client.patch(f"/waitlist/{entry_id}", json={"status": "notified"})
    assert response.status_code == 200
    assert response.json()["status"] == "notified"


def test_delete_waitlist_entry(client):
    entry_id = client.post(
        "/waitlist/", json={"customer_name": "Morgan Lee", "party_size": 2}
    ).json()["id"]

    response = client.delete(f"/waitlist/{entry_id}")
    assert response.status_code == 204

    response = client.get(f"/waitlist/{entry_id}")
    assert response.status_code == 404


def test_estimated_wait_reflects_queue_position(client):
    client.post("/waitlist/", json={"customer_name": "First InLine", "party_size": 2})
    second = client.post(
        "/waitlist/", json={"customer_name": "Second InLine", "party_size": 2}
    ).json()

    response = client.get(f"/waitlist/{second['id']}/estimated-wait")
    assert response.status_code == 200
    data = response.json()
    assert data["position"] == 2
    assert data["estimated_wait_minutes"] == 30


def test_seat_waitlist_entry_occupies_table(client):
    table_id = client.post("/tables/", json={"number": 40, "capacity": 4}).json()["id"]
    entry_id = client.post(
        "/waitlist/", json={"customer_name": "Avery Quinn", "party_size": 2}
    ).json()["id"]

    response = client.post(f"/waitlist/{entry_id}/seat", params={"table_id": table_id})
    assert response.status_code == 200
    assert response.json()["status"] == "seated"

    table = client.get(f"/tables/{table_id}").json()
    assert table["status"] == "occupied"
