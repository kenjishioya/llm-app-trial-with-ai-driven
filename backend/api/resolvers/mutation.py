"""
GraphQL Mutation リゾルバ
"""

import strawberry
import uuid
import json
import base64
from typing import Optional

from api.types import SessionType, SessionInput, AskInput, AskPayload
from api.types.document import UploadDocumentInput, UploadDocumentPayload
from services import SessionService, RAGService
from services.document_pipeline import DocumentPipeline
from deps import get_db


@strawberry.type
class Mutation:
    """GraphQL Mutation"""

    @strawberry.mutation
    async def create_session(self, input: SessionInput) -> SessionType:
        """セッション作成"""
        async for db in get_db():
            session_service = SessionService(db)
            session = await session_service.create_session(input.title)

            return SessionType(
                id=session.id,
                title=session.title,
                created_at=session.created_at.isoformat(),
                updated_at=(
                    session.updated_at.isoformat() if session.updated_at else None
                ),
                messages=[],
            )
        # Fallback for mypy
        raise RuntimeError("Database session not available")

    @strawberry.mutation
    async def update_session(
        self, id: str, input: SessionInput
    ) -> Optional[SessionType]:
        """セッション更新"""
        async for db in get_db():
            session_service = SessionService(db)
            session = await session_service.update_session(id, input.title)

            if not session:
                return None

            return SessionType(
                id=session.id,
                title=session.title,
                created_at=session.created_at.isoformat(),
                updated_at=(
                    session.updated_at.isoformat() if session.updated_at else None
                ),
                messages=[],
            )
        return None  # Fallback for mypy

    @strawberry.mutation
    async def delete_session(self, id: str) -> bool:
        """セッション削除"""
        async for db in get_db():
            session_service = SessionService(db)
            return await session_service.delete_session(id)
        return False  # Fallback for mypy

    @strawberry.mutation
    async def ask(self, input: AskInput) -> AskPayload:
        """質問を送信して回答を取得"""
        async for db in get_db():
            rag_service = RAGService(db)

            # セッションIDがあればUUIDに変換
            session_id = None
            if input.session_id:
                try:
                    session_id = uuid.UUID(input.session_id)
                except ValueError:
                    raise ValueError("Invalid session ID format")

            # 質問処理
            result = await rag_service.ask_question(
                question=input.question,
                session_id=session_id,
                deep_research=input.deep_research,
            )

            # ストリーム用エンドポイントURL生成
            stream_url = f"/graphql/stream?id={result['message_id']}"

            return AskPayload(
                session_id=result["session_id"],
                message_id=result["message_id"],
                stream=stream_url,
            )
        # Fallback for mypy
        raise RuntimeError("Database session not available")

    @strawberry.mutation
    async def upload_document(
        self, input: UploadDocumentInput
    ) -> UploadDocumentPayload:
        """ドキュメントアップロード"""
        try:
            # Base64デコード
            try:
                file_content = base64.b64decode(input.file_content)
            except Exception as decode_error:
                return UploadDocumentPayload(
                    document_id="",
                    file_name=input.file_name,
                    status="error",
                    message=f"Base64デコードエラー: {str(decode_error)}",
                    chunks_created=0,
                )

            # メタデータをJSONから辞書に変換
            metadata = {}
            if input.metadata:
                try:
                    metadata = json.loads(input.metadata)
                except json.JSONDecodeError:
                    metadata = {}

            # ドキュメント処理パイプライン実行
            pipeline = DocumentPipeline()

            result = await pipeline.process_document(
                file_content=file_content,
                filename=input.file_name,
                content_type=input.file_type,
                metadata=metadata,
            )

            # ProcessingResultオブジェクトから値を取得
            return UploadDocumentPayload(
                document_id=result.document_id,
                file_name=input.file_name,
                status="success" if not result.errors else "error",
                message=(
                    "ドキュメントが正常にアップロードされました"
                    if not result.errors
                    else f"エラー: {'; '.join(result.errors)}"
                ),
                chunks_created=result.chunks_count,
            )

        except Exception as e:
            return UploadDocumentPayload(
                document_id="",
                file_name=input.file_name,
                status="error",
                message=f"アップロードエラー: {str(e)}",
                chunks_created=0,
            )
