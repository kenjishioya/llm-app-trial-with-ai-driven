"""
メッセージ関連GraphQL型定義
"""

import strawberry
from typing import Optional
from datetime import datetime
import enum


@strawberry.enum
class MessageRole(enum.Enum):
    """メッセージの役割"""

    USER = "user"
    ASSISTANT = "assistant"


@strawberry.type
class MessageType:
    """メッセージ型"""

    id: strawberry.ID
    session_id: strawberry.ID
    role: MessageRole
    content: str
    citations: Optional[str] = None  # JSON文字列として扱う
    meta_data: Optional[str] = None  # JSON文字列として扱う
    created_at: datetime


@strawberry.input
class MessageInput:
    """メッセージ作成入力"""

    session_id: strawberry.ID
    role: MessageRole
    content: str
    citations: Optional[str] = None
    meta_data: Optional[str] = None
