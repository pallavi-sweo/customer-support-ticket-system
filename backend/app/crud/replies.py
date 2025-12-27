from sqlalchemy import asc, select
from sqlalchemy.orm import Session

from app.core.decorators import db_timed, log_call
from app.models.reply import TicketReply


@log_call(logger_name="app.crud.replies")
@db_timed(threshold_ms=15)
def create_reply(
    db: Session, ticket_id: int, author_id: int, message: str
) -> TicketReply:
    r = TicketReply(ticket_id=ticket_id, author_id=author_id, message=message)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@db_timed(threshold_ms=15)
def list_replies(db: Session, ticket_id: int) -> list[TicketReply]:
    q = (
        select(TicketReply)
        .where(TicketReply.ticket_id == ticket_id)
        .order_by(asc(TicketReply.created_at))
    )
    return db.scalars(q).all()
