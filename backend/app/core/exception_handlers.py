from fastapi import Request
from fastapi.responses import JSONResponse
from app.domain.errors import DomainError, NotFoundError, ForbiddenError, InvalidTransitionError, ValidationError

def add_exception_handlers(app):
    @app.exception_handler(DomainError)
    async def domain_error_handler(_: Request, exc: DomainError):
        status = 400
        if isinstance(exc, NotFoundError): status = 404
        if isinstance(exc, ForbiddenError): status = 403
        if isinstance(exc, InvalidTransitionError): status = 400
        if isinstance(exc, ValidationError): status = 400

        return JSONResponse(
            status_code=status,
            content={"error": {"code": exc.code, "message": str(exc)}},
        )
