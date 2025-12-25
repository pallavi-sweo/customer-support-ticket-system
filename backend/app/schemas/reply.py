from datetime import datetime
from pydantic import BaseModel, Field


class ReplyCreate(BaseModel):
    message: str = Field(min_length=1, max_length=5000)


class ReplyOut(BaseModel):
    id: int
    ticket_id: int
    author_id: int
    message: str
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
