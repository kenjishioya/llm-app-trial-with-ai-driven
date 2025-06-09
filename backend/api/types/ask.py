"""
質問関連GraphQL型定義
"""

import strawberry
from typing import Optional
from dataclasses import dataclass


@strawberry.input
@dataclass
class AskInput:
    """質問入力"""

    question: str
    session_id: Optional[strawberry.ID] = None
    deep_research: bool = False


@strawberry.type
@dataclass
class AskPayload:
    """質問応答ペイロード - ドキュメント仕様準拠"""

    stream: str
    session_id: strawberry.ID = strawberry.field(name="sessionId")
    message_id: strawberry.ID = strawberry.field(name="messageId")
