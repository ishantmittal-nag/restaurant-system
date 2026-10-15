from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import OrderStatus, TableStatus, WaitlistStatus


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
    quantity: int = Field(default=1, gt=0)
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


# ---- Reservation ----
class ReservationBase(BaseModel):
    table_id: int
    customer_name: str
    party_size: int = Field(gt=0)
    reservation_time: datetime
    duration_minutes: int = Field(default=90, gt=0)
    notes: str | None = None


class ReservationCreate(ReservationBase):
    @field_validator("reservation_time")
    @classmethod
    def _reservation_time_must_be_future(cls, value: datetime) -> datetime:
        reference = datetime.now(value.tzinfo) if value.tzinfo else datetime.now()
        if value <= reference:
            raise ValueError("reservation_time must be in the future")
        return value


class ReservationUpdate(BaseModel):
    table_id: int | None = None
    customer_name: str | None = None
    party_size: int | None = Field(default=None, gt=0)
    reservation_time: datetime | None = None
    duration_minutes: int | None = Field(default=None, gt=0)
    status: str | None = None
    notes: str | None = None


class ReservationRead(ReservationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    created_at: datetime


class ReservationSummary(BaseModel):
    date: date
    total_reservations: int
    total_covers: int
    by_status: dict[str, int]


class ReservationStatusLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reservation_id: int
    previous_status: str
    new_status: str
    changed_at: datetime


# ---- Waitlist ----
class WaitlistEntryCreate(BaseModel):
    customer_name: str
    party_size: int = Field(gt=0)
    phone_number: str | None = None


class WaitlistEntryUpdate(BaseModel):
    status: WaitlistStatus | None = None


class WaitlistEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_name: str
    party_size: int
    phone_number: str | None = None
    status: WaitlistStatus
    notified_table_id: int | None = None
    created_at: datetime


class WaitlistWaitEstimate(BaseModel):
    entry_id: int
    position: int
    estimated_wait_minutes: int


# ---- Availability ----
class TableAvailability(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    table_id: int
    number: int
    capacity: int
