from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.monitor import Monitor
from app.services.email import send_email


def maybe_send_monitor_alert(db: Session, monitor: Monitor) -> None:
    now = datetime.now(timezone.utc)

    if monitor.is_paused:
        return

    if monitor.status == "healthy":
        if monitor.alert_status:
            monitor.alert_status = None
            monitor.alert_sent_at = None
        return

    if monitor.status not in {"missing", "failed"}:
        return

    if monitor.alert_status == monitor.status:
        return

    subject = f"MissedRun alert: {monitor.name} is {monitor.status}"

    body = (
        f"Monitor: {monitor.name}\n"
        f"Status: {monitor.status}\n"
        f"Last ping: {monitor.last_ping_at}\n"
        f"Last success: {monitor.last_success_at}\n"
        f"Last fail: {monitor.last_fail_at}\n"
    )

    if settings.alert_email:
        send_email(settings.alert_email, subject, body)
    else:
        print("[alert] ALERT_EMAIL is not configured.")
        print(subject)
        print(body)

    monitor.alert_status = monitor.status
    monitor.alert_sent_at = now
