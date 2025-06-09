"""
GraphQL Query リゾルバ
"""

import strawberry
from typing import List, Optional
from datetime import datetime
from dataclasses import dataclass

from api.types import SessionType, MessageType
from api.types.message import MessageRole as GraphQLMessageRole
from services import SessionService
from deps import get_db


@strawberry.type
@dataclass
class HealthType:
    """ヘルスチェック型"""

    status: str
    timestamp: str


@strawberry.type
class Query:
    """GraphQL Query"""

    @strawberry.field
    async def health(self) -> HealthType:
        """ヘルスチェック"""
        return HealthType(status="ok", timestamp=datetime.now().isoformat())

    @strawberry.field
    async def sessions(self) -> List[SessionType]:
        """セッション一覧取得"""
        async for db in get_db():
            session_service = SessionService(db)
            sessions = await session_service.get_sessions()

            return [
                SessionType(
                    id=session.id,
                    title=session.title,
                    created_at=session.created_at.isoformat(),
                    updated_at=(
                        session.updated_at.isoformat() if session.updated_at else None
                    ),
                    messages=[],
                )
                for session in sessions
            ]
        return []  # Fallback return for mypy

    @strawberry.field
    async def session(self, id: str) -> Optional[SessionType]:
        """セッション詳細取得"""
        async for db in get_db():
            session_service = SessionService(db)
            session = await session_service.get_session_with_messages(id)

            if not session:
                return None

            # メッセージをGraphQL型に変換
            messages = [
                MessageType(
                    id=msg.id,
                    role=GraphQLMessageRole(msg.role.value),
                    content=msg.content,
                    created_at=msg.created_at.isoformat(),
                    citations=[],  # JSON文字列から変換
                    meta_data={},  # JSON文字列から変換
                )
                for msg in session.messages
            ]

            return SessionType(
                id=session.id,
                title=session.title,
                created_at=session.created_at.isoformat(),
                updated_at=(
                    session.updated_at.isoformat() if session.updated_at else None
                ),
                messages=messages,
            )
        return None  # Fallback return for mypy
