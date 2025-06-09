"""
GraphQL Subscription リゾルバ
"""

import strawberry
import uuid
from typing import AsyncGenerator, Optional
from dataclasses import dataclass

from services import RAGService
from deps import get_db


@strawberry.type
@dataclass
class StreamChunk:
    """ストリーミングチャンク"""

    content: str
    session_id: str
    is_complete: bool
    message_id: str = ""


@strawberry.type
class Subscription:
    """GraphQL Subscription"""

    @strawberry.subscription
    async def stream_answer(
        self,
        question: str,
        session_id: Optional[str] = None,
        deep_research: bool = False,
    ) -> AsyncGenerator[StreamChunk, None]:
        """ストリーミング回答"""
        async for db in get_db():
            rag_service = RAGService(db)

            # セッションIDがあればUUIDに変換
            session_uuid = None
            if session_id:
                try:
                    session_uuid = uuid.UUID(session_id)
                except ValueError:
                    yield StreamChunk(
                        content="Invalid session ID format",
                        session_id="",
                        is_complete=True,
                    )
                    return

            # ストリーミング処理
            try:
                async for chunk in rag_service.stream_answer(
                    question=question,
                    session_id=session_uuid,
                    deep_research=deep_research,
                ):
                    if "error" in chunk:
                        yield StreamChunk(
                            content=f"Error: {chunk['error']}",
                            session_id=chunk.get("session_id", ""),
                            is_complete=True,
                        )
                    else:
                        yield StreamChunk(
                            content=chunk.get("chunk", ""),
                            session_id=chunk["session_id"],
                            is_complete=chunk["is_complete"],
                            message_id=chunk.get("message_id", ""),
                        )
            except Exception as e:
                yield StreamChunk(
                    content=f"Error: {str(e)}",
                    session_id=session_id or "",
                    is_complete=True,
                )
