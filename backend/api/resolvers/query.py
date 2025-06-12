"""
GraphQL Query リゾルバ
"""

import strawberry
import json
import time
from typing import List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

from api.types import SessionType, MessageType, CitationType
from api.types.message import MessageRole as GraphQLMessageRole
from api.types.document import (
    SearchResultType,
    SearchInput,
    DocumentType,
    DocumentMetadataType,
)
from services import SessionService, RAGService
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
    async def sessions(self, include_messages: bool = False) -> List[SessionType]:
        """セッション一覧取得"""
        async for db in get_db():
            session_service = SessionService(db)

            if include_messages:
                # メッセージも含めて取得（より重い操作）
                sessions = await session_service.get_sessions_with_messages()

                return [
                    SessionType(
                        id=session.id,
                        title=session.title,
                        created_at=session.created_at.isoformat(),
                        updated_at=(
                            session.updated_at.isoformat()
                            if session.updated_at
                            else None
                        ),
                        messages=[
                            MessageType(
                                id=msg.id,
                                session_id=session.id,
                                role=GraphQLMessageRole(msg.role.value),
                                content=msg.content,
                                created_at=msg.created_at.isoformat(),
                                citations=self._parse_citations(msg.citations),
                                meta_data=self._parse_metadata(msg.meta_data),
                            )
                            for msg in session.messages[:5]  # 最新5件のみ
                        ],
                    )
                    for session in sessions
                ]
            else:
                # 軽量版: メッセージは含めない（デフォルト動作維持）
                sessions = await session_service.get_sessions()

                return [
                    SessionType(
                        id=session.id,
                        title=session.title,
                        created_at=session.created_at.isoformat(),
                        updated_at=(
                            session.updated_at.isoformat()
                            if session.updated_at
                            else None
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
                    session_id=session.id,
                    role=GraphQLMessageRole(msg.role.value),
                    content=msg.content,
                    created_at=msg.created_at.isoformat(),
                    citations=self._parse_citations(msg.citations),
                    meta_data=self._parse_metadata(msg.meta_data),
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

    @strawberry.field
    async def search_documents(self, input: SearchInput) -> SearchResultType:
        """ドキュメント検索"""
        start_time = time.time()

        async for db in get_db():
            rag_service = RAGService(db)

            # フィルタをJSONから辞書に変換
            filters = None
            if input.filters:
                try:
                    filters = json.loads(input.filters)
                except json.JSONDecodeError:
                    filters = None

            # ドキュメント検索実行
            results = await rag_service.search_documents(
                query=input.query,
                top_k=input.top_k or 10,
                filters=filters,
            )

            # 結果をGraphQL型に変換
            documents = []
            for result in results:
                metadata = DocumentMetadataType(
                    file_type=result["metadata"]["file_type"],
                    file_size=result["metadata"]["file_size"],
                    created_at=result["metadata"]["created_at"],
                    chunk_index=result["metadata"]["chunk_index"],
                    chunk_count=result["metadata"]["chunk_count"],
                )

                document = DocumentType(
                    id=result["id"],
                    title=result["title"],
                    content=result["content"],
                    score=result["score"],
                    source=result["source"],
                    url=result["url"],
                    metadata=metadata,
                )
                documents.append(document)

            execution_time_ms = int((time.time() - start_time) * 1000)

            return SearchResultType(
                query=input.query,
                total_count=len(documents),
                documents=documents,
                execution_time_ms=execution_time_ms,
            )

        # Fallback return for mypy
        return SearchResultType(
            query=input.query,
            total_count=0,
            documents=[],
            execution_time_ms=0,
        )

    def _parse_citations(self, citations_json: Optional[str]) -> List[CitationType]:
        """引用情報JSONを構造化データに変換"""
        if not citations_json:
            return []

        try:
            citations_data = json.loads(citations_json)
            return [
                CitationType(
                    id=citation.get("id", 0),
                    title=citation.get("title", ""),
                    content=citation.get("content", ""),
                    score=citation.get("score", 0.0),
                    source=citation.get("source", ""),
                    url=citation.get("url", ""),
                )
                for citation in citations_data
            ]
        except (json.JSONDecodeError, TypeError):
            return []

    def _parse_metadata(self, metadata_json: Optional[str]) -> Any:
        """メタデータJSONをパース（JSON型として返却）"""
        if not metadata_json:
            return {}

        try:
            return json.loads(metadata_json)
        except (json.JSONDecodeError, TypeError):
            return {}
