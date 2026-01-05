from app.domain.enums import Role, TicketStatus
from app.domain.errors import ForbiddenError, ValidationError


def can_view_ticket(user, ticket) -> None:
    if user.role == Role.ADMIN:
        return
    if ticket.user_id != user.id:
        raise ForbiddenError("You cannot view this ticket.")


def can_reply_ticket(user, ticket) -> None:
    # block CLOSED replies
    can_view_ticket(user, ticket)
    if ticket.status == TicketStatus.CLOSED:
        raise ValidationError("Closed tickets cannot be replied to.")


def can_update_status(user) -> None:
    if user.role != Role.ADMIN:
        raise ForbiddenError("Admin access required.")


def ensure_admin(current_user) -> None:
    if current_user.role != "ADMIN":
        raise ForbiddenError("Admin access required")


def ensure_customer(current_user) -> None:
    if current_user.role != "USER":
        raise ForbiddenError("Only customers can create tickets")
