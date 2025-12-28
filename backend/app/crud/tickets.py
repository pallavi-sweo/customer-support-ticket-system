from __future__ import annotations

from datetime import datetime
from sqlalchemy import and_, desc, func, select
from sqlalchemy.orm import Session

from app.core.decorators import db_timed, log_call
from app.core.transitions import validate_transition
from app.models.ticket import Ticket
from app.utils.pagination import Page


@log_call(logger_name="app.crud.tickets")
@db_timed(threshold_ms=15)
def create_ticket(
    db: Session, user_id: int, subject: str, description: str, priority: str
) -> Ticket:
    t = Ticket(
        user_id=user_id, subject=subject, description=description, priority=priority
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@db_timed(threshold_ms=10)
def get_ticket(db: Session, ticket_id: int) -> Ticket | None:
    return db.get(Ticket, ticket_id)


@db_timed(threshold_ms=25)
def list_tickets(
    db: Session,
    page: Page,
    *,
    is_admin: bool,
    user_id: int | None = None,
    status: str | None = None,
    priority: str | None = None,
    created_from: datetime | None = None,
    created_to: datetime | None = None,
) -> tuple[list[Ticket], int]:
    filters = []

    # RBAC: user sees only own tickets
    if not is_admin:
        filters.append(Ticket.user_id == user_id)

    if status:
        filters.append(
            Ticket.status == (status.value if hasattr(status, "value") else status)
        )
    if priority:
        filters.append(
            Ticket.priority
            == (priority.value if hasattr(priority, "value") else priority)
        )
    if created_from:
        filters.append(Ticket.created_at >= created_from)
    if created_to:
        filters.append(Ticket.created_at <= created_to)

    where_clause = and_(*filters) if filters else None

    base_q = select(Ticket)
    count_q = select(func.count()).select_from(Ticket)

    if where_clause is not None:
        base_q = base_q.where(where_clause)
        count_q = count_q.where(where_clause)

    total = db.scalar(count_q) or 0

    items = db.scalars(
        base_q.order_by(desc(Ticket.created_at), desc(Ticket.id))
        .offset(page.offset)
        .limit(page.page_size)
    ).all()

    return items, total


@log_call(logger_name="app.crud.tickets")
@db_timed(threshold_ms=20)
def update_ticket_status(db: Session, ticket: Ticket, new_status: str) -> Ticket:
    validate_transition(ticket.status, new_status)
    ticket.status = new_status
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket
