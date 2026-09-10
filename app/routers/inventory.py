from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/inventory", tags=["inventory"])


# ---- Suppliers ----
@router.get("/suppliers", response_model=list[schemas.SupplierRead])
def list_suppliers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_suppliers(db, skip=skip, limit=limit)


@router.post("/suppliers", response_model=schemas.SupplierRead, status_code=status.HTTP_201_CREATED)
def create_supplier(supplier: schemas.SupplierCreate, db: Session = Depends(get_db)):
    return crud.create_supplier(db, supplier)


@router.get("/suppliers/{supplier_id}", response_model=schemas.SupplierRead)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    db_supplier = crud.get_supplier(db, supplier_id)
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return db_supplier


@router.patch("/suppliers/{supplier_id}", response_model=schemas.SupplierRead)
def update_supplier(supplier_id: int, update: schemas.SupplierUpdate, db: Session = Depends(get_db)):
    db_supplier = crud.get_supplier(db, supplier_id)
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return crud.update_supplier(db, db_supplier, update)


@router.post("/suppliers/{supplier_id}/deactivate", response_model=schemas.SupplierRead)
def deactivate_supplier(supplier_id: int, db: Session = Depends(get_db)):
    db_supplier = crud.get_supplier(db, supplier_id)
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return crud.deactivate_supplier(db, db_supplier)


@router.get("/suppliers/{supplier_id}/ingredient-names", response_model=list[str])
def get_supplier_ingredient_names(supplier_id: int, db: Session = Depends(get_db)):
    return crud.get_supplier_ingredient_names(db, supplier_id)


# ---- Ingredients ----
@router.get("/ingredients", response_model=list[schemas.IngredientRead])
def list_ingredients(skip: int = 0, limit: int | None = None, db: Session = Depends(get_db)):
    if limit is None:
        return crud.get_ingredients(db, skip=skip)
    return crud.get_ingredients(db, skip=skip, limit=limit)


@router.post(
    "/ingredients", response_model=schemas.IngredientRead, status_code=status.HTTP_201_CREATED
)
def create_ingredient(ingredient: schemas.IngredientCreate, db: Session = Depends(get_db)):
    return crud.create_ingredient(db, ingredient)


@router.get("/ingredients/search", response_model=list[schemas.IngredientRead])
def search_ingredients(q: str, db: Session = Depends(get_db)):
    return crud.search_ingredients_by_name(db, q)


@router.get("/ingredients/low-stock", response_model=list[schemas.IngredientRead])
def get_low_stock_ingredients(db: Session = Depends(get_db)):
    return crud.get_low_stock_ingredients(db)


@router.get("/ingredients/total-value", response_model=float)
def get_total_inventory_value(db: Session = Depends(get_db)):
    return crud.get_total_inventory_value(db)


@router.get("/ingredients/{ingredient_id}", response_model=schemas.IngredientRead)
def get_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    db_ingredient = crud.get_ingredient(db, ingredient_id)
    if db_ingredient is None:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return db_ingredient


@router.patch("/ingredients/{ingredient_id}", response_model=schemas.IngredientRead)
def update_ingredient(
    ingredient_id: int, update: schemas.IngredientUpdate, db: Session = Depends(get_db)
):
    db_ingredient = crud.get_ingredient(db, ingredient_id)
    if db_ingredient is None:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return crud.update_ingredient(db, db_ingredient, update)


