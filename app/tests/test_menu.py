def test_search_menu_items(client):
    client.post("/menu/", json={"name": "Margherita Pizza", "price": 9.5, "category": "Pizza"})
    client.post("/menu/", json={"name": "Espresso", "price": 3.0, "category": "Drinks"})

    response = client.get("/menu/search/", params={"query": "pizza"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Margherita Pizza"


def test_bulk_update_availability(client):
    item_id = client.post(
        "/menu/", json={"name": "Espresso", "price": 3.0, "category": "Drinks"}
    ).json()["id"]

    response = client.post(
        "/menu/bulk-availability", json={"item_ids": [item_id], "is_available": False}
    )
    assert response.status_code == 200
    assert response.json()[0]["is_available"] is False
