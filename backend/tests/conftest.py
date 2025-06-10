"""
pytest設定とフィクスチャ - CI修正版 2025-06-10
"""

import pytest
import asyncio
import tempfile
import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# PythonPathを動的に追加（CI環境対応）
backend_path = Path(__file__).parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from main import app  # noqa: E402
from models import Base  # noqa: E402
from database import get_db  # noqa: E402


@pytest.fixture(scope="session")
def event_loop():
    """テスト用イベントループ"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# データベースエンジンとセッションファクトリー管理
_test_engines = {}
_test_sessionmakers = {}


async def create_test_session() -> AsyncSession:
    """独立したテスト用データベースセッションを作成"""
    # 常に一時SQLiteを使用（CI/ローカル両対応）
    test_db_fd, test_db_path = tempfile.mkstemp(suffix=".db")
    os.close(test_db_fd)

    engine = create_async_engine(
        f"sqlite+aiosqlite:///{test_db_path}",
        echo=False,
        future=True,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={"check_same_thread": False},
    )

    # テーブル作成
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # セッションファクトリー作成
    TestSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

    # リソース管理用にID保存
    test_id = id(engine)
    _test_engines[test_id] = engine
    _test_sessionmakers[test_id] = TestSessionLocal

    session = TestSessionLocal()
    session._test_db_path = test_db_path
    session._test_id = test_id

    return session


@pytest.fixture
async def db_session():
    """テスト用データベースセッション（各テスト独立）"""
    session = await create_test_session()

    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        # クリーンアップ
        test_id = session._test_id
        test_db_path = session._test_db_path

        await session.rollback()
        await session.close()

        # エンジンとファクトリークリーンアップ
        if test_id in _test_engines:
            engine = _test_engines.pop(test_id)
            await engine.dispose()

        if test_id in _test_sessionmakers:
            _test_sessionmakers.pop(test_id)

        # SQLiteファイル削除
        if os.path.exists(test_db_path):
            os.unlink(test_db_path)


@pytest.fixture
def client(db_session):
    """テスト用HTTPクライアント"""

    # データベースセッションを上書き
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def mock_llm_provider():
    """モックLLMプロバイダー（高速化設定）"""
    from providers.mock import MockLLMProvider

    return MockLLMProvider(response_delay=0.001)


@pytest.fixture
def patch_llm_service(monkeypatch, mock_llm_provider):
    """LLMServiceをモックに置き換える"""

    # モックLLMサービスクラスを作成
    class MockLLMService:
        def __init__(self):
            self.provider = mock_llm_provider

        async def generate_response(
            self,
            prompt: str,
            system_message=None,
            max_tokens: int = 1000,
            temperature: float = 0.7,
        ):
            return await self.provider.generate(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
            )

        async def stream_response(
            self,
            prompt: str,
            system_message=None,
            max_tokens: int = 1000,
            temperature: float = 0.7,
        ):
            # ストリーミングの代わりに単一レスポンスを返す
            response = await self.generate_response(
                prompt, system_message, max_tokens, temperature
            )
            yield response

        async def health_check(self):
            return True

        def get_provider_info(self):
            return {"provider": "MockLLMProvider", "available": True}

    # LLMServiceクラス自体をモックに置き換え
    monkeypatch.setattr("services.llm_service.LLMService", MockLLMService)
    monkeypatch.setattr("services.rag_service.LLMService", MockLLMService)

    return MockLLMService()
