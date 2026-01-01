import logging
from pathlib import Path
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


def _build_connect_args() -> dict:
    """
    Aiven requires TLS. PyMySQL needs ssl as a dict, not 'ssl=true'.
    supports:
      - settings.db_ssl_ca_path: a filesystem path to CA pem
      - settings.db_ssl_ca_pem: the PEM content stored in env var
    """
    if not settings.resolved_database_url.startswith("mysql+pymysql://"):
        return {}

    ca_path = settings.db_ssl_ca_path

    if not ca_path and settings.db_ssl_ca_pem:
        # Write PEM into a file inside container
        pem_file = Path("/tmp/aiven-ca.pem")
        pem_file.write_text(settings.db_ssl_ca_pem, encoding="utf-8")
        ca_path = str(pem_file)

    if ca_path:
        return {"ssl": {"ca": ca_path}}

    # If Aiven TLS is required and we don't have CA, connection may fail.
    # Return empty connect_args and let it error clearly.
    return {}


engine = create_engine(
    settings.resolved_database_url,
    pool_pre_ping=True,
    connect_args=_build_connect_args(),
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
