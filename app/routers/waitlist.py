from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db

router = APIRouter(prefix="/waitlist", tags=["waitlist"])


@router.get("/", response_model=list[schemas.WaitlistEntryRead])
def list_waitlist_entries(
    skip: int = 0,
    limit: int = 100,
    status_filter: models.WaitlistStatus | None = None,
    db: Session = Depends(get_db),
):
    return crud.get_waitlist_entries(db, skip=skip, limit=limit, status=status_filter)


@router.post("/", response_model=schemas.WaitlistEntryRead, status_code=status.HTTP_201_CREATED)
def create_waitlist_entry(entry: schemas.WaitlistEntryCreate, db: Session = Depends(get_db)):
    return crud.create_waitlist_entry(db, entry)


@router.get("/{entry_id}", response_model=schemas.WaitlistEntryRead)
def get_waitlist_entry(entry_id: int, db: Session = Depends(get_db)):
    db_entry = crud.get_waitlist_entry(db, entry_id)
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Waitlist entry not found")
    return db_entry


@router.patch("/{entry_id}", response_model=schemas.WaitlistEntryRead)
def update_waitlist_entry(
    entry_id: int, update: schemas.WaitlistEntryUpdate, db: Session = Depends(get_db)
):
    db_entry = crud.get_waitlist_entry(db, entry_id)
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Waitlist entry not found")
    return crud.update_waitlist_entry(db, db_entry, update)


@router.get("/{entry_id}/estimated-wait", response_model=schemas.WaitlistWaitEstimate)
def estimated_wait(entry_id: int, db: Session = Depends(get_db)):
    db_entry = crud.get_waitlist_entry(db, entry_id)
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Waitlist entry not found")
    return crud.estimate_waitlist_wait(db, db_entry)


@router.post("/{entry_id}/seat", response_model=schemas.WaitlistEntryRead)
def seat_waitlist_entry(entry_id: int, table_id: int, db: Session = Depends(get_db)):
    db_entry = crud.get_waitlist_entry(db, entry_id)
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Waitlist entry not found")
    target_table = crud.get_table(db, table_id)
    if target_table is None:
        raise HTTPException(status_code=404, detail="Table not found")
    return crud.seat_waitlist_entry(db, db_entry, target_table)


@router.post("/{entry_id}/reassign", response_model=schemas.WaitlistEntryRead)
def reassign_waitlist_entry(entry_id: int, table_id: int, db: Session = Depends(get_db)):
    db_entry = crud.get_waitlist_entry(db, entry_id)
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Waitlist entry not found")
    target_table = crud.get_table(db, table_id)
    if target_table is None:
        raise HTTPException(status_code=404, detail="Table not found")
    return crud.reassign_waitlist_entry(db, db_entry, target_table)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_waitlist_entry(entry_id: int, db: Session = Depends(get_db)):
    db_entry = crud.get_waitlist_entry(db, entry_id)
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Waitlist entry not found")
    crud.delete_waitlist_entry(db, db_entry)
