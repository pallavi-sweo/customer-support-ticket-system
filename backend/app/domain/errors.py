class DomainError(Exception):
    code = "DOMAIN_ERROR"

class NotFoundError(DomainError):
    code = "NOT_FOUND"

class ForbiddenError(DomainError):
    code = "FORBIDDEN"

class InvalidTransitionError(DomainError):
    code = "INVALID_TRANSITION"

class ValidationError(DomainError):
    code = "VALIDATION_ERROR"
