"""
チャットメッセージモデル
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from enum import Enum
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped
import uuid

from . import Base

if TYPE_CHECKING:
    from .session import Session


class MessageRole(Enum):
    """メッセージの役割"""

    USER = "user"
    ASSISTANT = "assistant"


class Message(Base):  # type: ignore[valid-type,misc]
    """チャットメッセージ"""

    __tablename__ = "messages"

    id: Mapped[str] = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    session_id: Mapped[str] = Column(
        String(36), ForeignKey("sessions.id"), nullable=False
    )
    role: Mapped[MessageRole] = Column(SQLEnum(MessageRole), nullable=False)
    content: Mapped[str] = Column(Text, nullable=False)

    # RAG関連のメタデータ（JSONで格納）
    citations: Mapped[Optional[str]] = Column(
        Text, nullable=True
    )  # 引用情報（JSON文字列）
    meta_data: Mapped[Optional[str]] = Column(
        Text, nullable=True
    )  # その他のメタデータ（JSON文字列）

    created_at: Mapped[datetime] = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # リレーション
    session: Mapped["Session"] = relationship("Session", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role.value}, session_id={self.session_id})>"
