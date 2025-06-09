"""
QRAI MVP API メインアプリケーション
"""

import strawberry
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from contextlib import asynccontextmanager
import structlog
from datetime import datetime

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
