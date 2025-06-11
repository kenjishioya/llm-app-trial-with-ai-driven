"""
QRAI MVP API メインアプリケーション
Phase 1.5D2: 起動時設定検証統合
"""

import strawberry
from fastapi import FastAPI, Query as FastAPIQuery
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from strawberry.fastapi import GraphQLRouter
from contextlib import asynccontextmanager
from datetime import datetime
import json
import sys

from api.resolvers import Query, Mutation, Subscription
from config import get_settings  # type: ignore
from pydantic import ValidationError
from utils.logging import setup_logging, get_logger

# 設定検証とロード
try:
    settings = get_settings()

    # ログ設定初期化
    setup_logging(
        log_level=settings.log_level,
        environment=settings.environment,
        structured=True,
    )

    logger = get_logger(__name__)
    logger.info("✅ 環境設定検証完了", environment=settings.environment)
except ValidationError as e:
    logger.error("❌ 環境設定検証エラー", errors=[error["msg"] for error in e.errors()])
    sys.exit(1)
except Exception as e:
    logger.error("❌ 環境設定エラー", error=str(e))
    sys.exit(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションライフサイクル管理"""
    logger.info("Starting QRAI API", version="0.1.0")

    # データベーステーブル自動作成
    try:
        from database import engine
        from models import Base

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ データベーステーブル初期化完了")
    except Exception as e:
        logger.error("❌ データベーステーブル初期化エラー", error=str(e))

    yield
    logger.info("Shutting down QRAI API")


# FastAPIアプリケーション作成
app = FastAPI(
    title="QRAI MVP API",
    description="QRAI MVP GraphQL API with RAG capabilities",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS設定（環境設定から動的取得）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins_list(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# GraphQLスキーマ作成
schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription)

# GraphQLルーター設定
graphql_app = GraphQLRouter(schema, path="/graphql")

app.include_router(graphql_app, prefix="")


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    # APIキー設定状況
    api_status = settings.validate_api_keys()
    configured_apis = [api for api, status in api_status.items() if status]

    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "environment": settings.environment,
        "app_name": settings.app_name,
        "version": settings.app_version,
        "database": settings.get_database_info()["scheme"],
        "configured_apis": configured_apis,
        "debug_mode": settings.debug,
    }


@app.get("/graphql/stream")
async def graphql_stream(
    id: str = FastAPIQuery(..., description="Message ID for streaming"),
    sessionId: str = FastAPIQuery(None, description="Session ID for streaming"),
):
    """GraphQL SSE ストリーミングエンドポイント"""

    async def generate_stream():
        """SSE ストリーム生成"""
        try:
            # データベース接続取得
            from deps import get_db
            from services import RAGService

            async for db in get_db():
                rag_service = RAGService(db)

                # SSE ヘッダー
                yield "data: " + json.dumps({"type": "connection_init"}) + "\n\n"

                # メッセージIDからメッセージ情報を取得
                from models.message import Message
                from sqlalchemy import select

                stmt = select(Message).where(Message.id == id)
                result = await db.execute(stmt)
                message = result.scalar_one_or_none()

                if not message:
                    yield "data: " + json.dumps(
                        {"type": "error", "messageId": id, "error": "Message not found"}
                    ) + "\n\n"
                    return

                # メッセージ処理開始
                yield "data: " + json.dumps(
                    {"type": "message", "messageId": id, "status": "processing"}
                ) + "\n\n"

                # RAGServiceでストリーミング開始
                # セッションIDをUUIDに変換
                import uuid

                session_uuid = uuid.UUID(message.session_id)

                # ストリーミング処理
                async for chunk in rag_service.stream_answer(
                    question=message.content,
                    session_id=session_uuid,
                    deep_research=False,
                ):
                    if "error" in chunk:
                        yield "data: " + json.dumps(
                            {"type": "error", "messageId": id, "error": chunk["error"]}
                        ) + "\n\n"
                        break
                    elif chunk.get("chunk"):
                        yield "data: " + json.dumps(
                            {
                                "type": "chunk",
                                "messageId": id,
                                "content": chunk["chunk"],
                            }
                        ) + "\n\n"

                    if chunk.get("is_complete"):
                        # 完了通知
                        yield "data: " + json.dumps(
                            {"type": "complete", "messageId": id}
                        ) + "\n\n"
                        break

        except Exception as e:
            logger.error("❌ SSE ストリーミングエラー", error=str(e), message_id=id)
            yield "data: " + json.dumps(
                {"type": "error", "messageId": id, "error": "Internal server error"}
            ) + "\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        },
    )
