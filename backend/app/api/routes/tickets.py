from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.decorators import timed
from app.core.deps import get_current_user
from app.db.session import get_db
from app.schemas.ticket import TicketCreate, TicketListOut, TicketOut
from app.domain.enums import TicketStatus, TicketPriority
from app.utils.pagination import normalize_pagination
from app.services.tickets_list_service import (
    TicketFilters,
    create_ticket_service,
    get_ticket_service,
    list_tickets_service,
)

router = APIRouter()


@router.post("", response_model=TicketOut, status_code=status.HTTP_201_CREATED)
@timed(logger_name="app.api", threshold_ms=80)
def create_ticket_api(
    payload: TicketCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return create_ticket_service(
        db=db,
        current_user=current_user,
        subject=payload.subject,
        description=payload.description,
        priority=payload.priority,
    )


@router.get("", response_model=TicketListOut)
@timed(logger_name="app.api", threshold_ms=120)
def list_tickets_api(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    status_filter: TicketStatus | None = Query(None, alias="status"),
    priority: TicketPriority | None = Query(None),
    created_from: datetime | None = Query(None),
    created_to: datetime | None = Query(None),
):
    pg = normalize_pagination(page, page_size)
    filters = TicketFilters(
        status=status_filter,
        priority=priority,
        created_from=created_from,
        created_to=created_to,
    )

    items, total = list_tickets_service(
        db=db,
        current_user=current_user,
        page=pg,
        filters=filters,
    )
    return TicketListOut(items=items, page=pg.page, page_size=pg.page_size, total=total)


@router.get("/{ticket_id}", response_model=TicketOut)
@timed(logger_name="app.api", threshold_ms=80)
def get_ticket_api(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_ticket_service(db=db, ticket_id=ticket_id, current_user=current_user)
