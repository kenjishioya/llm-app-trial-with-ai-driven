"""
サービス層ユニットテスト（モック使用）
"""

import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from services.session_service import SessionService
from services.rag_service import RAGService
from models.session import Session
from tests.mocks.llm_mock import MockLLMService, MockLLMResponse


class TestLLMService:
    """LLMサービスのユニットテスト"""

    @pytest.fixture
    def mock_llm_service(self):
        """LLMサービスのモック"""
        return MockLLMService("テスト用の固定回答です。")

    @pytest.mark.asyncio
    async def test_generate_response(self, mock_llm_service):
        """回答生成のテスト"""
        prompt = "テストプロンプトです"
        response = await mock_llm_service.generate_response(prompt)

        assert isinstance(response, MockLLMResponse)
        assert response.content == "テスト用の固定回答です。"
        assert response.provider == "mock"
        assert response.model == "mock-test-model"
        assert mock_llm_service.call_count == 1
        assert mock_llm_service.last_prompt == prompt

    @pytest.mark.asyncio
    async def test_generate_response_dynamic(self, mock_llm_service):
        """動的回答生成のテスト"""
        prompt = "こんにちは、元気ですか？"
        response = await mock_llm_service.generate_response(prompt)

        assert "こんにちは！元気です" in response.content
        assert "テスト用の回答" in response.content

    @pytest.mark.asyncio
    async def test_stream_response(self, mock_llm_service):
        """ストリーミング回答のテスト"""
        prompt = "ストリーミングテスト"
        chunks = []

        async for chunk in mock_llm_service.stream_response(prompt):
            chunks.append(chunk)

        assert len(chunks) > 0
        # 全チャンクを結合すると元のレスポンスになる
        full_content = "".join(chunk.content for chunk in chunks)
        assert "テスト用の固定回答です。" == full_content

    @pytest.mark.asyncio
    async def test_health_check(self, mock_llm_service):
        """ヘルスチェックのテスト"""
        result = await mock_llm_service.health_check()
        assert result is True

    def test_get_provider_info(self, mock_llm_service):
        """プロバイダー情報取得のテスト"""
        info = mock_llm_service.get_provider_info()
        assert info["provider"] == "MockLLMService"
        assert info["available"] is True
        assert info["call_count"] == 0


class TestSessionService:
    """セッションサービスのユニットテスト"""

    @pytest.fixture
    def mock_db(self):
        """モックDBセッション"""
        mock_db = AsyncMock(spec=AsyncSession)
        return mock_db

    @pytest.fixture
    def session_service(self, mock_db):
        """セッションサービス"""
        return SessionService(mock_db)

    @pytest.mark.asyncio
    async def test_create_session(self, session_service, mock_db):
        """セッション作成のテスト"""
        # モック設定
        mock_session = Session(id=str(uuid.uuid4()), title="Test Session")
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        # セッション作成をモック
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr("models.session.Session", lambda title: mock_session)
            await session_service.create_session("Test Session")

        # 検証
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_session(self, session_service, mock_db):
        """セッション取得のテスト"""
        session_id = str(uuid.uuid4())
        mock_session = Session(id=session_id, title="Test Session")

        # モック結果を設定
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_session
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await session_service.get_session(session_id)

        # 検証
        mock_db.execute.assert_called_once()
        assert result == mock_session


class TestRAGService:
    """RAGサービスのユニットテスト"""

    @pytest.fixture
    def mock_db(self):
        """モックDBセッション"""
        mock_db = AsyncMock(spec=AsyncSession)
        return mock_db

    @pytest.fixture
    def mock_session_service(self):
        """モックセッションサービス"""
        service = AsyncMock()
        service.get_session.return_value = Session(
            id=str(uuid.uuid4()), title="Test Session"
        )
        return service

    @pytest.fixture
    def mock_llm_service(self):
        """モックLLMサービス"""
        return MockLLMService("RAGテスト用の回答です。")

    @pytest.fixture
    def rag_service(self, mock_db, monkeypatch):
        """RAGサービス（モック適用済み）"""
        # SessionServiceとLLMServiceをモックに置き換え
        mock_session_service = AsyncMock()
        mock_session_service.get_session.return_value = Session(
            id=str(uuid.uuid4()), title="Test Session"
        )

        mock_llm_service = MockLLMService("RAGテスト用の回答です。")

        monkeypatch.setattr(
            "services.rag_service.SessionService", lambda db: mock_session_service
        )
        monkeypatch.setattr("services.rag_service.LLMService", lambda: mock_llm_service)

        return RAGService(mock_db)

    @pytest.mark.asyncio
    async def test_ask_question_success(self, rag_service, mock_db):
        """質問回答の成功テスト"""
        question = "テスト質問です"
        session_id = uuid.uuid4()

        # モック設定
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        # テスト実行
        result = await rag_service.ask_question(question, session_id)

        # 検証
        assert "answer" in result
        assert result["session_id"] == str(session_id)
        assert "message_id" in result
        assert "metadata" in result

        # DBメソッドが適切に呼ばれたか
        assert mock_db.add.call_count == 2  # user_message + assistant_message
        assert mock_db.commit.call_count == 2
        assert mock_db.refresh.call_count == 2

    @pytest.mark.asyncio
    async def test_ask_question_no_session_id(self, rag_service):
        """セッションID未指定時のエラーテスト"""
        question = "テスト質問です"

        with pytest.raises(ValueError, match="Session ID is required"):
            await rag_service.ask_question(question, session_id=None)

    @pytest.mark.asyncio
    async def test_stream_answer_success(self, rag_service, mock_db):
        """ストリーミング回答の成功テスト"""
        question = "ストリーミングテスト質問です"
        session_id = uuid.uuid4()

        # モック設定
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        chunks = []
        async for chunk in rag_service.stream_answer(question, session_id):
            chunks.append(chunk)

        # 検証
        assert len(chunks) > 0

        # 最後のchunkがcomplete=Trueになっているか
        last_chunk = chunks[-1]
        assert last_chunk.get("is_complete") is True
        assert last_chunk.get("session_id") == str(session_id)

        # 中間chunkがcomplete=Falseになっているか
        for chunk in chunks[:-1]:
            assert chunk.get("is_complete") is False

    @pytest.mark.asyncio
    async def test_get_message_history(self, rag_service):
        """メッセージ履歴取得のテスト"""
        session_id = uuid.uuid4()

        # テスト実行
        result = await rag_service.get_message_history(session_id)

        # 空の履歴が返されることを確認（モック環境）
        assert isinstance(result, list)
