from app.domain.enums import Role, TicketStatus
from app.domain.errors import ForbiddenError, ValidationError

def can_view_ticket(user, ticket) -> None:
    if user.role == Role.ADMIN:
        return
    if ticket.user_id != user.id:
        raise ForbiddenError("You cannot view this ticket.")

def can_reply_ticket(user, ticket) -> None:
    # block CLOSED replies 
    if ticket.status == TicketStatus.CLOSED: 
        raise ValidationError("Closed tickets cannot be replied to.")
    return can_view_ticket(user, ticket)

def can_update_status(user) -> None:
    if user.role != Role.ADMIN:
        raise ForbiddenError("Admin access required.")

def ensure_can_access_ticket(current_user, ticket) -> None:
    """
    Admin can access any ticket.
    User can access only their own ticket.
    """
    if current_user.role == "ADMIN":
        return
    if ticket.user_id != current_user.id:
        raise ForbiddenError("Forbidden")
