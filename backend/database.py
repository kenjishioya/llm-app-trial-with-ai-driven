"""
データベース接続設定
PostgreSQL対応・接続プール最適化・ヘルスチェック機能付き
"""

import logging
import os
from typing import Any, AsyncGenerator, Dict

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.pool import StaticPool

logger = logging.getLogger(__name__)


def get_database_config() -> Dict[str, Any]:
    """環境に応じたデータベース設定を取得"""
    database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app.db")
    environment = os.getenv("ENVIRONMENT", "development")

    # 接続プール設定
    if database_url.startswith("postgresql"):
        # PostgreSQL: 非同期エンジン用設定
        pool_config: Dict[str, Any] = {
            "pool_size": 10,  # 基本接続数
            "max_overflow": 20,  # 追加接続数
            "pool_timeout": 30,  # 接続取得タイムアウト
            "pool_recycle": 3600,  # 接続再利用時間（1時間）
            "pool_pre_ping": True,  # 接続前ping確認
        }

        # 接続引数
        connect_args: Dict[str, Any] = {
            "server_settings": {
                "jit": "off",  # JIT無効化（安定性向上）
                "timezone": "Asia/Tokyo",
            },
        }

    elif database_url.startswith("sqlite"):
        # SQLite: 開発・テスト環境設定
        pool_config = {
            "poolclass": StaticPool,  # SQLiteは静的プール
            "pool_size": 1,  # SQLiteは単一接続
            "max_overflow": 0,
        }

        connect_args = {
            "check_same_thread": False,
            "timeout": 20,  # タイムアウト設定
        }

    else:
        raise ValueError(f"Unsupported database URL: {database_url}")

    return {
        "url": database_url,
        "pool_config": pool_config,
        "connect_args": connect_args,
        "echo": environment == "development",  # 開発時のみSQLログ出力
    }


# データベース設定
db_config = get_database_config()

# 非同期エンジン作成
engine = create_async_engine(
    db_config["url"],
    echo=db_config["echo"],
    future=True,
    connect_args=db_config["connect_args"],
    **db_config["pool_config"],
)

# セッションファクトリー
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """データベースセッション取得（依存性注入用）"""
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_database_health() -> Dict[str, Any]:
    """データベース接続ヘルスチェック"""
    try:
        async with engine.begin() as conn:
            # 基本接続テスト
            result = await conn.execute("SELECT 1 as health_check")
            health_result = result.scalar()

            # 接続プール状態取得
            pool = engine.pool
            pool_status = (
                {
                    "size": pool.size(),
                    "checked_in": pool.checkedin(),
                    "checked_out": pool.checkedout(),
                    "overflow": pool.overflow(),
                }
                if hasattr(pool, "size")
                else {"status": "No pool (SQLite)"}
            )

            return {
                "status": "healthy",
                "database_url": db_config["url"].split("@")[0] + "@***",
                "health_check_result": health_result,
                "pool_status": pool_status,
                "engine_echo": db_config["echo"],
            }

    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "database_url": db_config["url"].split("@")[0] + "@***",
        }


async def close_database() -> None:
    """データベース接続クローズ（アプリケーション終了時）"""
    try:
        await engine.dispose()
        logger.info("Database connections closed successfully")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")


# 初期化時ログ出力
logger.info(f"Database initialized: {db_config['url'].split('@')[0]}@***")
logger.info(f"Engine echo: {db_config['echo']}")
logger.info(f"Pool config: {db_config['pool_config']}")
