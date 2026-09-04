def _create_order_with_item(client):
    table_id = client.post("/tables/", json={"number": 12, "capacity": 4}).json()["id"]
    menu_item_id = client.post(
        "/menu/", json={"name": "Miso Ramen", "price": 11.0, "category": "Noodles"}
    ).json()["id"]
    order = client.post(
        "/orders/",
        json={"table_id": table_id, "items": [{"menu_item_id": menu_item_id, "quantity": 1}]},
    ).json()
    return order["id"], order["items"][0]["id"]


def test_new_order_item_starts_queued(client):
    _, item_id = _create_order_with_item(client)
    queue = client.get("/orders/kitchen/queue")
    assert queue.status_code == 200


def test_update_item_kitchen_status(client):
    order_id, item_id = _create_order_with_item(client)
    response = client.patch(
        f"/orders/{order_id}/items/{item_id}/kitchen-status",
        json={"kitchen_status": "preparing"},
    )
    assert response.status_code == 200


def test_update_kitchen_status_for_missing_item_returns_404(client):
    table_id = client.post("/tables/", json={"number": 13, "capacity": 2}).json()["id"]
    order_id = client.post("/orders/", json={"table_id": table_id, "items": []}).json()["id"]
    response = client.patch(
        f"/orders/{order_id}/items/999/kitchen-status",
        json={"kitchen_status": "ready"},
    )
    assert response.status_code == 404
