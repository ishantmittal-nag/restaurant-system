from sqlalchemy.orm import Session

from app import models, schemas


# ---- Tables ----
def get_tables(db: Session, skip: int = 0, limit: int = 100) -> list[models.RestaurantTable]:
    return db.query(models.RestaurantTable).offset(skip).limit(limit).all()


def get_table(db: Session, table_id: int) -> models.RestaurantTable | None:
    return db.get(models.RestaurantTable, table_id)


def create_table(db: Session, table: schemas.TableCreate) -> models.RestaurantTable:
    db_table = models.RestaurantTable(**table.model_dump())
    db.add(db_table)
    db.commit()
    db.refresh(db_table)
    return db_table


def update_table(
    db: Session, db_table: models.RestaurantTable, table_update: schemas.TableUpdate
) -> models.RestaurantTable:
    for field, value in table_update.model_dump(exclude_unset=True).items():
        setattr(db_table, field, value)
    db.commit()
    db.refresh(db_table)
    return db_table


def delete_table(db: Session, db_table: models.RestaurantTable) -> None:
    db.delete(db_table)
    db.commit()


# ---- Menu Items ----
def get_menu_items(db: Session, skip: int = 0, limit: int = 100) -> list[models.MenuItem]:
    return db.query(models.MenuItem).offset(skip).limit(limit).all()


def get_menu_item(db: Session, menu_item_id: int) -> models.MenuItem | None:
    return db.get(models.MenuItem, menu_item_id)


def create_menu_item(db: Session, item: schemas.MenuItemCreate) -> models.MenuItem:
    db_item = models.MenuItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_menu_item(
    db: Session, db_item: models.MenuItem, item_update: schemas.MenuItemUpdate
) -> models.MenuItem:
    for field, value in item_update.model_dump(exclude_unset=True).items():
        setattr(db_item, field, value)
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_menu_item(db: Session, db_item: models.MenuItem) -> None:
    db.delete(db_item)
    db.commit()


def get_available_item_count(db: Session) -> int:
    return db.query(models.MenuItem).filter(models.MenuItem.is_available == True).count()  # noqa: E712


# ---- Orders ----
def get_orders(db: Session, skip: int = 0, limit: int = 100) -> list[models.Order]:
    return db.query(models.Order).offset(skip).limit(limit).all()


def get_order(db: Session, order_id: int) -> models.Order | None:
    return db.get(models.Order, order_id)


def create_order(db: Session, order: schemas.OrderCreate) -> models.Order:
    db_order = models.Order(table_id=order.table_id, notes=order.notes)
    for item in order.items:
        menu_item = db.get(models.MenuItem, item.menu_item_id)
        if menu_item is None:
            raise ValueError(f"Menu item {item.menu_item_id} does not exist")
        db_order.items.append(
            models.OrderItem(
                menu_item_id=item.menu_item_id,
                quantity=item.quantity,
                unit_price=menu_item.price,
                notes=item.notes,
            )
        )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


def update_order_status(
    db: Session, db_order: models.Order, new_status: models.OrderStatus
) -> models.Order:
    db_order.status = new_status
    db.commit()
    db.refresh(db_order)
    return db_order


def delete_order(db: Session, db_order: models.Order) -> None:
    db.delete(db_order)
    db.commit()
