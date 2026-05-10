import time
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.monitor import Monitor
from app.models.monitor_event import MonitorEvent
from app.services.alerts import maybe_send_monitor_alert


CHECK_INTERVAL_SECONDS = 30


def record_missing_event(
    db: Session,
    monitor: Monitor,
    now: datetime,
) -> None:
    event = MonitorEvent(
        monitor_id=monitor.id,
        event_type="missing",
        status_after="missing",
        received_at=now,
    )
    db.add(event)


def run_monitor_checks(db: Session) -> None:
    now = datetime.now(timezone.utc)

    monitors = (
        db.query(Monitor)
        .filter(Monitor.is_paused == False)  # noqa: E712
        .all()
    )

    for monitor in monitors:
        if not monitor.last_success_at:
            continue

        deadline = monitor.last_success_at + timedelta(
            minutes=monitor.interval_minutes + monitor.grace_minutes
        )

        if now <= deadline:
            continue

        if monitor.status == "missing":
            continue

        monitor.status = "missing"

        record_missing_event(db, monitor, now)
        maybe_send_monitor_alert(db, monitor)

    db.commit()


def main():
    print("MissedRun self-hosted checker started")

    while True:
        db = SessionLocal()
        try:
            run_monitor_checks(db)
        except Exception as exc:
            print(f"Monitor checker error: {exc}")
        finally:
            db.close()

        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
