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
from api.types.session import (
    SessionListInput,
    SessionListResult,
)
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
        """セッション一覧取得（従来版・後方互換性維持）"""
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
                                citations=Query._parse_citations(msg.citations),
                                meta_data=Query._parse_metadata(msg.meta_data),
                            )
                            for msg in session.messages[
                                :3
                            ]  # 最新3件のみ（パフォーマンス改善）
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
    async def sessions_filtered(self, input: SessionListInput) -> SessionListResult:
        """フィルタリング・ソート機能付きセッション一覧取得"""
        async for db in get_db():
            session_service = SessionService(db)

            # 入力パラメータを解析
            search_query = None
            created_after = None
            created_before = None
            has_messages = None

            if input.filter:
                search_query = input.filter.search_query

                # 日時文字列をdatetimeに変換
                if input.filter.created_after:
                    try:
                        created_after = datetime.fromisoformat(
                            input.filter.created_after.replace("Z", "+00:00")
                        )
                    except ValueError:
                        pass

                if input.filter.created_before:
                    try:
                        created_before = datetime.fromisoformat(
                            input.filter.created_before.replace("Z", "+00:00")
                        )
                    except ValueError:
                        pass

                has_messages = input.filter.has_messages

            # ソート設定
            sort_field = "created_at"
            sort_order = "desc"

            if input.sort:
                sort_field = input.sort.field.value
                sort_order = input.sort.order.value

            # フィルタリング実行
            result = await session_service.get_sessions_filtered(
                search_query=search_query,
                created_after=created_after,
                created_before=created_before,
                has_messages=has_messages,
                sort_field=sort_field,
                sort_order=sort_order,
                limit=input.limit,
                offset=input.offset,
                include_messages=input.include_messages,
            )

            # GraphQL型に変換
            session_types = []
            for session in result["sessions"]:
                messages = []
                if input.include_messages and hasattr(session, "messages"):
                    messages = [
                        MessageType(
                            id=msg.id,
                            session_id=session.id,
                            role=GraphQLMessageRole(msg.role.value),
                            content=msg.content,
                            created_at=msg.created_at.isoformat(),
                            citations=Query._parse_citations(msg.citations),
                            meta_data=Query._parse_metadata(msg.meta_data),
                        )
                        for msg in session.messages[
                            :3
                        ]  # 最新3件まで（パフォーマンス改善）
                    ]

                session_types.append(
                    SessionType(
                        id=session.id,
                        title=session.title,
                        created_at=session.created_at.isoformat(),
                        updated_at=(
                            session.updated_at.isoformat()
                            if session.updated_at
                            else None
                        ),
                        messages=messages,
                    )
                )

            return SessionListResult(
                sessions=session_types,
                total_count=result["total_count"],
                has_more=result["has_more"],
            )

        # Fallback return for mypy
        return SessionListResult(
            sessions=[],
            total_count=0,
            has_more=False,
        )

    @strawberry.field
    async def search_sessions(self, query: str, limit: int = 20) -> List[SessionType]:
        """セッション検索（簡易版）"""
        async for db in get_db():
            session_service = SessionService(db)
            sessions = await session_service.search_sessions(query, limit)

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
                    session_id=session.id,
                    role=GraphQLMessageRole(msg.role.value),
                    content=msg.content,
                    created_at=msg.created_at.isoformat(),
                    citations=Query._parse_citations(msg.citations),
                    meta_data=Query._parse_metadata(msg.meta_data),
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

    @staticmethod
    def _parse_citations(citations_json: Optional[str]) -> List[CitationType]:
        """引用情報JSONを構造化データに変換"""
        if not citations_json:
            return []

        try:
            citations_data = json.loads(citations_json)
            return [
                CitationType(
                    id=citation.get("id", idx + 1),  # idフィールドを追加
                    title=citation.get("title", ""),
                    content=citation.get("content", ""),  # contentフィールドを追加
                    url=citation.get("url", ""),
                    source=citation.get("source", ""),
                    score=citation.get("score", 0.0),
                )
                for idx, citation in enumerate(citations_data)
                if isinstance(citation, dict)
            ]
        except (json.JSONDecodeError, AttributeError):
            return []

    @staticmethod
    def _parse_metadata(metadata_json: Optional[str]) -> Any:
        """メタデータJSONを構造化データに変換"""
        if not metadata_json:
            return None

        try:
            return json.loads(metadata_json)
        except json.JSONDecodeError:
            return None
