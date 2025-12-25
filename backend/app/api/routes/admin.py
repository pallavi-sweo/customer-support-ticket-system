from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.decorators import timed
from app.core.deps import require_admin
from app.crud.tickets import get_ticket, update_ticket_status
from app.db.session import get_db
from pydantic import BaseModel, Field

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
    _admin=Depends(require_admin),
):
    t = get_ticket(db, ticket_id)
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    try:
        updated = update_ticket_status(db, t, payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return {"id": updated.id, "status": updated.status}
