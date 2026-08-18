def test_create_order_with_items(client):
    table_id = client.post("/tables/", json={"number": 5, "capacity": 2}).json()["id"]
    menu_item_id = client.post(
        "/menu/", json={"name": "Margherita Pizza", "price": 9.5, "category": "Pizza"}
    ).json()["id"]

    response = client.post(
        "/orders/",
        json={
            "table_id": table_id,
            "items": [{"menu_item_id": menu_item_id, "quantity": 2}],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
    assert len(data["items"]) == 1
    assert data["items"][0]["unit_price"] == 9.5
    assert data["items"][0]["quantity"] == 2


def test_create_order_for_missing_table_returns_404(client):
    response = client.post("/orders/", json={"table_id": 999, "items": []})
    assert response.status_code == 404


def test_update_order_status(client):
    table_id = client.post("/tables/", json={"number": 6, "capacity": 4}).json()["id"]
    order_id = client.post("/orders/", json={"table_id": table_id, "items": []}).json()["id"]

    response = client.patch(f"/orders/{order_id}/status", json={"status": "in_progress"})
    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


def test_order_summary(client):
    table_id = client.post("/tables/", json={"number": 7, "capacity": 2}).json()["id"]
    menu_item_id = client.post(
        "/menu/", json={"name": "Espresso", "price": 3.0, "category": "Drinks"}
    ).json()["id"]
    order_id = client.post(
        "/orders/",
        json={
            "table_id": table_id,
            "items": [{"menu_item_id": menu_item_id, "quantity": 2}],
        },
    ).json()["id"]

    response = client.get(f"/orders/{order_id}/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 6.0
    assert data["category_totals"]["Drinks"] == 6.0
