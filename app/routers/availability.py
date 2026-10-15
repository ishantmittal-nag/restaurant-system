from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/availability", tags=["availability"])


@router.get("/", response_model=list[schemas.TableAvailability])
def check_availability(
    party_size: int,
    start: datetime,
    duration_minutes: int = 90,
    db: Session = Depends(get_db),
):
    tables = crud.find_available_tables(db, party_size, start, duration_minutes)
    return [
        schemas.TableAvailability(table_id=table.id, number=table.number, capacity=table.capacity)
        for table in tables
    ]
