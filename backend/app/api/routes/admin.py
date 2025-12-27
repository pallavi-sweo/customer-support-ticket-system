from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.decorators import timed
from app.core.deps import require_admin
from app.db.session import get_db
from app.services.tickets import update_status_service

STATUS_PATTERN = "^(OPEN|IN_PROGRESS|RESOLVED|CLOSED)$"


class StatusUpdate(BaseModel):
    status: str = Field(pattern=STATUS_PATTERN)


router = APIRouter()


@router.put("/tickets/{ticket_id}/status", status_code=status.HTTP_200_OK)
@timed(logger_name="app.api", threshold_ms=120)
def update_status_api(
    ticket_id: int,
    payload: StatusUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin),
):
    updated = update_status_service(
        db=db,
        ticket_id=ticket_id,
        current_user=current_user,
        new_status=payload.status,
    )
    return {"id": updated.id, "status": updated.status}