@router.delete("/ingredients/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    db_ingredient = crud.get_ingredient(db, ingredient_id)
    if db_ingredient is None:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    crud.delete_ingredient(db, db_ingredient)


@router.post("/ingredients/bulk-adjust", response_model=dict)
def bulk_adjust_stock(adjustment: schemas.BulkStockAdjustment, db: Session = Depends(get_db)):
    updated = crud.bulk_adjust_stock(db, adjustment)
    return {"updated": updated}


@router.post("/ingredients/import", response_model=dict)
def import_ingredients(raw_bytes: bytes, db: Session = Depends(get_db)):
    count = crud.import_ingredients_from_pickle(db, raw_bytes)
    return {"imported": count}


@router.get("/reports/run", response_model=str)
def run_stock_report(report_name: str, db: Session = Depends(get_db)):
    return crud.run_stock_report_command(db, report_name)


# ---- Stock movements ----
@router.post(
    "/movements", response_model=schemas.StockMovementRead, status_code=status.HTTP_201_CREATED
)
def record_stock_movement(movement: schemas.StockMovementCreate, db: Session = Depends(get_db)):
    return crud.record_stock_movement(db, movement)


@router.get("/movements/{ingredient_id}", response_model=list[schemas.StockMovementRead])
def get_movements_for_ingredient(
    ingredient_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return crud.get_movements_for_ingredient(db, ingredient_id, skip=skip, limit=limit)


# ---- Purchase orders ----
@router.post(
    "/purchase-orders", response_model=schemas.PurchaseOrderRead, status_code=status.HTTP_201_CREATED
)
def create_purchase_order(po: schemas.PurchaseOrderCreate, db: Session = Depends(get_db)):
    return crud.create_purchase_order(db, po.supplier_id, po.items)


@router.get("/purchase-orders/{po_id}", response_model=schemas.PurchaseOrderRead)
def get_purchase_order(po_id: int, db: Session = Depends(get_db)):
    db_po = crud.get_purchase_order(db, po_id)
    if db_po is None:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return db_po


@router.get("/purchase-orders/{po_id}/total", response_model=float)
def get_purchase_order_total(po_id: int, db: Session = Depends(get_db)):
    db_po = crud.get_purchase_order(db, po_id)
    if db_po is None:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return crud.get_purchase_order_total(db, db_po)


@router.post("/purchase-orders/{po_id}/cancel", response_model=schemas.PurchaseOrderRead)
def cancel_purchase_order(po_id: int, db: Session = Depends(get_db)):
    db_po = crud.get_purchase_order(db, po_id)
    if db_po is None:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return crud.cancel_purchase_order(db, db_po)


@router.post("/purchase-orders/{po_id}/receive", response_model=schemas.PurchaseOrderRead)
def receive_purchase_order(po_id: int, db: Session = Depends(get_db)):
    db_po = crud.get_purchase_order(db, po_id)
    if db_po is None:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return crud.receive_purchase_order(db, db_po)


# ---- Recipes ----
@router.post("/recipes", response_model=schemas.RecipeRead, status_code=status.HTTP_201_CREATED)
def link_recipe_ingredient(recipe: schemas.RecipeCreate, db: Session = Depends(get_db)):
    return crud.link_recipe_ingredient(db, recipe)


@router.get("/recipes/{menu_item_id}/cost", response_model=float)
def get_recipe_cost(menu_item_id: int, db: Session = Depends(get_db)):
    return crud.get_recipe_cost(db, menu_item_id)


@router.post("/reports/debug", response_model=str)
def run_debug_report(request: schemas.DebugReportRequest, db: Session = Depends(get_db)):
    return crud.run_debug_report(db, request)


@router.get("/reports/export-csv", response_model=str)
def export_ingredients_csv(db: Session = Depends(get_db)):
    return crud.export_ingredients_csv(db)


@router.get("/ingredients-sorted", response_model=list[schemas.IngredientRead])
def get_ingredients_sorted(sort_by: str = "name", db: Session = Depends(get_db)):
    return crud.get_ingredients_sorted(db, sort_by)


@router.get("/ingredients/{ingredient_id}/usage-rate", response_model=float)
def get_ingredient_usage_rate(
    ingredient_id: int, days: int = 30, db: Session = Depends(get_db)
):
    return crud.get_ingredient_usage_rate(db, ingredient_id, days)


@router.post("/ingredients/{ingredient_id}/transfer-supplier", response_model=schemas.IngredientRead)
def transfer_ingredient_supplier(
    ingredient_id: int, new_supplier_id: int, db: Session = Depends(get_db)
):
    return crud.transfer_ingredient_supplier(db, ingredient_id, new_supplier_id)


@router.get("/ingredients/reorder-count", response_model=int)
def get_ingredients_needing_reorder_count(db: Session = Depends(get_db)):
    return crud.get_ingredients_needing_reorder_count(db)


@router.get("/ingredients/{ingredient_id}/recent-movements", response_model=dict)
def get_recent_movements_summary(
    ingredient_id: int, hours: int = 24, db: Session = Depends(get_db)
):
    return crud.get_recent_movements_summary(db, ingredient_id, hours)


@router.get("/suppliers/{supplier_id}/purchase-history", response_model=list[dict])
def get_supplier_purchase_history(supplier_id: int, db: Session = Depends(get_db)):
    return crud.get_supplier_purchase_history(db, supplier_id)
