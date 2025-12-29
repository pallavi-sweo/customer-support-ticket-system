from sqlalchemy import asc, select, func
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
def list_replies(
    db: Session,
    ticket_id: int,
    page: int,
    page_size: int,
) -> tuple[list[TicketReply], int]:
    base = select(TicketReply).where(TicketReply.ticket_id == ticket_id)

    # total count
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0

    # stable ordering (thread order)
    q = (
        base.order_by(asc(TicketReply.created_at), asc(TicketReply.id))
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = db.scalars(q).all()
    return items, total
