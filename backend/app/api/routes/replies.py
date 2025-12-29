from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.decorators import timed
from app.core.deps import get_current_user
from app.db.session import get_db
from app.schemas.reply import ReplyCreate, ReplyOut, ReplyListOut
from app.services.tickets import create_reply_service
from app.crud.tickets import get_ticket
from app.policies.tickets import ensure_can_access_ticket
from app.crud.replies import list_replies
from app.domain.errors import NotFoundError

router = APIRouter()


@router.get("/tickets/{ticket_id}/replies", response_model=ReplyListOut)
@timed(logger_name="app.api", threshold_ms=120)
def list_replies_api(
    ticket_id: int,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    t = get_ticket(db, ticket_id)
    if not t:
        raise NotFoundError("Ticket not found")

    ensure_can_access_ticket(current_user, t)
    items, total = list_replies(db, ticket_id=ticket_id, page=page, page_size=page_size)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.post(
    "/tickets/{ticket_id}/replies",
    response_model=ReplyOut,
    status_code=status.HTTP_201_CREATED,
)
@timed(logger_name="app.api", threshold_ms=120)
def create_reply_api(
    ticket_id: int,
    payload: ReplyCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return create_reply_service(
        db=db, ticket_id=ticket_id, current_user=current_user, message=payload.message
    )
