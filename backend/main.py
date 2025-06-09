"""
QRAI MVP API メインアプリケーション
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

from api.resolvers import Query, Mutation, Subscription


logger = structlog.get_logger(__name__)


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

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.azurestaticapps.net"],
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
    return {"message": "QRAI MVP API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
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
