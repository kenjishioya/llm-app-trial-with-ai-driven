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


class TestSearchService:
    """SearchServiceのユニットテスト"""

    @pytest.fixture
    def mock_search_client(self):
        """モックSearchClient"""
        from unittest.mock import AsyncMock

        mock_client = AsyncMock()
        mock_client.search = AsyncMock()
        mock_client.get_document = AsyncMock()
        mock_client.upload_documents = AsyncMock()
        mock_client.delete_documents = AsyncMock()
        return mock_client

    @pytest.fixture
    def mock_index_client(self):
        """モックSearchIndexClient"""
        from unittest.mock import AsyncMock

        mock_client = AsyncMock()
        mock_client.get_service_statistics = AsyncMock()
        mock_client.get_index = AsyncMock()
        return mock_client

    @pytest.fixture
    def mock_settings(self):
        """モック設定"""
        from unittest.mock import MagicMock

        settings = MagicMock()
        settings.azure_search_endpoint = "https://test-search.search.windows.net"
        settings.azure_search_api_key = "test-api-key"  # pragma: allowlist secret
        settings.azure_search_index_name = "test-index"
        return settings

    @pytest.fixture
    def search_service(
        self, monkeypatch, mock_settings, mock_search_client, mock_index_client
    ):
        """SearchServiceインスタンス（モック適用済み）"""
        from services.search_service import SearchService

        # 設定をモックに置き換え
        monkeypatch.setattr(
            "services.search_service.get_settings", lambda: mock_settings
        )

        # SearchServiceインスタンス作成
        service = SearchService()

        # クライアントをモックに置き換え
        service.search_client = mock_search_client
        service.index_client = mock_index_client

        return service

    @pytest.mark.asyncio
    async def test_health_check_healthy(self, search_service, mock_index_client):
        """ヘルスチェック成功のテスト"""
        from unittest.mock import MagicMock

        # モックサービス統計を設定
        mock_stats = MagicMock()
        mock_stats.counters.document_count = 100
        mock_stats.counters.index_count = 5
        mock_stats.counters.indexer_count = 2
        mock_stats.counters.data_source_count = 3
        mock_stats.counters.storage_size = 1024000
        mock_stats.limits.max_indexes_allowed = 50
        mock_stats.limits.max_fields_per_index = 1000
        mock_stats.limits.max_complex_collection_fields_per_index = 40
        mock_stats.limits.max_complex_objects_in_collections_per_document = 100

        mock_index_client.get_service_statistics.return_value = mock_stats

        # テスト実行
        result = await search_service.health_check()

        # 検証
        assert result["status"] == "healthy"
        assert "service_stats" in result
        assert result["service_stats"]["counters"]["document_count"] == 100
        assert result["service_stats"]["limits"]["max_indexes_allowed"] == 50
        mock_index_client.get_service_statistics.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_unhealthy_no_clients(self):
        """クライアント未初期化時のヘルスチェックテスト"""
        from services.search_service import SearchService

        # クライアント未初期化のSearchService
        service = SearchService.__new__(SearchService)
        service.search_client = None
        service.index_client = None

        # テスト実行
        result = await service.health_check()

        # 検証
        assert result["status"] == "unhealthy"
        assert result["error"] == "Clients not initialized"
        assert result["details"]["search_client"] is False
        assert result["details"]["index_client"] is False

    @pytest.mark.asyncio
    async def test_search_documents_success(self, search_service, mock_search_client):
        """ドキュメント検索成功のテスト"""
        from unittest.mock import AsyncMock

        # モック検索結果を設定
        mock_result1 = {
            "@search.score": 0.95,
            "id": "doc1",
            "title": "Test Document 1",
            "content": "This is test content",
            "@search.highlights": {"title": ["<em>Test</em> Document 1"]},
        }
        mock_result2 = {
            "@search.score": 0.85,
            "id": "doc2",
            "title": "Test Document 2",
            "content": "Another test content",
            "@search.highlights": {},
        }

        # AsyncIteratorをモック
        async def mock_search_results():
            yield mock_result1
            yield mock_result2

        mock_results = AsyncMock()
        mock_results.__aiter__ = lambda self: mock_search_results()
        mock_results.get_count = lambda: 2

        mock_search_client.search.return_value = mock_results

        # テスト実行
        result = await search_service.search_documents(
            query="test query", top=10, select_fields=["id", "title", "content"]
        )

        # 検証
        assert len(result["documents"]) == 2
        assert result["query"] == "test query"
        assert result["total_count"] == 2

        # 最初のドキュメント検証
        first_doc = result["documents"][0]
        assert first_doc["score"] == 0.95
        assert first_doc["document"]["id"] == "doc1"
        assert first_doc["document"]["title"] == "Test Document 1"
        assert first_doc["highlights"]["title"] == ["<em>Test</em> Document 1"]

        # SearchClientが適切に呼ばれたか検証
        mock_search_client.search.assert_called_once_with(
            search_text="test query",
            top=10,
            skip=0,
            search_fields=None,
            select=["id", "title", "content"],
            filter=None,
            order_by=None,
            include_total_count=True,
        )

    @pytest.mark.asyncio
    async def test_search_documents_no_client(self):
        """SearchClient未初期化時のエラーテスト"""
        from services.search_service import SearchService, SearchServiceError

        # クライアント未初期化のSearchService
        service = SearchService.__new__(SearchService)
        service.search_client = None

        # テスト実行とエラー検証
        with pytest.raises(SearchServiceError, match="Search client not initialized"):
            await service.search_documents("test query")

    @pytest.mark.asyncio
    async def test_get_document_success(self, search_service, mock_search_client):
        """ドキュメント取得成功のテスト"""
        # モックドキュメントを設定
        mock_document = {
            "id": "test-doc-1",
            "title": "Test Document",
            "content": "This is test content",
        }
        mock_search_client.get_document.return_value = mock_document

        # テスト実行
        result = await search_service.get_document("test-doc-1")

        # 検証
        assert result["document"] == mock_document
        mock_search_client.get_document.assert_called_once_with(key="test-doc-1")

    @pytest.mark.asyncio
    async def test_get_document_not_found(self, search_service, mock_search_client):
        """ドキュメント未発見時のテスト"""
        from azure.core.exceptions import ResourceNotFoundError

        # ResourceNotFoundErrorを発生させる
        mock_search_client.get_document.side_effect = ResourceNotFoundError(
            "Document not found"
        )

        # テスト実行
        result = await search_service.get_document("nonexistent-doc")

        # 検証
        assert result["document"] is None
        assert result["error"] == "Document not found"

    @pytest.mark.asyncio
    async def test_upload_documents_success(self, search_service, mock_search_client):
        """ドキュメントアップロード成功のテスト"""
        from unittest.mock import MagicMock

        # モックアップロード結果を設定
        mock_result1 = MagicMock()
        mock_result1.succeeded = True
        mock_result1.key = "doc1"

        mock_result2 = MagicMock()
        mock_result2.succeeded = False
        mock_result2.key = "doc2"
        mock_result2.error_message = "Validation error"

        mock_search_client.upload_documents.return_value = [mock_result1, mock_result2]

        # テスト実行
        documents = [
            {"id": "doc1", "title": "Document 1", "content": "Content 1"},
            {"id": "doc2", "title": "Document 2", "content": "Content 2"},
        ]
        result = await search_service.upload_documents(documents)

        # 検証
        assert result["success_count"] == 1
        assert result["failed_count"] == 1
        assert result["total_count"] == 2
        assert len(result["errors"]) == 1
        assert result["errors"][0]["key"] == "doc2"
        assert result["errors"][0]["error"] == "Validation error"

    @pytest.mark.asyncio
    async def test_get_index_info_exists(self, search_service, mock_index_client):
        """インデックス情報取得（存在する場合）のテスト"""
        from unittest.mock import MagicMock

        # モックインデックスを設定
        mock_field1 = MagicMock()
        mock_field1.name = "id"
        mock_field1.type = "Edm.String"
        mock_field1.searchable = False
        mock_field1.filterable = True
        mock_field1.retrievable = True
        mock_field1.sortable = False
        mock_field1.facetable = False
        mock_field1.key = True

        mock_field2 = MagicMock()
        mock_field2.name = "content"
        mock_field2.type = "Edm.String"
        mock_field2.searchable = True
        mock_field2.filterable = False
        mock_field2.retrievable = True
        mock_field2.sortable = False
        mock_field2.facetable = False
        mock_field2.key = False

        mock_index = MagicMock()
        mock_index.name = "test-index"
        mock_index.fields = [mock_field1, mock_field2]

        mock_index_client.get_index.return_value = mock_index

        # テスト実行
        result = await search_service.get_index_info()

        # 検証
        assert result["exists"] is True
        assert result["name"] == "test-index"
        assert result["fields_count"] == 2
        assert len(result["fields"]) == 2

        # フィールド情報検証
        id_field = result["fields"][0]
        assert id_field["name"] == "id"
        assert id_field["type"] == "Edm.String"
        assert id_field["key"] is True
        assert id_field["searchable"] is False

    @pytest.mark.asyncio
    async def test_get_index_info_not_exists(self, search_service, mock_index_client):
        """インデックス情報取得（存在しない場合）のテスト"""
        from azure.core.exceptions import ResourceNotFoundError

        # ResourceNotFoundErrorを発生させる
        mock_index_client.get_index.side_effect = ResourceNotFoundError(
            "Index not found"
        )

        # テスト実行
        result = await search_service.get_index_info()

        # 検証
        assert result["exists"] is False
        assert result["name"] == "test-index"
        assert result["error"] == "Index not found"

    def test_get_service_info(self, search_service, mock_settings):
        """サービス情報取得のテスト"""
        # テスト実行
        result = search_service.get_service_info()

        # 検証
        assert result["endpoint"] == "https://test-search.search.windows.net"
        assert result["index_name"] == "test-index"
        assert result["clients_initialized"]["search_client"] is True
        assert result["clients_initialized"]["index_client"] is True
        assert result["configuration"]["endpoint_configured"] is True
        assert result["configuration"]["api_key_configured"] is True
        assert result["configuration"]["index_name_configured"] is True
