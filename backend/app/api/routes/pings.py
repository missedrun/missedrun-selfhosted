from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.monitor import Monitor
from app.models.monitor_event import MonitorEvent
from app.schemas.ping import PingResponse
from app.services.alerts import maybe_send_monitor_alert

router = APIRouter(prefix="/ping", tags=["pings"])

MAX_EVENTS_PER_MONITOR = 500


class FailPingRequest(BaseModel):
    message: str | None = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def prune_monitor_events(
    db: Session,
    monitor_id: int,
    keep_last: int = MAX_EVENTS_PER_MONITOR,
) -> None:
    old_event_ids = (
        db.query(MonitorEvent.id)
        .filter(MonitorEvent.monitor_id == monitor_id)
        .order_by(MonitorEvent.id.desc())
        .offset(keep_last)
        .subquery()
    )

    db.query(MonitorEvent).filter(
        MonitorEvent.id.in_(old_event_ids)
    ).delete(synchronize_session=False)


def record_monitor_event(
    db: Session,
    monitor: Monitor,
    event_type: str,
    status_after: str,
    received_at: datetime,
    message: str | None = None,
) -> MonitorEvent:
    event = MonitorEvent(
        monitor_id=monitor.id,
        event_type=event_type,
        status_after=status_after,
        message=message,
        received_at=received_at,
    )

    db.add(event)
    db.flush()

    prune_monitor_events(db, monitor.id)

    return event


@router.post("/{token}", response_model=PingResponse)
def receive_ping(token: str, db: Session = Depends(get_db)):
    monitor = db.query(Monitor).filter(Monitor.token == token).first()

    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")

    now = datetime.now(timezone.utc)

    monitor.last_ping_at = now
    monitor.last_success_at = now
    monitor.status = "healthy"

    maybe_send_monitor_alert(db, monitor)

    record_monitor_event(
        db=db,
        monitor=monitor,
        event_type="success",
        status_after=monitor.status,
        received_at=now,
    )

    db.commit()

    return PingResponse(
        message="Ping received",
        monitor_id=monitor.id,
        monitor_name=monitor.name,
        status=monitor.status,
        received_at=now,
    )


@router.post("/{token}/start", response_model=PingResponse)
def receive_start_ping(token: str, db: Session = Depends(get_db)):
    monitor = db.query(Monitor).filter(Monitor.token == token).first()

    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")

    now = datetime.now(timezone.utc)

    monitor.last_ping_at = now
    monitor.last_start_at = now
    monitor.status = "running"

    record_monitor_event(
        db=db,
        monitor=monitor,
        event_type="start",
        status_after=monitor.status,
        received_at=now,
    )

    db.commit()

    return PingResponse(
        message="Start ping received",
        monitor_id=monitor.id,
        monitor_name=monitor.name,
        status=monitor.status,
        received_at=now,
    )


@router.post("/{token}/fail", response_model=PingResponse)
def receive_fail_ping(
    token: str,
    payload: FailPingRequest | None = None,
    db: Session = Depends(get_db),
):
    monitor = (
        db.query(Monitor)
        .filter(Monitor.token == token)
        .with_for_update()
        .first()
    )

    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")

    now = datetime.now(timezone.utc)
    message = payload.message if payload else None

    already_alerted_for_failed = monitor.alert_status == "failed"

    monitor.last_ping_at = now
    monitor.last_fail_at = now
    monitor.status = "failed"

    if not monitor.is_paused and not already_alerted_for_failed:
        maybe_send_monitor_alert(db, monitor)

    record_monitor_event(
        db=db,
        monitor=monitor,
        event_type="fail",
        status_after=monitor.status,
        received_at=now,
        message=message,
    )

    db.commit()

    return PingResponse(
        message="Fail ping received",
        monitor_id=monitor.id,
        monitor_name=monitor.name,
        status=monitor.status,
        received_at=now,
    )
