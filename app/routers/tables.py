from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/tables", tags=["tables"])


@router.get("/", response_model=list[schemas.TableRead])
def list_tables(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_tables(db, skip=skip, limit=limit)


@router.post("/", response_model=schemas.TableRead, status_code=status.HTTP_201_CREATED)
def create_table(table: schemas.TableCreate, db: Session = Depends(get_db)):
    return crud.create_table(db, table)


@router.get("/{table_id}", response_model=schemas.TableRead)
def get_table(table_id: int, db: Session = Depends(get_db)):
    try:
        return crud.get_table(db, table_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Table not found") from exc


@router.patch("/{table_id}", response_model=schemas.TableRead)
def update_table(table_id: int, table_update: schemas.TableUpdate, db: Session = Depends(get_db)):
    try:
        db_table = crud.get_table(db, table_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Table not found") from exc
    return crud.update_table(db, db_table, table_update)


@router.delete("/{table_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_table(table_id: int, db: Session = Depends(get_db)):
    try:
        db_table = crud.get_table(db, table_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Table not found") from exc
    crud.delete_table(db, db_table)


@router.get("/{table_id}/reservations", response_model=list[schemas.ReservationRead])
def list_table_reservations(table_id: int, db: Session = Depends(get_db)):
    try:
        crud.get_table(db, table_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Table not found") from exc
    return crud.get_reservations(db, table_id=table_id, limit=1000)
