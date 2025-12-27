from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.decorators import timed
from app.core.security import create_access_token, verify_password
from app.crud.users import create_user, get_user_by_email
from app.db.session import get_db
from app.schemas.auth import TokenOut, UserCreate, UserOut

router = APIRouter()


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
@timed(logger_name="app.api", threshold_ms=50)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, email=payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )

    user = create_user(db, email=payload.email, password=payload.password, role="USER")
    return user


@router.post("/login", response_model=TokenOut)
@timed(logger_name="app.api", threshold_ms=50)
def login(payload: UserCreate, db: Session = Depends(get_db)):
    user = get_user_by_email(db, email=payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    token = create_access_token(subject=user.email, role=user.role)
    return TokenOut(access_token=token, role=user.role)
