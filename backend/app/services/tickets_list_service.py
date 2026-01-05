from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple

from sqlalchemy import and_, desc, func, select
from sqlalchemy.orm import Session

from app.domain.enums import Role, TicketStatus, TicketPriority
from app.domain.errors import NotFoundError, ValidationError
from app.policies.tickets import can_view_ticket, ensure_customer
from app.crud.tickets import create_ticket as crud_create_ticket
from app.crud.tickets import get_ticket as crud_get_ticket
from app.crud.tickets import list_tickets as crud_list_tickets
from app.utils.pagination import Page


@dataclass(frozen=True)
class TicketFilters:
    status: Optional[str] = None
    priority: Optional[str] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None

    def validate(self) -> None:
        if self.created_from and self.created_to and self.created_from > self.created_to:
            raise ValidationError("created_from must be <= created_to")


def create_ticket_service(
    db: Session, current_user, subject: str, description: str, priority: TicketPriority | str
):
    ensure_customer(current_user)

    subject = (subject or "").strip()
    description = (description or "").strip()

    if not subject:
        raise ValidationError("subject is required")
    if not description:
        raise ValidationError("description is required")
    if isinstance(priority, TicketPriority):
        priority_value = priority.value
    else:
        try:
            priority_value = TicketPriority(priority).value
        except ValueError as exc:
            raise ValidationError(f"Invalid priority: {priority}") from exc

    return crud_create_ticket(
        db,
        user_id=current_user.id,
        subject=subject,
        description=description,
        priority=priority_value,
    )


def get_ticket_service(db: Session, ticket_id: int, current_user):
    t = crud_get_ticket(db, ticket_id)
    if not t:
        raise NotFoundError("Ticket not found")
    can_view_ticket(current_user, t)
    return t


def list_tickets_service(
    db: Session,
    current_user,
    page: Page,
    filters: TicketFilters,
) -> Tuple[list, int]:
    filters.validate()

    is_admin = current_user.role == Role.ADMIN

    status_value = filters.status.value if filters.status else None
    priority_value = filters.priority.value if filters.priority else None

    items, total = crud_list_tickets(
        db,
        page,
        is_admin=is_admin,
        user_id=current_user.id,
        status=status_value,
        priority=priority_value,
        created_from=filters.created_from,
        created_to=filters.created_to,
    )
    return items, total
