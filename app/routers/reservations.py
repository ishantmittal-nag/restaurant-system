from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.get("/", response_model=list[schemas.ReservationRead])
def list_reservations(
    skip: int = 0,
    limit: int = 100,
    table_id: int | None = None,
    status_filter: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    db: Session = Depends(get_db),
):
    return crud.get_reservations(
        db,
        skip=skip,
        limit=limit,
        table_id=table_id,
        status=status_filter,
        date_from=date_from,
        date_to=date_to,
    )


@router.get("/today")
def list_todays_reservations(db: Session = Depends(get_db)):
    today = datetime.now(timezone.utc).date()
    reservations = crud.get_reservations(db, limit=1000)
    results = []
    for reservation in reservations:
        if reservation.reservation_time.date() != today:
            continue
        table = crud.get_table(db, reservation.table_id)
        results.append(
            {
                "id": reservation.id,
                "table_number": table.number if table else None,
                "customer_name": reservation.customer_name,
                "party_size": reservation.party_size,
                "reservation_time": reservation.reservation_time,
                "status": reservation.status,
            }
        )
    return results


@router.get("/summary", response_model=schemas.ReservationSummary)
def reservation_summary(target_date: date, db: Session = Depends(get_db)):
    return crud.get_reservation_summary(db, target_date)


@router.get("/upcoming", response_model=list[schemas.ReservationRead])
def upcoming_reservations(within_hours: int = 24, db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    cutoff = now + timedelta(hours=within_hours)
    reservations = crud.get_reservations(db, limit=1000)
    return [
        reservation
        for reservation in reservations
        if reservation.status == "confirmed" and now <= reservation.reservation_time <= cutoff
    ]


@router.post("/", response_model=schemas.ReservationRead, status_code=status.HTTP_201_CREATED)
def create_reservation(reservation: schemas.ReservationCreate, db: Session = Depends(get_db)):
    table = crud.get_table(db, reservation.table_id)
    if table is None:
        raise HTTPException(status_code=404, detail="Table not found")
    if reservation.party_size > table.capacity:
        raise HTTPException(status_code=400, detail="Party size exceeds table capacity")
    try:
        return crud.create_reservation(db, reservation)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{reservation_id}", response_model=schemas.ReservationRead)
def get_reservation(reservation_id: int, db: Session = Depends(get_db)):
    db_reservation = crud.get_reservation(db, reservation_id)
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return db_reservation


@router.patch("/{reservation_id}", response_model=schemas.ReservationRead)
def update_reservation(
    reservation_id: int, update: schemas.ReservationUpdate, db: Session = Depends(get_db)
):
    db_reservation = crud.get_reservation(db, reservation_id)
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return crud.update_reservation(db, db_reservation, update)


@router.post("/{reservation_id}/cancel", response_model=schemas.ReservationRead)
def cancel_reservation(reservation_id: int, db: Session = Depends(get_db)):
    db_reservation = crud.get_reservation(db, reservation_id)
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return crud.cancel_reservation(db, db_reservation)


@router.post("/{reservation_id}/seat", response_model=schemas.ReservationRead)
def seat_reservation(reservation_id: int, db: Session = Depends(get_db)):
    db_reservation = crud.get_reservation(db, reservation_id)
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return crud.seat_reservation(db, db_reservation)


@router.post("/{reservation_id}/complete", response_model=schemas.ReservationRead)
def complete_reservation(reservation_id: int, db: Session = Depends(get_db)):
    db_reservation = crud.get_reservation(db, reservation_id)
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return crud.complete_reservation(db, db_reservation)


@router.post("/{reservation_id}/no-show", response_model=schemas.ReservationRead)
def mark_reservation_no_show(reservation_id: int, db: Session = Depends(get_db)):
    db_reservation = crud.get_reservation(db, reservation_id)
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return crud.mark_reservation_no_show(db, db_reservation)


@router.get("/{reservation_id}/history", response_model=list[schemas.ReservationStatusLogRead])
def reservation_history(reservation_id: int, db: Session = Depends(get_db)):
    db_reservation = crud.get_reservation(db, reservation_id)
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return crud.get_reservation_history(db, reservation_id)


@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reservation(reservation_id: int, db: Session = Depends(get_db)):
    db_reservation = crud.get_reservation(db, reservation_id)
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    crud.delete_reservation(db, db_reservation)
