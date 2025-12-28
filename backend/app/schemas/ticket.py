from datetime import datetime
from pydantic import BaseModel, Field

from app.domain.enums import TicketPriority, TicketStatus


class TicketCreate(BaseModel):
    subject: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=10, max_length=5000)
    priority: TicketPriority


class TicketOut(BaseModel):
    id: int
    user_id: int
    subject: str
    description: str
    status: TicketStatus
    priority: TicketPriority
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class TicketListOut(BaseModel):
    items: list[TicketOut]
    page: int
    page_size: int
    total: int


class StatusUpdate(BaseModel):
    status: TicketStatus
