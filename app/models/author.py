from __future__ import annotations
from sqlalchemy import Integer, String, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone, timedelta
from typing import List, TYPE_CHECKING
from app.core.db import Base

if TYPE_CHECKING:
    from .post import PostORM

class AuthorORM(Base):
    __tablename__ = "authors"
    __table_args__ = (UniqueConstraint("email", name="unique_author_email"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone(timedelta(hours=-5))), nullable=False)
    posts: Mapped[List["PostORM"]] = relationship(back_populates="author")
