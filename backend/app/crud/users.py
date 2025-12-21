from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.decorators import db_timed, log_call
from app.core.security import hash_password
from app.models.user import User


@db_timed(threshold_ms=10)
def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


@log_call(logger_name="app.crud.users")
@db_timed(threshold_ms=10)
def create_user(db: Session, email: str, password: str, role: str = "USER") -> User:
    user = User(email=email, password_hash=hash_password(password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
