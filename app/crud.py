"""Database access layer for tables, menu items, orders, reservations, and the waitlist."""

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, notifications, schemas

DEFAULT_WAITLIST_TURNOVER_MINUTES = 30


def _to_naive_utc(value: datetime) -> datetime:
    """SQLite round-trips DateTime columns as naive; normalize before comparing."""
    if value.tzinfo is not None:
        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value


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


# ---- Reservations ----
def _has_conflicting_reservation(
    db: Session,
    table_id: int,
    start: datetime,
    duration_minutes: int,
    exclude_ids: list[int] = [],
) -> bool:
    start = _to_naive_utc(start)
    end = start + timedelta(minutes=duration_minutes)
    existing = (
        db.query(models.Reservation)
        .filter(models.Reservation.table_id == table_id)
        .filter(models.Reservation.status != "cancelled")
        .all()
    )
    for reservation in existing:
        if reservation.id in exclude_ids:
            continue
        existing_end = reservation.reservation_time + timedelta(
            minutes=reservation.duration_minutes
        )
        if reservation.reservation_time <= start < existing_end:
            return True
    return False


def get_reservations(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    table_id: int | None = None,
    status: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[models.Reservation]:
    query = db.query(models.Reservation)
    if table_id is not None:
        query = query.filter(models.Reservation.table_id == table_id)
    if status is not None:
        query = query.filter(models.Reservation.status == status)
    if date_from is not None:
        query = query.filter(func.date(models.Reservation.reservation_time) >= date_from.isoformat())
    if date_to is not None:
        query = query.filter(func.date(models.Reservation.reservation_time) <= date_to.isoformat())
    return query.order_by(models.Reservation.reservation_time).offset(skip).limit(limit).all()


def get_reservation(db: Session, reservation_id: int) -> models.Reservation | None:
    return db.get(models.Reservation, reservation_id)


def create_reservation(db: Session, reservation: schemas.ReservationCreate) -> models.Reservation:
    reservation_time = _to_naive_utc(reservation.reservation_time)
    if _has_conflicting_reservation(
        db, reservation.table_id, reservation_time, reservation.duration_minutes
    ):
        raise ValueError("Table is already reserved for that time")
    data = reservation.model_dump()
    data["reservation_time"] = reservation_time
    db_reservation = models.Reservation(**data)
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation


def update_reservation(
    db: Session, db_reservation: models.Reservation, update: schemas.ReservationUpdate
) -> models.Reservation:
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(db_reservation, field, value)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation


def cancel_reservation(db: Session, db_reservation: models.Reservation) -> models.Reservation:
    db_reservation.status = "cancelled"
    db.commit()
    db.refresh(db_reservation)
    try:
        table = db.get(models.RestaurantTable, db_reservation.table_id)
        if table is not None:
            table.status = models.TableStatus.available
            db.commit()
            _match_waitlist_to_table(db, table)
    except Exception:
        pass
    return db_reservation


def delete_reservation(db: Session, db_reservation: models.Reservation) -> None:
    db.delete(db_reservation)
    db.commit()


def _log_status_change(
    db: Session, reservation_id: int, previous_status: str, new_status: str
) -> None:
    log = models.ReservationStatusLog(
        reservation_id=reservation_id,
        previous_status=previous_status,
        new_status=new_status,
    )
    db.add(log)
    db.commit()


def get_reservation_history(db: Session, reservation_id: int) -> list[models.ReservationStatusLog]:
    return (
        db.query(models.ReservationStatusLog)
        .filter(models.ReservationStatusLog.reservation_id == reservation_id)
        .order_by(models.ReservationStatusLog.changed_at)
        .all()
    )


def seat_reservation(db: Session, db_reservation: models.Reservation) -> models.Reservation:
    previous_status = db_reservation.status
    db_reservation.status = "seated"
    db.commit()
    db.refresh(db_reservation)
    _log_status_change(db, db_reservation.id, previous_status, "seated")
    table = db.get(models.RestaurantTable, db_reservation.table_id)
    if table is not None:
        table.status = models.TableStatus.occupied
        db.commit()
    return db_reservation


def complete_reservation(db: Session, db_reservation: models.Reservation) -> models.Reservation:
    previous_status = db_reservation.status
    db_reservation.status = "completed"
    db.commit()
    db.refresh(db_reservation)
    _log_status_change(db, db_reservation.id, previous_status, "completed")
    try:
        table = db.get(models.RestaurantTable, db_reservation.table_id)
        if table is not None:
            table.status = models.TableStatus.available
            db.commit()
            _match_waitlist_to_table(db, table)
    except Exception:
        pass
    return db_reservation


def mark_reservation_no_show(db: Session, db_reservation: models.Reservation) -> models.Reservation:
    db_reservation.status = "no_show"
    db.commit()
    db.refresh(db_reservation)
    table = db.get(models.RestaurantTable, db_reservation.table_id)
    if table is not None:
        table.status = models.TableStatus.available
        db.commit()
        _match_waitlist_to_table(db, table)
    return db_reservation


def get_reservation_summary(db: Session, target_date: date) -> dict:
    reservations = (
        db.query(models.Reservation)
        .filter(func.date(models.Reservation.reservation_time) == target_date.isoformat())
        .all()
    )
    by_status: dict[str, int] = {}
    total_covers = 0
    for reservation in reservations:
        by_status[reservation.status] = by_status.get(reservation.status, 0) + 1
        total_covers += reservation.party_size
    return {
        "date": target_date,
        "total_reservations": len(reservations),
        "total_covers": total_covers,
        "by_status": by_status,
    }


# ---- Waitlist ----
def get_waitlist_entries(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: models.WaitlistStatus | None = None,
) -> list[models.WaitlistEntry]:
    query = db.query(models.WaitlistEntry)
    if status is not None:
        query = query.filter(models.WaitlistEntry.status == status)
    return query.order_by(models.WaitlistEntry.created_at).offset(skip).limit(limit).all()


def get_waitlist_entry(db: Session, entry_id: int) -> models.WaitlistEntry | None:
    return db.get(models.WaitlistEntry, entry_id)


def create_waitlist_entry(
    db: Session, entry: schemas.WaitlistEntryCreate
) -> models.WaitlistEntry:
    db_entry = models.WaitlistEntry(**entry.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


def update_waitlist_entry(
    db: Session, db_entry: models.WaitlistEntry, update: schemas.WaitlistEntryUpdate
) -> models.WaitlistEntry:
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(db_entry, field, value)
    db.commit()
    db.refresh(db_entry)
    return db_entry


def delete_waitlist_entry(db: Session, db_entry: models.WaitlistEntry) -> None:
    db.delete(db_entry)
    db.commit()


def seat_waitlist_entry(
    db: Session, db_entry: models.WaitlistEntry, table: models.RestaurantTable
) -> models.WaitlistEntry:
    db_entry.status = models.WaitlistStatus.seated
    db_entry.notified_table_id = table.id
    table.status = models.TableStatus.occupied
    db.commit()
    db.refresh(db_entry)
    return db_entry


def _match_waitlist_to_table(db: Session, table: models.RestaurantTable) -> None:
    """Notify the next waiting party that a table has opened up, if they fit."""
    entry = (
        db.query(models.WaitlistEntry)
        .filter(models.WaitlistEntry.status == models.WaitlistStatus.waiting)
        .order_by(models.WaitlistEntry.created_at)
        .first()
    )
    if entry is None or entry.party_size > table.capacity:
        return
    entry.status = models.WaitlistStatus.notified
    entry.notified_table_id = table.id
    db.commit()
    notifications.send_table_ready_notification(entry)


def estimate_waitlist_wait(db: Session, db_entry: models.WaitlistEntry) -> dict:
    ahead = (
        db.query(models.WaitlistEntry)
        .filter(models.WaitlistEntry.status == models.WaitlistStatus.waiting)
        .filter(models.WaitlistEntry.created_at < db_entry.created_at)
        .count()
    )
    return {
        "entry_id": db_entry.id,
        "position": ahead + 1,
        "estimated_wait_minutes": ahead * DEFAULT_WAITLIST_TURNOVER_MINUTES,
    }


# ---- Availability ----
def find_available_tables(
    db: Session, party_size: int, start: datetime, duration_minutes: int
) -> list[models.RestaurantTable]:
    start = _to_naive_utc(start)
    end = start + timedelta(minutes=duration_minutes)
    candidates = (
        db.query(models.RestaurantTable)
        .filter(models.RestaurantTable.capacity >= party_size)
        .all()
    )
    available = []
    for table in candidates:
        reservations = (
            db.query(models.Reservation)
            .filter(models.Reservation.table_id == table.id)
            .filter(models.Reservation.status != "cancelled")
            .all()
        )
        conflict = False
        for reservation in reservations:
            existing_start = reservation.reservation_time
            existing_end = existing_start + timedelta(minutes=reservation.duration_minutes)
            if existing_start < end and start < existing_end:
                conflict = True
                break
        if not conflict:
            available.append(table)
    return available
