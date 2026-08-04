def test_create_and_get_table(client):
    response = client.post("/tables/", json={"number": 1, "capacity": 4})
    assert response.status_code == 201
    data = response.json()
    assert data["number"] == 1
    assert data["status"] == "available"

    table_id = data["id"]
    response = client.get(f"/tables/{table_id}")
    assert response.status_code == 200
    assert response.json()["id"] == table_id


def test_get_missing_table_returns_404(client):
    response = client.get("/tables/999")
    assert response.status_code == 404


def test_update_table_status(client):
    created = client.post("/tables/", json={"number": 2, "capacity": 2}).json()

    response = client.patch(f"/tables/{created['id']}", json={"status": "occupied"})
    assert response.status_code == 200
    assert response.json()["status"] == "occupied"
