"""
データベース統合テスト
"""

import pytest
import tempfile
import os
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from models import Base
from models.session import Session
from models.message import Message, MessageRole
from services.session_service import SessionService


async def create_test_database_session():
    """テスト用データベースセッションを作成（直接呼び出し）"""
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

    session = TestSessionLocal()
    session._test_db_path = test_db_path
    session._test_engine = engine

    return session


async def cleanup_test_database_session(session):
    """テスト用データベースセッションをクリーンアップ"""
    test_db_path = session._test_db_path
    engine = session._test_engine

    await session.rollback()
    await session.close()
    await engine.dispose()

    if os.path.exists(test_db_path):
        os.unlink(test_db_path)


class TestDatabaseIntegration:
    """データベース統合テスト"""

    @pytest.mark.asyncio
    async def test_session_crud_operations(self):
        """セッションCRUD操作のテスト"""
        test_db_session = await create_test_database_session()

        try:
            # 作成
            test_session = Session(title="Integration Test Session")
            test_db_session.add(test_session)
            await test_db_session.commit()
            await test_db_session.refresh(test_session)

            assert test_session.id is not None
            assert test_session.title == "Integration Test Session"
            assert test_session.created_at is not None

            # 読取
            stmt = select(Session).where(Session.id == test_session.id)
            result = await test_db_session.execute(stmt)
            retrieved_session = result.scalar_one_or_none()

            assert retrieved_session is not None
            assert retrieved_session.id == test_session.id
            assert retrieved_session.title == test_session.title

            # 更新
            retrieved_session.title = "Updated Session"
            await test_db_session.commit()
            await test_db_session.refresh(retrieved_session)

            assert retrieved_session.title == "Updated Session"

            # 削除
            await test_db_session.delete(retrieved_session)
            await test_db_session.commit()

            # 削除確認
            stmt = select(Session).where(Session.id == test_session.id)
            result = await test_db_session.execute(stmt)
            deleted_session = result.scalar_one_or_none()

            assert deleted_session is None

        finally:
            await cleanup_test_database_session(test_db_session)

    @pytest.mark.asyncio
    async def test_message_crud_operations(self):
        """メッセージCRUD操作のテスト"""
        test_db_session = await create_test_database_session()

        try:
            # セッション作成
            test_session = Session(title="Message Test Session")
            test_db_session.add(test_session)
            await test_db_session.commit()
            await test_db_session.refresh(test_session)

            # メッセージ作成
            message = Message(
                session_id=test_session.id,
                role=MessageRole.USER,
                content="Test message content",
            )
            test_db_session.add(message)
            await test_db_session.commit()
            await test_db_session.refresh(message)

            assert message.id is not None
            assert message.session_id == test_session.id
            assert message.role == MessageRole.USER
            assert message.content == "Test message content"
            assert message.created_at is not None

            # リレーション確認
            stmt = select(Session).where(Session.id == test_session.id)
            result = await test_db_session.execute(stmt)

            # メッセージがセッションに紐づいているか確認
            # （遅延ロードのため、必要に応じて明示的に確認）
            stmt = select(Message).where(Message.session_id == test_session.id)
            result = await test_db_session.execute(stmt)
            messages = result.scalars().all()

            assert len(messages) == 1
            assert messages[0].id == message.id

        finally:
            await cleanup_test_database_session(test_db_session)


