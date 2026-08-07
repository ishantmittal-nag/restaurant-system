"""Display-ready pricing views for the menu."""

from app import models


class MenuPricing:
    def __init__(self, items: list[models.MenuItem]):
        self.items = items

    def get_table(self) -> list[dict]:
        return [{"name": item.name, "price": item.price} for item in self.items]
