from sqlalchemy import Boolean, Integer, String, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone, timedelta
from typing import Literal
from app.core.db import Base

Role = Literal["admin", "editor", "user"]

class UserORM(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(Enum("admin", "editor", "user", name="role_enum"), default="user", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone(timedelta(hours=-5))), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone(timedelta(hours=-5))), nullable=False)
    