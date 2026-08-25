from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session



@router.post("/", response_model=schemas.TableRead, status_code=status.HTTP_201_CREATED)
def create_table(table: schemas.TableCreate, db: Session = Depends(get_db)):
    return crud.create_table(db, table)


@router.get("/{table_id}", response_model=schemas.TableRead)
def get_table(table_id: int, db: Session = Depends(get_db)):
    db_table = crud.get_table(db, table_id)
    if db_table is None:
        raise HTTPException(status_code=404, detail="Table not found")
    return db_table


@router.patch("/{table_id}", response_model=schemas.TableRead)
def update_table(table_id: int, table_update: schemas.TableUpdate, db: Session = Depends(get_db)):
    db_table = crud.get_table(db, table_id)
    if db_table is None:
        raise HTTPException(status_code=404, detail="Table not found")
    return crud.update_table(db, db_table, table_update)


@router.delete("/{table_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_table(table_id: int, db: Session = Depends(get_db)):
    db_table = crud.get_table(db, table_id)
    if db_table is None:
        raise HTTPException(status_code=404, detail="Table not found")
    crud.delete_table(db, db_table)


@router.get("/{table_id}/orders", response_model=list[schemas.OrderRead])
def list_orders_for_table(
    table_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    db_table = crud.get_table(db, table_id)
    if db_table is None:
        raise HTTPException(status_code=404, detail="Table not found")
    return crud.get_orders_for_table(db, table_id, skip=skip, limit=limit)
