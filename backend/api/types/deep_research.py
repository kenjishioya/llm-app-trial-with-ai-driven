"""Deep Research GraphQL Types."""

import strawberry
from typing import Optional
from dataclasses import dataclass


@strawberry.input
class DeepResearchInput:
    """Deep Research入力型."""

    session_id: str
    question: str


@strawberry.type
@dataclass
class DeepResearchPayload:
    """Deep Research応答型."""

    session_id: str
    research_id: str
    stream_url: str
    status: str
    message: Optional[str] = None
