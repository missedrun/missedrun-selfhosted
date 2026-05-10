import secrets

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.monitor import Monitor
from app.models.monitor_event import MonitorEvent
from app.schemas.monitor import MonitorCreate, MonitorResponse, MonitorUpdate

router = APIRouter(prefix="/monitors", tags=["monitors"])

SAFE_TOKEN_ALPHABET = (
    "ABCDEFGHJKLMNPQRSTUVWXYZ"
    "abcdefghijkmnpqrstuvwxyz"
    "23456789"
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def generate_monitor_token(length: int = 32) -> str:
    return "".join(secrets.choice(SAFE_TOKEN_ALPHABET) for _ in range(length))


def generate_unique_monitor_token(db: Session, length: int = 32) -> str:
    for _ in range(10):
        token = generate_monitor_token(length)
        exists = db.query(Monitor).filter(Monitor.token == token).first()

        if not exists:
            return token

    raise HTTPException(
        status_code=500,
        detail="Could not generate a unique monitor token",
    )


def get_monitor_or_404(monitor_id: int, db: Session) -> Monitor:
    monitor = db.query(Monitor).filter(Monitor.id == monitor_id).first()

    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")

    return monitor


@router.post("", response_model=MonitorResponse)
def create_monitor(
    payload: MonitorCreate,
    db: Session = Depends(get_db),
):
    token = generate_unique_monitor_token(db)

    monitor = Monitor(
        name=payload.name,
        token=token,
        interval_minutes=payload.interval_minutes,
        grace_minutes=payload.grace_minutes,
        status="pending",
        is_paused=False,
    )

    db.add(monitor)
    db.commit()
    db.refresh(monitor)

    return monitor


@router.get("", response_model=list[MonitorResponse])
def list_monitors(db: Session = Depends(get_db)):
    return db.query(Monitor).order_by(Monitor.id.desc()).all()


@router.get("/{monitor_id}", response_model=MonitorResponse)
def get_monitor(
    monitor_id: int,
    db: Session = Depends(get_db),
):
    return get_monitor_or_404(monitor_id, db)


@router.patch("/{monitor_id}", response_model=MonitorResponse)
def update_monitor(
    monitor_id: int,
    payload: MonitorUpdate,
    db: Session = Depends(get_db),
):
    monitor = get_monitor_or_404(monitor_id, db)

    update_data = payload.model_dump(exclude_unset=True)

    if "name" in update_data:
        monitor.name = update_data["name"]

    if "interval_minutes" in update_data:
        monitor.interval_minutes = update_data["interval_minutes"]

    if "grace_minutes" in update_data:
        monitor.grace_minutes = update_data["grace_minutes"]

    db.commit()
    db.refresh(monitor)

    return monitor


@router.post("/{monitor_id}/pause", response_model=MonitorResponse)
def pause_monitor(
    monitor_id: int,
    db: Session = Depends(get_db),
):
    monitor = get_monitor_or_404(monitor_id, db)

    monitor.is_paused = True
    monitor.status = "paused"

    db.commit()
    db.refresh(monitor)

    return monitor


@router.post("/{monitor_id}/resume", response_model=MonitorResponse)
def resume_monitor(
    monitor_id: int,
    db: Session = Depends(get_db),
):
    monitor = get_monitor_or_404(monitor_id, db)

    monitor.is_paused = False

    if monitor.last_success_at:
        monitor.status = "healthy"
    elif monitor.last_start_at:
        monitor.status = "running"
    else:
        monitor.status = "pending"

    db.commit()
    db.refresh(monitor)

    return monitor


@router.get("/{monitor_id}/history")
def get_monitor_history(
    monitor_id: int,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    monitor = get_monitor_or_404(monitor_id, db)

    query = db.query(MonitorEvent).filter(MonitorEvent.monitor_id == monitor.id)

    total = query.count()

    events = (
        query
        .order_by(MonitorEvent.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": events,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": max((total + page_size - 1) // page_size, 1),
    }


@router.delete("/{monitor_id}")
def delete_monitor(
    monitor_id: int,
    db: Session = Depends(get_db),
):
    monitor = get_monitor_or_404(monitor_id, db)

    db.query(MonitorEvent).filter(
        MonitorEvent.monitor_id == monitor.id
    ).delete(synchronize_session=False)

    db.delete(monitor)
    db.commit()

    return {
        "message": "Monitor deleted",
        "monitor_id": monitor_id,
    }
