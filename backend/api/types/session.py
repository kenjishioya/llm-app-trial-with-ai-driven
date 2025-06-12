"""
セッション関連のGraphQL型定義
"""

import strawberry
from typing import List, Optional
from dataclasses import dataclass

from .message import MessageType


@strawberry.type
@dataclass
class SessionType:
    """セッション型"""

    id: str
    title: str
    created_at: str
    updated_at: Optional[str] = None
    messages: List[MessageType] = strawberry.field(default_factory=list)


@strawberry.input
class SessionInput:
    """セッション入力型"""

    title: str = "新しいチャット"