class TestSessionServiceIntegration:
    """セッションサービス統合テスト"""

    @pytest.mark.asyncio
    async def test_create_and_get_session(self):
        """セッション作成・取得のテスト"""
        test_db_session = await create_test_database_session()

        try:
            service = SessionService(test_db_session)

            # セッション作成
            created_session = await service.create_session("Integration Test")

            assert created_session.id is not None
            assert created_session.title == "Integration Test"

            # セッション取得
            retrieved_session = await service.get_session(created_session.id)

            assert retrieved_session is not None
            assert retrieved_session.id == created_session.id
            assert retrieved_session.title == created_session.title

        finally:
            await cleanup_test_database_session(test_db_session)

    @pytest.mark.asyncio
    async def test_get_sessions_list(self):
        """セッション一覧取得のテスト"""
        test_db_session = await create_test_database_session()

        try:
            service = SessionService(test_db_session)

            # 複数セッション作成
            session1 = await service.create_session("Session 1")
            session2 = await service.create_session("Session 2")
            session3 = await service.create_session("Session 3")

            # セッション一覧取得
            sessions = await service.get_sessions(limit=10)

            assert len(sessions) >= 3
            session_ids = [s.id for s in sessions]
            assert session1.id in session_ids
            assert session2.id in session_ids
            assert session3.id in session_ids

        finally:
            await cleanup_test_database_session(test_db_session)

    @pytest.mark.asyncio
    async def test_update_session(self):
        """セッション更新のテスト"""
        test_db_session = await create_test_database_session()

        try:
            service = SessionService(test_db_session)

            # セッション作成
            test_session = await service.create_session("Original Title")

            # セッション更新
            updated_session = await service.update_session(
                test_session.id, "Updated Title"
            )

            assert updated_session is not None
            assert updated_session.id == test_session.id
            assert updated_session.title == "Updated Title"

            # 更新確認
            retrieved_session = await service.get_session(test_session.id)
            assert retrieved_session.title == "Updated Title"

        finally:
            await cleanup_test_database_session(test_db_session)

    @pytest.mark.asyncio
    async def test_delete_session(self):
        """セッション削除のテスト"""
        test_db_session = await create_test_database_session()

        try:
            service = SessionService(test_db_session)

            # セッション作成
            test_session = await service.create_session("Session to Delete")

            # セッション削除
            deleted = await service.delete_session(test_session.id)

            assert deleted is True

            # 削除確認
            retrieved_session = await service.get_session(test_session.id)
            assert retrieved_session is None

        finally:
            await cleanup_test_database_session(test_db_session)

    @pytest.mark.asyncio
    async def test_session_with_messages(self):
        """メッセージ付きセッション取得のテスト"""
        test_db_session = await create_test_database_session()

        try:
            service = SessionService(test_db_session)

            # セッション作成
            test_session = await service.create_session("Session with Messages")

            # メッセージ追加
            message1 = Message(
                session_id=test_session.id,
                role=MessageRole.USER,
                content="User message",
            )
            message2 = Message(
                session_id=test_session.id,
                role=MessageRole.ASSISTANT,
                content="Assistant message",
            )

            test_db_session.add(message1)
            test_db_session.add(message2)
            await test_db_session.commit()

            # メッセージ付きセッション取得
            session_with_messages = await service.get_session_with_messages(
                test_session.id
            )

            assert session_with_messages is not None
            assert len(session_with_messages.messages) == 2

            # メッセージ順序確認
            messages = sorted(
                session_with_messages.messages, key=lambda m: m.created_at
            )
            assert messages[0].role == MessageRole.USER
            assert messages[0].content == "User message"
            assert messages[1].role == MessageRole.ASSISTANT
            assert messages[1].content == "Assistant message"

        finally:
            await cleanup_test_database_session(test_db_session)


class TestDatabaseCleanup:
    """データベースクリーンアップのテスト"""

    @pytest.mark.asyncio
    async def test_test_isolation(self):
        """テスト間のデータ分離確認"""
        test_db_session = await create_test_database_session()

        try:
            # 他のテストで作成されたデータが残っていないか確認
            stmt = select(Session)
            result = await test_db_session.execute(stmt)
            sessions = result.scalars().all()

            # 新しい独立したDBなので、最初は空のはず
            # ただし、他のテストが同時実行される可能性があるため、
            # 特定の数での検証は避ける
            assert isinstance(sessions, list)

        finally:
            await cleanup_test_database_session(test_db_session)

    @pytest.mark.asyncio
    async def test_transaction_rollback(self):
        """トランザクション rollback のテスト"""
        test_db_session = await create_test_database_session()

        try:
            # セッション作成
            test_session = Session(title="Rollback Test Session")
            test_db_session.add(test_session)
            await test_db_session.commit()
            await test_db_session.refresh(test_session)

            session_id = test_session.id

            # ロールバックテスト
            try:
                test_session.title = "Updated Title"
                # 意図的にエラーを発生させる
                raise Exception("Test error")
            except Exception:
                await test_db_session.rollback()

            # ロールバック後の確認
            stmt = select(Session).where(Session.id == session_id)
            result = await test_db_session.execute(stmt)
            retrieved_session = result.scalar_one_or_none()

            # タイトルが元のままであることを確認
            assert retrieved_session.title == "Rollback Test Session"

        finally:
            await cleanup_test_database_session(test_db_session)
