from datetime import datetime

from pydantic import BaseModel, Field


class MonitorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    interval_minutes: int = Field(default=1440, ge=1)
    grace_minutes: int = Field(default=60, ge=0)


class MonitorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    interval_minutes: int | None = Field(default=None, ge=1)
    grace_minutes: int | None = Field(default=None, ge=0)


class MonitorResponse(BaseModel):
    id: int
    name: str
    token: str
    interval_minutes: int
    grace_minutes: int
    status: str
    is_paused: bool
    last_ping_at: datetime | None
    last_start_at: datetime | None
    last_success_at: datetime | None
    last_fail_at: datetime | None
    alert_status: str | None
    alert_sent_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True
