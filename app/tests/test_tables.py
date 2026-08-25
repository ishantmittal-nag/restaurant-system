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


def test_list_orders_for_table(client):
    table_id = client.post("/tables/", json={"number": 3, "capacity": 4}).json()["id"]
    other_table_id = client.post("/tables/", json={"number": 4, "capacity": 2}).json()["id"]
    order_id = client.post("/orders/", json={"table_id": table_id, "items": []}).json()["id"]
    client.post("/orders/", json={"table_id": other_table_id, "items": []})

    response = client.get(f"/tables/{table_id}/orders")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == order_id


def test_list_orders_for_missing_table_returns_404(client):
    response = client.get("/tables/999/orders")
    assert response.status_code == 404
