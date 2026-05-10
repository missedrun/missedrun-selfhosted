from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.db.base import Base


class Monitor(Base):
    __tablename__ = "monitors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)

    token = Column(String(64), nullable=False, unique=True, index=True)

    interval_minutes = Column(Integer, nullable=False, default=1440)
    grace_minutes = Column(Integer, nullable=False, default=60)

    status = Column(String(50), nullable=False, default="pending")
    is_paused = Column(Boolean, nullable=False, default=False)

    last_ping_at = Column(DateTime(timezone=True), nullable=True)
    last_start_at = Column(DateTime(timezone=True), nullable=True)
    last_success_at = Column(DateTime(timezone=True), nullable=True)
    last_fail_at = Column(DateTime(timezone=True), nullable=True)

    alert_status = Column(String(50), nullable=True)
    alert_sent_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
