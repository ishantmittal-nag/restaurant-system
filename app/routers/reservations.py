from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.get("/", response_model=list[schemas.ReservationRead])
def list_reservations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_reservations(db, skip=skip, limit=limit)


@router.post("/", response_model=schemas.ReservationRead, status_code=status.HTTP_201_CREATED)
def create_reservation(reservation: schemas.ReservationCreate, db: Session = Depends(get_db)):
    table = crud.get_table(db, reservation.table_id)
    if table is None:
        raise HTTPException(status_code=404, detail="Table not found")
    return crud.create_reservation(db, reservation)


@router.get("/{reservation_id}", response_model=schemas.ReservationRead)
def get_reservation(reservation_id: int, db: Session = Depends(get_db)):
    db_reservation = crud.get_reservation(db, reservation_id)
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return db_reservation


@router.patch("/{reservation_id}/status", response_model=schemas.ReservationRead)
def update_reservation_status(
    reservation_id: int,
    status_update: schemas.ReservationStatusUpdate,
    db: Session = Depends(get_db),
):
    db_reservation = crud.get_reservation(db, reservation_id)
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return crud.update_reservation_status(db, db_reservation, status_update.status)


@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reservation(reservation_id: int, db: Session = Depends(get_db)):
    db_reservation = crud.get_reservation(db, reservation_id)
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    crud.delete_reservation(db, db_reservation)


@router.get("/table/{table_id}/upcoming")
def list_upcoming_for_table(table_id: int, db: Session = Depends(get_db)):
    reservations = crud.get_reservations_for_table(db, table_id)
    result = []
    for reservation in reservations:
        table = crud.get_table(db, reservation.table_id)
        result.append(
            {
                "id": reservation.id,
                "customer_name": reservation.customer_name,
                "party_size": reservation.party_size,
                "table_number": table.number,
                "status": reservation.status,
            }
        )
    return result
