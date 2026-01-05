from sqlalchemy.orm import Session

from app.core.transitions import validate_transition
from app.domain.errors import InvalidTransitionError, NotFoundError
from app.crud.tickets import get_ticket, update_ticket_status
from app.crud.replies import create_reply, list_replies
from app.policies.tickets import (
    can_reply_ticket,
    can_view_ticket,
    can_update_status,
)


def _get_ticket_or_404(db: Session, ticket_id: int):
    t = get_ticket(db, ticket_id)
    if not t:
        raise NotFoundError("Ticket not found")
    return t


def list_replies_service(db: Session, ticket_id: int, current_user):
    t = _get_ticket_or_404(db, ticket_id)
    can_view_ticket(current_user, t)

    return list_replies(db, ticket_id=ticket_id)


def create_reply_service(db: Session, ticket_id: int, current_user, message: str):
    t = _get_ticket_or_404(db, ticket_id)
    can_reply_ticket(current_user, t)
    return create_reply(
        db, ticket_id=ticket_id, author_id=current_user.id, message=message
    )


def update_status_service(db: Session, ticket_id: int, current_user, new_status: str):
    can_update_status(current_user)
    t = _get_ticket_or_404(db, ticket_id)
    try:
        validate_transition(t.status, new_status)
    except ValueError as e:
        raise InvalidTransitionError(str(e)) from e
    return update_ticket_status(db, t, new_status)
