from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.routes.monitors import router as monitors_router
from app.api.routes.pings import router as pings_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.monitor import Monitor
from app.models.monitor_event import MonitorEvent


Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

cors_origins = [
    origin.strip()
    for origin in settings.backend_cors_origins.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/db-health")
def db_health():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return {"database": "ok"}
    finally:
        db.close()


app.include_router(monitors_router, prefix="/api")
app.include_router(pings_router, prefix="/api")
