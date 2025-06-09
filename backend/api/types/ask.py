"""
質問関連GraphQL型定義
"""

import strawberry
from typing import Optional
from .message import MessageType


@strawberry.input
class AskInput:
    """質問入力"""

    question: str
    session_id: Optional[strawberry.ID] = None
    deep_research: bool = False


@strawberry.type
class AskPayload:
    """質問応答ペイロード"""

    user_message: MessageType
    assistant_message: MessageType
    session_id: strawberry.ID
