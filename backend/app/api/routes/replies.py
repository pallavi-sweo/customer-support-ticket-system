from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.decorators import timed
from app.core.deps import get_current_user
from app.db.session import get_db
from app.schemas.reply import ReplyCreate, ReplyOut
from app.services.tickets import create_reply_service, list_replies_service

router = APIRouter()


@router.get("/tickets/{ticket_id}/replies", response_model=list[ReplyOut])
@timed(logger_name="app.api", threshold_ms=120)
def list_replies_api(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return list_replies_service(db=db, ticket_id=ticket_id, current_user=current_user)


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
        db=db,
        ticket_id=ticket_id,
        current_user=current_user,
        message=payload.message,
    )
