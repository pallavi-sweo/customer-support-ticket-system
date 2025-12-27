from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.decorators import timed
from app.core.deps import get_current_user
from app.crud.tickets import create_ticket, get_ticket, list_tickets
from app.db.session import get_db
from app.schemas.ticket import TicketCreate, TicketListOut, TicketOut
from app.utils.pagination import normalize_pagination

router = APIRouter()


def _ensure_ticket_access(ticket_user_id: int, current_user) -> None:
    if current_user.role == "ADMIN":
        return
    if ticket_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


@router.post("", response_model=TicketOut, status_code=status.HTTP_201_CREATED)
@timed(logger_name="app.api", threshold_ms=80)
def create_ticket_api(
    payload: TicketCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "USER":
        # spec: users create tickets
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers can create tickets",
        )

    t = create_ticket(
        db,
        user_id=current_user.id,
        subject=payload.subject,
        description=payload.description,
        priority=payload.priority,
    )
    return t


@router.get("", response_model=TicketListOut)
@timed(logger_name="app.api", threshold_ms=120)
def list_tickets_api(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    status_filter: str | None = Query(None, alias="status"),
    priority: str | None = Query(None),
    created_from: datetime | None = Query(None),
    created_to: datetime | None = Query(None),
):
    pg = normalize_pagination(page, page_size)
    is_admin = current_user.role == "ADMIN"

    # Spec says filters for admin. For user, allowing filters is ok; RBAC still applies.
    items, total = list_tickets(
        db,
        pg,
        is_admin=is_admin,
        user_id=current_user.id,
        status=status_filter,
        priority=priority,
        created_from=created_from,
        created_to=created_to,
    )
    return TicketListOut(items=items, page=pg.page, page_size=pg.page_size, total=total)


@router.get("/{ticket_id}", response_model=TicketOut)
@timed(logger_name="app.api", threshold_ms=80)
def get_ticket_api(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    t = get_ticket(db, ticket_id)
    if not t:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
        )

    _ensure_ticket_access(t.user_id, current_user)
    return t
