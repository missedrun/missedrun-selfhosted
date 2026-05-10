from datetime import datetime

from pydantic import BaseModel


class PingResponse(BaseModel):
    message: str
    monitor_id: int
    monitor_name: str
    status: str
    received_at: datetime


class MonitorEventResponse(BaseModel):
    id: int
    monitor_id: int
    event_type: str
    status_after: str
    message: str | None
    received_at: datetime

    class Config:
        from_attributes = True
