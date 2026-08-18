from fastapi import FastAPI

from app.config import get_settings
from app.database import Base, engine
from app.routers import menu, orders, reservations, tables

settings = get_settings()

# Bare-bones schema management: create tables on startup if they don't exist yet.
# A migration tool (e.g. Alembic) should replace this once the schema needs to evolve.
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

app.include_router(tables.router)
app.include_router(menu.router)
app.include_router(orders.router)
app.include_router(reservations.router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
