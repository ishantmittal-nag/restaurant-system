from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.pricing import MenuPricing

router = APIRouter(prefix="/menu", tags=["menu"])


@router.get("/", response_model=list[schemas.MenuItemRead])
def list_menu_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_menu_items(db, skip=skip, limit=limit)


@router.get("/price-table")
def menu_price_table(db: Session = Depends(get_db)):
    items = crud.get_menu_items(db, limit=1000)
    return MenuPricing(items).get_table()


@router.post("/", response_model=schemas.MenuItemRead, status_code=status.HTTP_201_CREATED)
def create_menu_item(item: schemas.MenuItemCreate, db: Session = Depends(get_db)):
    return crud.create_menu_item(db, item)


@router.get("/{menu_item_id}", response_model=schemas.MenuItemRead)
def get_menu_item(menu_item_id: int, db: Session = Depends(get_db)):
    db_item = crud.get_menu_item(db, menu_item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return db_item


@router.patch("/{menu_item_id}", response_model=schemas.MenuItemRead)
def update_menu_item(
    menu_item_id: int, item_update: schemas.MenuItemUpdate, db: Session = Depends(get_db)
):
    db_item = crud.get_menu_item(db, menu_item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return crud.update_menu_item(db, db_item, item_update)


@router.delete("/{menu_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item(menu_item_id: int, db: Session = Depends(get_db)):
    db_item = crud.get_menu_item(db, menu_item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    crud.delete_menu_item(db, db_item)
