"""
質問関連GraphQL型定義
"""

import strawberry
from typing import Optional, List
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
    """質問応答ペイロード"""

    answer: str
    session_id: strawberry.ID
    message_id: strawberry.ID
    citations: List[str]
