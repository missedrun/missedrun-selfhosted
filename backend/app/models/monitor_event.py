from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class MonitorEvent(Base):
    __tablename__ = "monitor_events"

    id = Column(Integer, primary_key=True, index=True)

    monitor_id = Column(
        Integer,
        ForeignKey("monitors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    event_type = Column(String(50), nullable=False)
    status_after = Column(String(50), nullable=False)
    message = Column(Text, nullable=True)

    received_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    monitor = relationship("Monitor")
