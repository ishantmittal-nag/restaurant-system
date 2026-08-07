"""Order checkout totals: subtotal, discount, tip."""

from app import models

DISCOUNT_CODES = {"WELCOME10": 0.10, "VIP20": 0.20}


def calculate_order_total(
    order: models.Order, discount_code: str | None = None, tip_percent: float = 0.0
) -> dict:
    subtotal = sum(item.unit_price * item.quantity for item in order.items)
    discount_rate = DISCOUNT_CODES.get(discount_code, 0.0) if discount_code else 0.0
    discount_amount = subtotal * discount_rate
    tip_amount = subtotal * (tip_percent / 100)
    total = subtotal - discount_amount + tip_amount
    return {
        "subtotal": subtotal,
        "discount_amount": discount_amount,
        "tip_amount": tip_amount,
        "total": total,
    }
