from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.domain.enums import TicketStatus, TicketPriority
from app.domain.errors import NotFoundError, ValidationError
from app.policies.tickets import ensure_can_access_ticket, ensure_customer
from app.crud.tickets import create_ticket as crud_create_ticket
from app.crud.tickets import get_ticket as crud_get_ticket
from app.crud.tickets import list_tickets as crud_list_tickets
from app.utils.pagination import Page

ALLOWED_STATUS = {"OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"}
ALLOWED_PRIORITY = {"LOW", "MEDIUM", "HIGH"}


@dataclass(frozen=True)
class TicketFilters:
    status: Optional[str] = None
    priority: Optional[str] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None


def validate_filters(filters: TicketFilters) -> None:
    if (
        filters.created_from
        and filters.created_to
        and filters.created_from > filters.created_to
    ):
        raise ValidationError("created_from must be <= created_to")


def create_ticket_service(
    db: Session, current_user, subject: str, description: str, priority: str
):
    ensure_customer(current_user)

    subject = (subject or "").strip()
    description = (description or "").strip()

    if not subject:
        raise ValidationError("subject is required")
    if not description:
        raise ValidationError("description is required")
    if priority not in ALLOWED_PRIORITY:
        raise ValidationError(f"Invalid priority: {priority}")

    return crud_create_ticket(
        db,
        user_id=current_user.id,
        subject=subject,
        description=description,
        priority=priority,
    )


def get_ticket_service(db: Session, ticket_id: int, current_user):
    t = crud_get_ticket(db, ticket_id)
    if not t:
        raise NotFoundError("Ticket not found")
    ensure_can_access_ticket(current_user, t)
    return t


def list_tickets_service(
    db: Session,
    current_user,
    page: Page,
    filters: TicketFilters,
):
    validate_filters(filters)

    is_admin = current_user.role == "ADMIN"

    items, total = crud_list_tickets(
        db,
        page,
        is_admin=is_admin,
        user_id=current_user.id,
        status=filters.status,
        priority=filters.priority,
        created_from=filters.created_from,
        created_to=filters.created_to,
    )
    return items, total
