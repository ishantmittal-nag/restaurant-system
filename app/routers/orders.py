from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import billing, crud, schemas
from app.database import get_db

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/", response_model=list[schemas.OrderRead])
def list_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_orders(db, skip=skip, limit=limit)


@router.post("/", response_model=schemas.OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    table = crud.get_table(db, order.table_id)
    if table is None:
        raise HTTPException(status_code=404, detail="Table not found")
    try:
        return crud.create_order(db, order)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{order_id}", response_model=schemas.OrderRead)
def get_order(order_id: int, db: Session = Depends(get_db)):
    db_order = crud.get_order(db, order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order


@router.patch("/{order_id}/status", response_model=schemas.OrderRead)
def update_order_status(
    order_id: int, status_update: schemas.OrderStatusUpdate, db: Session = Depends(get_db)
):
    db_order = crud.get_order(db, order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return crud.update_order_status(db, db_order, status_update.status)


@router.get("/{order_id}/checkout")
def checkout_order(
    order_id: int,
    discount_code: str | None = None,
    tip_percent: float = 0.0,
    surcharge_type: str | None = None,
    db: Session = Depends(get_db),
):
    db_order = crud.get_order(db, order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return billing.calculate_order_total(db_order, discount_code, tip_percent, surcharge_type)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    db_order = crud.get_order(db, order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    crud.delete_order(db, db_order)
