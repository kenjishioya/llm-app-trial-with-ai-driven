"""
チャットセッションモデル
"""

from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship, Mapped
import uuid
from datetime import datetime, timezone
from typing import List, TYPE_CHECKING

from . import Base

if TYPE_CHECKING:
    from .message import Message


class Session(Base):  # type: ignore[valid-type,misc]
    """チャットセッション"""

    __tablename__ = "sessions"

    id: Mapped[str] = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    title: Mapped[str] = Column(String(255), nullable=False, default="新しいチャット")
    created_at: Mapped[datetime] = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # リレーション
    messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="session", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Session(id={self.id}, title='{self.title}')>"
