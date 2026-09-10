from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import OrderStatus, PurchaseOrderStatus, StockMovementType, TableStatus


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


# ---- Supplier ----
class SupplierBase(BaseModel):
    name: str
    contact_email: str | None = None
    is_active: bool = True


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: str | None = None
    contact_email: str | None = None
    is_active: bool | None = None


class SupplierRead(SupplierBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


# ---- Ingredient ----
class IngredientBase(BaseModel):
    name: str
    unit: str
    quantity_on_hand: float = 0
    reorder_threshold: float = 0
    unit_cost: float = 0
    supplier_id: int | None = None


class IngredientCreate(IngredientBase):
    pass


class IngredientUpdate(BaseModel):
    name: str | None = None
    unit: str | None = None
    quantity_on_hand: float | None = None
    reorder_threshold: float | None = None
    unit_cost: float | None = None
    supplier_id: int | None = None


class IngredientRead(IngredientBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


# ---- Stock Movement ----
class StockMovementCreate(BaseModel):
    ingredient_id: int
    movement_type: StockMovementType
    quantity: float
    note: str | None = None


class StockMovementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ingredient_id: int
    movement_type: StockMovementType
    quantity: float
    note: str | None = None
    created_at: datetime


class RecipeIngredientUsage(BaseModel):
    ingredient_id: int
    quantity_per_item: float


class BulkStockAdjustment(BaseModel):
    adjustments: dict[int, float]


# ---- Purchase Orders ----
class PurchaseOrderItemCreate(BaseModel):
    ingredient_id: int
    quantity: float
    unit_cost: float


class PurchaseOrderItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ingredient_id: int
    quantity: float
    unit_cost: float


class PurchaseOrderCreate(BaseModel):
    supplier_id: int
    items: list[PurchaseOrderItemCreate] = []


class PurchaseOrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    supplier_id: int
    status: PurchaseOrderStatus
    created_at: datetime
    items: list[PurchaseOrderItemRead] = []


# ---- Recipes ----
class RecipeCreate(BaseModel):
    menu_item_id: int
    ingredient_id: int
    quantity_per_item: float


class RecipeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    menu_item_id: int
    ingredient_id: int
    quantity_per_item: float


class DebugReportRequest(BaseModel):
    report_name: str
    admin_password: str
