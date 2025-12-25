from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.decorators import timed
from app.core.deps import get_current_user
from app.crud.replies import create_reply, list_replies
from app.crud.tickets import get_ticket
from app.db.session import get_db
from app.schemas.reply import ReplyCreate, ReplyOut

router = APIRouter()


def _ensure_ticket_access(ticket_user_id: int, current_user) -> None:
    if current_user.role == "ADMIN":
        return
    if ticket_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


@router.get("/tickets/{ticket_id}/replies", response_model=list[ReplyOut])
@timed(logger_name="app.api", threshold_ms=120)
def list_replies_api(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    t = get_ticket(db, ticket_id)
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    _ensure_ticket_access(t.user_id, current_user)
    return list_replies(db, ticket_id=ticket_id)


@router.post(
    "/tickets/{ticket_id}/replies", response_model=ReplyOut, status_code=status.HTTP_201_CREATED
)
@timed(logger_name="app.api", threshold_ms=120)
def create_reply_api(
    ticket_id: int,
    payload: ReplyCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    t = get_ticket(db, ticket_id)
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    _ensure_ticket_access(t.user_id, current_user)
    return create_reply(db, ticket_id=ticket_id, author_id=current_user.id, message=payload.message)
