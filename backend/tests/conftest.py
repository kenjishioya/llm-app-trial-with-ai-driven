"""
pytest設定とフィクスチャ - CI修正版 同期統一 2025-06-10
"""

import pytest
import tempfile
import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# PythonPathを動的に追加（CI環境対応）
backend_path = Path(__file__).parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from main import app  # noqa: E402
from models import Base  # noqa: E402

# モデルクラスを明示的にインポート（テーブル作成のため）
from models.session import Session  # noqa: E402, F401
from models.message import Message  # noqa: E402, F401


@pytest.fixture
def db_session():
    """テスト用データベースセッション（同期・独立）"""
    # 一時SQLiteファイル作成
    test_db_fd, test_db_path = tempfile.mkstemp(suffix=".db")
    os.close(test_db_fd)

    # 同期エンジン作成
    engine = create_engine(
        f"sqlite:///{test_db_path}",
        echo=False,
        connect_args={"check_same_thread": False},
    )

    # テーブル作成（同期）
    print(f"Creating tables for database: {test_db_path}")
    print(f"Available tables in metadata: {list(Base.metadata.tables.keys())}")

    # SQLAlchemy metadata からテーブル作成
    Base.metadata.create_all(bind=engine)

    # Alembicマイグレーションも実行（確実にテーブル作成）
    try:
        from alembic.config import Config
        from alembic import command

        # 一時的なalembic.iniを作成
        alembic_cfg = Config()
        alembic_cfg.set_main_option("script_location", "migrations")
        alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{test_db_path}")

        # マイグレーション実行
        command.upgrade(alembic_cfg, "head")
        print("Alembic migration completed successfully")
    except Exception as e:
        print(f"Alembic migration failed: {e}")
        # Alembicが失敗してもテストは継続
        pass

    print("Tables created successfully")

    # セッション作成
    SessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    session = SessionLocal()
    session._test_db_path = test_db_path

    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.rollback()
        session.close()
        engine.dispose()

        # SQLiteファイル削除
        if os.path.exists(test_db_path):
            os.unlink(test_db_path)


@pytest.fixture
def client(db_session):
    """テスト用HTTPクライアント（同期対応）"""

    # 同期セッションを非同期セッションに変換するラッパー
    class AsyncSessionWrapper:
        def __init__(self, sync_session):
            self._sync_session = sync_session

        async def add(self, instance):
            self._sync_session.add(instance)

        async def commit(self):
            self._sync_session.commit()

        async def rollback(self):
            self._sync_session.rollback()

        async def refresh(self, instance):
            self._sync_session.refresh(instance)

        async def delete(self, instance):
            self._sync_session.delete(instance)

        def query(self, *args, **kwargs):
            return self._sync_session.query(*args, **kwargs)

        async def execute(self, stmt):
            return self._sync_session.execute(stmt)

        async def get(self, entity, ident):
            return self._sync_session.get(entity, ident)

        async def merge(self, instance):
            return self._sync_session.merge(instance)

        async def close(self):
            self._sync_session.close()

    # 非同期セッション依存関係のオーバーライド
    async def override_get_db():
        wrapper = AsyncSessionWrapper(db_session)
        try:
            yield wrapper
        finally:
            await wrapper.close()

    from database import get_db

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
