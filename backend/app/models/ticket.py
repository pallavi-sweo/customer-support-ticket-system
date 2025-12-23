from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Use strings for speed and MySQL compatibility; validate via Pydantic on input.
    status: Mapped[str] = mapped_column(String(20), index=True, nullable=False, default="OPEN")
    priority: Mapped[str] = mapped_column(String(20), index=True, nullable=False, default="MEDIUM")

    created_at: Mapped[str] = mapped_column(DateTime(timezone=False), server_default=func.now(), index=True)
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())

    creator = relationship("User", back_populates="tickets")
