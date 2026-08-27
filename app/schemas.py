from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import OrderStatus, TableStatus


# ---- Table ----
class TableBase(BaseModel):
    number: int
    capacity: int
    status: TableStatus = TableStatus.available


class TableCreate(TableBase):
    pass


class TableUpdate(BaseModel):
    number: int | None = None
    capacity: int | None = None
    status: TableStatus | None = None


class TableRead(TableBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


# ---- Menu Item ----
class MenuItemBase(BaseModel):
    name: str
    description: str | None = None
    price: float = Field(gt=0)
    category: str | None = None
    is_available: bool = True


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = Field(default=None, gt=0)
    category: str | None = None
    is_available: bool | None = None


class MenuItemRead(MenuItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


# ---- Order Item ----
class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int = Field(default=1)
    notes: str | None = None


class OrderItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    menu_item_id: int
    quantity: int
    unit_price: float
    notes: str | None = None


# ---- Order ----
class OrderCreate(BaseModel):
    table_id: int
    notes: str | None = None
    items: list[OrderItemCreate] = Field(default_factory=list)


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    table_id: int
    status: OrderStatus
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemRead] = []
