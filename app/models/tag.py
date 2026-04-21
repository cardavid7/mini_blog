from __future__ import annotations
from sqlalchemy import Integer, String, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone, timedelta
from typing import List, TYPE_CHECKING
from app.core.db import Base

if TYPE_CHECKING:
    from .post import PostORM

class TagORM(Base):
    __tablename__ = "tags"
    __table_args__ = (UniqueConstraint("name", name="unique_tag_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone(timedelta(hours=-5))), nullable=False)
    posts: Mapped[List["PostORM"]] = relationship(secondary="post_tags", back_populates="tags", lazy="selectin")
