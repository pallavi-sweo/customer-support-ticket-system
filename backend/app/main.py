import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.tickets import router as tickets_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import init_db

logger = logging.getLogger("app")


def create_app() -> FastAPI:
    setup_logging("INFO")

    app = FastAPI(title=settings.app_name)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # tighten if needed
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    app.include_router(tickets_router, prefix="/tickets", tags=["tickets"])

    @app.on_event("startup")
    def _startup() -> None:
        if os.getenv("TESTING") == "1":
            return
        init_db()
        logger.info("startup_complete env=%s", settings.env)

    return app


app = create_app()
