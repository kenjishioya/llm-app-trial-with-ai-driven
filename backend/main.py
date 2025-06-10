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
import structlog
from datetime import datetime
import asyncio
import json
import sys

from api.resolvers import Query, Mutation, Subscription
from config import get_settings  # type: ignore
from pydantic import ValidationError


logger = structlog.get_logger(__name__)

# 設定検証とロード
try:
    settings = get_settings()
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
    id: str = FastAPIQuery(..., description="Message ID for streaming")
):
    """GraphQL SSE ストリーミングエンドポイント"""

    async def generate_stream():
        """SSE ストリーム生成"""
        # SSE ヘッダー
        yield "data: " + json.dumps({"type": "connection_init"}) + "\n\n"

        # メッセージ処理開始
        yield "data: " + json.dumps(
            {"type": "message", "messageId": id, "status": "processing"}
        ) + "\n\n"

        # シミュレートされた応答チャンク
        response_chunks = [
            "こんにちは、",
            "ご質問にお答えします。",
            "\n\nMVP版のストリーミング機能が",
            "正常に動作しています。",
        ]

        for chunk in response_chunks:
            await asyncio.sleep(0.1)  # 実際の処理を模擬
            yield "data: " + json.dumps(
                {"type": "chunk", "messageId": id, "content": chunk}
            ) + "\n\n"

        # 完了通知
        yield "data: " + json.dumps({"type": "complete", "messageId": id}) + "\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        },
    )
