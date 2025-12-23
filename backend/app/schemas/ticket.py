from datetime import datetime
from pydantic import BaseModel, Field

# Enums by regex pattern for simplicity
STATUS_PATTERN = "^(OPEN|IN_PROGRESS|RESOLVED|CLOSED)$"
PRIORITY_PATTERN = "^(LOW|MEDIUM|HIGH)$"


class TicketCreate(BaseModel):
    subject: str = Field(min_length=5, max_length=200)
    description: str = Field(min_length=10, max_length=5000)
    priority: str = Field(pattern=PRIORITY_PATTERN)


class TicketOut(BaseModel):
    id: int
    user_id: int
    subject: str
    description: str
    status: str
    priority: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class TicketListOut(BaseModel):
    items: list[TicketOut]
    page: int
    page_size: int
    total: int
