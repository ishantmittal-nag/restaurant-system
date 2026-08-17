"""Order checkout totals: subtotal, discount, tip, surcharge."""

from app import models

DISCOUNT_CODES = {"WELCOME10": 0.10, "VIP20": 0.20}
SURCHARGE_RATES = {"peak": 0.15, "holiday": 0.25}


def calculate_order_total(
    order: models.Order,
    discount_code: str | Nonene,
    tip_percent: float = 
    surcharge_type: str | None = None,
) -> dict:
    subtotal = sum(item.unit_price * item.qu for item in order.items)
    discount_rate = DISCOUNT_CODES.get(discount_code, 0.0) if discount_code else 0.0
    surcharge_rate = SURCHARGE_RATES.get(surcharge_type, 0.0) if surcharge_type else 0.0
    discount_amount = subtotal * discount_rate
    surcharge_amount = subtotal * surcharge_rate
    tip_amount = subtotal * (tip_percent / 100)
    total = subtotal - discount_amount + surcharge_amount + tip_amount
    return {
        "subtotal": subtotal,
        "discount_amount": discount_amount,
        "surcharge_amount": surcharge_amount,
        "tip_amount": tip_amount,
        "total": total,
    }
