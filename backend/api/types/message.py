"""
メッセージ関連GraphQL型定義
"""

import strawberry
from typing import Optional, List
from dataclasses import dataclass
import enum


@strawberry.enum
class MessageRole(enum.Enum):
    """メッセージの役割"""

    USER = "user"
    ASSISTANT = "assistant"


@strawberry.type
@dataclass
class CitationType:
    """引用情報型"""

    id: int
    title: str
    content: str
    score: float
    source: str
    url: str


@strawberry.type
@dataclass
class MessageType:
    """メッセージ型"""

    id: strawberry.ID
    session_id: strawberry.ID
    role: MessageRole
    content: str
    citations: List[CitationType]  # 構造化された引用情報
    meta_data: strawberry.scalars.JSON  # JSONスカラー型を使用
    created_at: str


@strawberry.input
class MessageInput:
    """メッセージ作成入力"""

    session_id: strawberry.ID
    role: MessageRole
    content: str
    citations: Optional[str] = None  # JSON文字列として受け取り
    meta_data: Optional[str] = None  # JSON文字列として受け取り
