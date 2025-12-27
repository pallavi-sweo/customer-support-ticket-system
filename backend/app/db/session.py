import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.models import (
    user,
    ticket,
    reply,
)  # noqa: F401  # ensure models imported for metadata
from app.core.decorators import db_timed

logger = logging.getLogger("app.db.session")

engine = create_engine(
    settings.resolved_database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@db_timed(threshold_ms=10)
def init_db() -> None:
    """
    create tables at startup.
    """
    Base.metadata.create_all(bind=engine)
    _bootstrap_admin_if_configured()


def _bootstrap_admin_if_configured() -> None:
    if not settings.bootstrap_admin_email or not settings.bootstrap_admin_password:
        return

    from sqlalchemy import select
    from app.models.user import User
    from app.core.security import hash_password

    with SessionLocal() as db:
        existing = db.scalar(
            select(User).where(User.email == settings.bootstrap_admin_email)
        )
        if existing:
            return

        admin = User(
            email=settings.bootstrap_admin_email,
            password_hash=hash_password(settings.bootstrap_admin_password),
            role="ADMIN",
        )
        db.add(admin)
        db.commit()
        logger.info("bootstrapped_admin email=%s", settings.bootstrap_admin_email)
