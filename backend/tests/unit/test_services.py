"""
サービス層ユニットテスト（モック使用）
"""

import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, Mock
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

    @pytest.mark.asyncio
    async def test_search_documents_success(self, rag_service):
        """ドキュメント検索の成功テスト"""
        query = "テスト検索クエリ"

        # SearchServiceのモック設定（SearchServiceのAPIレスポンス形式に合わせる）
        mock_search_response = {
            "documents": [
                {
                    "score": 0.85,
                    "document": {
                        "id": "doc1",
                        "title": "テストドキュメント1",
                        "content": "これはテスト用のドキュメント内容です。",
                        "file_name": "test1.pdf",
                        "source_url": "https://example.com/test1.pdf",
                        "file_type": "pdf",
                        "file_size": 1024,
                        "created_at": "2025-06-12T00:00:00Z",
                        "chunk_index": 0,
                        "chunk_count": 1,
                    },
                }
            ]
        }

        rag_service.search_service.search_documents = AsyncMock(
            return_value=mock_search_response
        )

        # テスト実行
        result = await rag_service.search_documents(query=query, top_k=5)

        # 検証
        assert len(result) == 1
        assert result[0]["id"] == "doc1"
        assert result[0]["title"] == "テストドキュメント1"
        assert result[0]["score"] == 0.85
        assert result[0]["metadata"]["file_type"] == "pdf"

        # SearchServiceが適切に呼ばれたか
        rag_service.search_service.search_documents.assert_called_once_with(
            query=query,
            top=5,  # SearchServiceのAPIに合わせてtopパラメータを使用
            select_fields=[
                "id",
                "title",
                "content",
                "file_name",
                "source_url",
                "file_type",
                "file_size",
                "created_at",
                "chunk_index",
                "chunk_count",
            ],
            filter_expression=None,
        )

    @pytest.mark.asyncio
    async def test_search_documents_with_filters(self, rag_service):
        """フィルタ付きドキュメント検索のテスト"""
        query = "テスト検索"
        filters = {"file_type": "pdf"}

        # SearchServiceのモック設定（空の結果）
        mock_empty_response = {"documents": []}
        rag_service.search_service.search_documents = AsyncMock(
            return_value=mock_empty_response
        )

        # テスト実行
        result = await rag_service.search_documents(query=query, filters=filters)

        # 検証
        assert isinstance(result, list)
        rag_service.search_service.search_documents.assert_called_once_with(
            query=query,
            top=10,  # デフォルト値、SearchServiceのAPIに合わせてtopパラメータを使用
            select_fields=[
                "id",
                "title",
                "content",
                "file_name",
                "source_url",
                "file_type",
                "file_size",
                "created_at",
                "chunk_index",
                "chunk_count",
            ],
            filter_expression="file_type eq 'pdf'",  # フィルタが文字列形式に変換される
        )

    @pytest.mark.asyncio
    async def test_search_documents_error_handling(self, rag_service):
        """ドキュメント検索のエラーハンドリングテスト"""
        query = "エラーテスト"

        # SearchServiceでエラーを発生させる
        rag_service.search_service.search_documents = AsyncMock(
            side_effect=Exception("Search error")
        )

        # テスト実行
        result = await rag_service.search_documents(query=query)

        # エラー時は空のリストが返されることを確認
        assert result == []

    @pytest.mark.asyncio
    async def test_ask_question_with_search_results(self, rag_service, mock_db):
        """検索結果がある場合の質問回答テスト"""
        question = "Azure AI Searchについて教えて"
        session_id = uuid.uuid4()

        # SearchServiceのモック設定（SearchServiceのAPIレスポンス形式に合わせる）
        mock_search_response = {
            "documents": [
                {
                    "score": 0.9,
                    "document": {
                        "id": "doc1",
                        "title": "Azure AI Search ガイド",
                        "content": "Azure AI Searchは強力な検索サービスです。",
                        "file_name": "azure_guide.pdf",
                        "source_url": "https://example.com/azure_guide.pdf",
                        "file_type": "pdf",
                        "file_size": 2048,
                        "created_at": "2025-06-12T00:00:00Z",
                        "chunk_index": 0,
                        "chunk_count": 1,
                    },
                }
            ]
        }

        rag_service.search_service.search_documents = AsyncMock(
            return_value=mock_search_response
        )

        # モック設定
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        # テスト実行
        result = await rag_service.ask_question(question, session_id)

        # 検証
        assert "answer" in result
        assert len(result["citations"]) == 1
        assert result["citations"][0]["title"] == "Azure AI Search ガイド"
        assert result["citations"][0]["score"] == 0.9
        assert result["metadata"]["search_results_count"] == 1
        assert result["metadata"]["has_context"] is True

    @pytest.mark.asyncio
    async def test_stream_answer_with_citations(self, rag_service, mock_db):
        """引用付きストリーミング回答のテスト"""
        question = "ストリーミングテスト"
        session_id = uuid.uuid4()

        # SearchServiceのモック設定（SearchServiceのAPIレスポンス形式に合わせる）
        mock_search_response = {
            "documents": [
                {
                    "score": 0.8,
                    "document": {
                        "id": "doc1",
                        "title": "ストリーミングガイド",
                        "content": "ストリーミングの詳細説明",
                        "file_name": "streaming.pdf",
                        "source_url": "",
                        "file_type": "pdf",
                        "file_size": 1024,
                        "created_at": "2025-06-12T00:00:00Z",
                        "chunk_index": 0,
                        "chunk_count": 1,
                    },
                }
            ]
        }

        rag_service.search_service.search_documents = AsyncMock(
            return_value=mock_search_response
        )

        # モック設定
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        chunks = []
        async for chunk in rag_service.stream_answer(question, session_id):
            chunks.append(chunk)

        # 検証
        assert len(chunks) > 0

        # 最後のchunkに引用情報が含まれているか
        last_chunk = chunks[-1]
        assert last_chunk.get("is_complete") is True
        assert "citations" in last_chunk
        assert len(last_chunk["citations"]) == 1
        assert last_chunk["citations"][0]["title"] == "ストリーミングガイド"


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


class TestBlobStorageService:
    """BlobStorageServiceのテストクラス"""

    @pytest.fixture
    def mock_blob_service_client(self):
        """BlobServiceClientのモック"""
        from unittest.mock import AsyncMock, MagicMock

        mock_client = AsyncMock()
        mock_client.get_account_information = AsyncMock()
        mock_client.get_container_client = MagicMock()
        mock_client.get_blob_client = MagicMock()
        mock_client.close = AsyncMock()
        return mock_client

    @pytest.fixture
    def mock_settings(self):
        """設定のモック"""
        from unittest.mock import MagicMock

        mock_settings = MagicMock()
        mock_settings.azure_storage_account_name = "teststorage"
        mock_settings.azure_storage_account_key = "test-key"  # pragma: allowlist secret
        mock_settings.azure_storage_container_name = "test-container"
        return mock_settings

    @pytest.fixture
    def blob_storage_service(
        self, monkeypatch, mock_settings, mock_blob_service_client
    ):
        """BlobStorageServiceのテスト用インスタンス"""
        from services.blob_storage_service import BlobStorageService

        # 設定をモック
        monkeypatch.setattr(
            "services.blob_storage_service.get_settings", lambda: mock_settings
        )

        # BlobServiceClientをモック
        monkeypatch.setattr(
            "services.blob_storage_service.BlobServiceClient",
            lambda account_url, credential: mock_blob_service_client,
        )

        service = BlobStorageService()
        service._client = mock_blob_service_client
        return service

    @pytest.mark.asyncio
    async def test_health_check_healthy(
        self, blob_storage_service, mock_blob_service_client
    ):
        """ヘルスチェック成功のテスト"""
        # モックコンテナクライアントを設定
        mock_container_client = AsyncMock()
        mock_container_client.get_container_properties = AsyncMock()
        mock_blob_service_client.get_container_client.return_value = (
            mock_container_client
        )

        # テスト実行
        result = await blob_storage_service.health_check()

        # 検証
        assert result is True
        mock_blob_service_client.get_container_client.assert_called_once_with(
            "test-container"
        )
        mock_container_client.get_container_properties.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_unhealthy_no_client(self):
        """クライアント未初期化時のヘルスチェックテスト"""
        from services.blob_storage_service import BlobStorageService

        # クライアント未初期化のBlobStorageService
        service = BlobStorageService.__new__(BlobStorageService)
        service._client = None

        # テスト実行
        result = await service.health_check()

        # 検証
        assert result is False

    @pytest.mark.asyncio
    async def test_upload_document_success(
        self, blob_storage_service, mock_blob_service_client
    ):
        """ドキュメントアップロード成功のテスト"""
        from azure.core.exceptions import ResourceExistsError

        # モックコンテナクライアントとBlobクライアントを設定
        mock_container_client = AsyncMock()
        mock_container_client.create_container = AsyncMock(
            side_effect=ResourceExistsError("Container exists")
        )
        mock_blob_service_client.get_container_client.return_value = (
            mock_container_client
        )

        mock_blob_client = AsyncMock()
        mock_blob_client.upload_blob = AsyncMock()
        mock_blob_client.url = (
            "https://teststorage.blob.core.windows.net/test-container/test.txt"
        )
        mock_blob_service_client.get_blob_client.return_value = mock_blob_client

        # テスト実行
        test_content = b"Test document content"
        result = await blob_storage_service.upload_document(
            file_name="test.txt",
            file_content=test_content,
            content_type="text/plain",
            metadata={"test": "true"},
        )

        # 検証
        assert (
            result
            == "https://teststorage.blob.core.windows.net/test-container/test.txt"
        )
        mock_blob_client.upload_blob.assert_called_once()

        # upload_blobの引数を検証
        call_args = mock_blob_client.upload_blob.call_args
        assert call_args[1]["data"] == test_content
        assert call_args[1]["content_type"] == "text/plain"
        assert call_args[1]["overwrite"] is True
        assert "uploaded_at" in call_args[1]["metadata"]

    @pytest.mark.asyncio
    async def test_download_document_success(
        self, blob_storage_service, mock_blob_service_client
    ):
        """ドキュメントダウンロード成功のテスト"""
        # モックBlobクライアントを設定
        mock_blob_client = AsyncMock()
        mock_download_stream = AsyncMock()
        mock_download_stream.readall = AsyncMock(return_value=b"Test document content")
        mock_blob_client.download_blob = AsyncMock(return_value=mock_download_stream)
        mock_blob_service_client.get_blob_client.return_value = mock_blob_client

        # テスト実行
        result = await blob_storage_service.download_document("test.txt")

        # 検証
        assert result == b"Test document content"
        mock_blob_client.download_blob.assert_called_once()
        mock_download_stream.readall.assert_called_once()

    @pytest.mark.asyncio
    async def test_download_document_not_found(
        self, blob_storage_service, mock_blob_service_client
    ):
        """ドキュメント未発見時のテスト"""
        from azure.core.exceptions import ResourceNotFoundError
        from services.blob_storage_service import BlobStorageError

        # ResourceNotFoundErrorを発生させる
        mock_blob_client = AsyncMock()
        mock_blob_client.download_blob = AsyncMock(
            side_effect=ResourceNotFoundError("Blob not found")
        )
        mock_blob_service_client.get_blob_client.return_value = mock_blob_client

        # テスト実行とエラー検証
        with pytest.raises(BlobStorageError, match="Document not found"):
            await blob_storage_service.download_document("nonexistent.txt")

    @pytest.mark.asyncio
    async def test_get_service_info_healthy(
        self, blob_storage_service, mock_blob_service_client
    ):
        """サービス情報取得（正常時）のテスト"""
        from unittest.mock import MagicMock
        from datetime import datetime

        # モックアカウント情報を設定
        mock_account_info = {"account_kind": "StorageV2", "sku_name": "Standard_LRS"}
        mock_blob_service_client.get_account_information = AsyncMock(
            return_value=mock_account_info
        )

        # モックコンテナプロパティを設定
        mock_container_client = AsyncMock()
        mock_container_props = MagicMock()
        mock_container_props.last_modified = datetime(2024, 1, 1, 12, 0, 0)
        mock_container_client.get_container_properties = AsyncMock(
            return_value=mock_container_props
        )
        mock_blob_service_client.get_container_client.return_value = (
            mock_container_client
        )

        # テスト実行
        result = await blob_storage_service.get_service_info()

        # 検証
        assert result["status"] == "healthy"
        assert result["account_name"] == "teststorage"
        assert result["container_name"] == "test-container"
        assert result["account_kind"] == "StorageV2"
        assert result["sku_name"] == "Standard_LRS"
        assert result["container_last_modified"] == "2024-01-01T12:00:00"

    @pytest.mark.asyncio
    async def test_get_service_info_not_configured(self):
        """サービス情報取得（未設定時）のテスト"""
        from services.blob_storage_service import BlobStorageService

        # クライアント未初期化のBlobStorageService
        service = BlobStorageService.__new__(BlobStorageService)
        service._client = None

        # テスト実行
        result = await service.get_service_info()

        # 検証
        assert result["status"] == "not_configured"
        assert result["account_name"] is None
        assert result["container_name"] is None


class TestDocumentParser:
    """ドキュメントパーサーのユニットテスト"""

    @pytest.fixture
    def document_parser(self):
        """DocumentParserインスタンス"""
        from services.document_parser import DocumentParser

        return DocumentParser(chunk_size=500, chunk_overlap=50)

    @pytest.fixture
    def sample_text_content(self):
        """テスト用テキストコンテンツ"""
        return b"This is a test document.\n\nIt has multiple paragraphs.\n\nEach paragraph should be processed correctly."

    @pytest.fixture
    def sample_pdf_content(self):
        """テスト用PDFコンテンツ（バイナリ）"""
        # 実際のPDFバイナリの代わりにダミーデータ
        return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"

    @pytest.mark.asyncio
    async def test_parse_text_file(self, document_parser, sample_text_content):
        """テキストファイル解析のテスト"""
        result = await document_parser.parse(
            file_content=sample_text_content,
            content_type="text/plain",
            filename="test.txt",
        )

        from services.document_parser import ParsedDocument

        assert isinstance(result, ParsedDocument)
        assert result.file_type == "txt"
        assert "This is a test document" in result.text
        assert len(result.chunks) > 0
        assert result.metadata["filename"] == "test.txt"
        assert result.metadata["content_type"] == "text/plain"
        assert result.processing_time > 0

    @pytest.mark.asyncio
    async def test_parse_markdown_file(self, document_parser):
        """Markdownファイル解析のテスト"""
        markdown_content = b"# Test Document\n\nThis is a **markdown** document.\n\n## Section 2\n\nWith multiple sections."

        result = await document_parser.parse(
            file_content=markdown_content,
            content_type="text/markdown",
            filename="test.md",
        )

        assert result.file_type == "txt"
        assert "# Test Document" in result.text
        assert "markdown" in result.text
        assert len(result.chunks) > 0

    @pytest.mark.asyncio
    async def test_detect_file_type_by_extension(self, document_parser):
        """ファイル拡張子による形式判定のテスト"""
        # PDF拡張子
        file_type = document_parser._detect_file_type(
            "application/octet-stream", "document.pdf"
        )
        assert file_type == "pdf"

        # DOCX拡張子
        file_type = document_parser._detect_file_type(
            "application/octet-stream", "document.docx"
        )
        assert file_type == "docx"

        # TXT拡張子
        file_type = document_parser._detect_file_type(
            "application/octet-stream", "document.txt"
        )
        assert file_type == "txt"

    @pytest.mark.asyncio
    async def test_detect_file_type_by_content_type(self, document_parser):
        """Content-Typeによる形式判定のテスト"""
        # PDF Content-Type
        file_type = document_parser._detect_file_type("application/pdf", "")
        assert file_type == "pdf"

        # DOCX Content-Type
        file_type = document_parser._detect_file_type(
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "",
        )
        assert file_type == "docx"

        # Text Content-Type
        file_type = document_parser._detect_file_type("text/plain", "")
        assert file_type == "txt"

    @pytest.mark.asyncio
    async def test_chunk_splitting(self, document_parser):
        """チャンク分割のテスト"""
        # 長いテキストを作成
        long_text = "This is a paragraph. " * 50  # 約1000文字
        long_content = long_text.encode("utf-8")

        result = await document_parser.parse(
            file_content=long_content,
            content_type="text/plain",
            filename="long_text.txt",
        )

        # チャンクが複数作成されることを確認
        assert len(result.chunks) > 1

        # 各チャンクのサイズが適切であることを確認
        for chunk in result.chunks:
            assert len(chunk.content) <= document_parser.chunk_size + 100  # 多少の余裕
            assert chunk.chunk_index >= 0
            assert chunk.start_char >= 0
            assert chunk.end_char > chunk.start_char

    @pytest.mark.asyncio
    async def test_unsupported_file_type_error(self, document_parser):
        """サポートされていないファイル形式のエラーテスト"""
        from services.document_parser import DocumentParserError

        with pytest.raises(DocumentParserError, match="Unsupported file type"):
            await document_parser.parse(
                file_content=b"binary data",
                content_type="application/unknown",
                filename="test.unknown",
            )

    @pytest.mark.asyncio
    async def test_empty_content_handling(self, document_parser):
        """空コンテンツの処理テスト"""
        result = await document_parser.parse(
            file_content=b"", content_type="text/plain", filename="empty.txt"
        )

        assert result.text == ""
        assert len(result.chunks) == 0
        assert result.metadata["text_length"] == 0

    @pytest.mark.asyncio
    async def test_encoding_detection(self, document_parser):
        """文字エンコーディング検出のテスト"""
        # UTF-8テキスト
        utf8_content = "日本語のテキストです。".encode("utf-8")
        result = await document_parser.parse(
            file_content=utf8_content,
            content_type="text/plain",
            filename="japanese.txt",
        )
        assert "日本語" in result.text

        # Shift_JISテキスト（フォールバック）
        try:
            sjis_content = "日本語のテキストです。".encode("shift_jis")
            result = await document_parser.parse(
                file_content=sjis_content,
                content_type="text/plain",
                filename="japanese_sjis.txt",
            )
            assert "日本語" in result.text
        except UnicodeEncodeError:
            # Shift_JISでエンコードできない文字がある場合はスキップ
            pass

    def test_get_supported_types(self):
        """サポートされるファイル形式取得のテスト"""
        from services.document_parser import DocumentParser

        supported_types = DocumentParser.get_supported_types()

        assert "application/pdf" in supported_types
        assert "text/plain" in supported_types
        assert (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            in supported_types
        )
        assert supported_types["application/pdf"] == "pdf"
        assert supported_types["text/plain"] == "txt"

    def test_is_supported_type(self):
        """ファイル形式サポート判定のテスト"""
        from services.document_parser import DocumentParser

        assert DocumentParser.is_supported_type("application/pdf") is True
        assert DocumentParser.is_supported_type("text/plain") is True
        assert DocumentParser.is_supported_type("application/unknown") is False

    @pytest.mark.asyncio
    async def test_metadata_extraction(self, document_parser, sample_text_content):
        """メタデータ抽出のテスト"""
        custom_metadata = {"source": "test", "category": "sample"}

        result = await document_parser.parse(
            file_content=sample_text_content,
            content_type="text/plain",
            filename="test.txt",
            metadata=custom_metadata,
        )

        # 基本メタデータの確認
        assert result.metadata["filename"] == "test.txt"
        assert result.metadata["content_type"] == "text/plain"
        assert result.metadata["file_type"] == "txt"
        assert "parsed_at" in result.metadata
        assert "text_length" in result.metadata

        # カスタムメタデータの確認
        assert result.metadata["source"] == "test"
        assert result.metadata["category"] == "sample"

        # テキスト固有メタデータの確認
        assert "lines" in result.metadata
        assert "encoding" in result.metadata


class TestDocumentPipeline:
    """ドキュメント処理パイプラインのユニットテスト"""

    @pytest.fixture
    def mock_blob_storage(self):
        """モックBlobStorageService"""
        mock_service = AsyncMock()
        mock_service.upload_document = AsyncMock(
            return_value="https://test.blob.core.windows.net/test.txt"
        )
        mock_service.health_check = AsyncMock(return_value=True)
        return mock_service

    @pytest.fixture
    def mock_document_parser(self):
        """モックDocumentParser"""
        from services.document_parser import ParsedDocument, TextChunk

        mock_parser = AsyncMock()

        # parse メソッドを動的に設定
        async def mock_parse(file_content, content_type, filename, metadata=None):
            # テスト用のチャンクを作成
            test_chunk = TextChunk(
                content="Test content chunk",
                chunk_index=0,
                chunk_overlap=0,
                start_char=0,
                end_char=18,
                metadata={"chunk_type": "test"},
            )

            # メタデータを統合
            combined_metadata = {
                "filename": filename,
                "content_type": content_type,
                "file_type": "txt",
                "text_length": 18,
                **(metadata or {}),  # カスタムメタデータを含める
            }

            # テスト用の解析結果を作成
            return ParsedDocument(
                text="Test content chunk",
                chunks=[test_chunk],
                metadata=combined_metadata,
                file_type="txt",
                processing_time=0.1,
            )

        mock_parser.parse = AsyncMock(side_effect=mock_parse)
        mock_parser.get_supported_types = Mock(return_value={"text/plain": "txt"})
        mock_parser.is_supported_type = Mock(return_value=True)

        return mock_parser

    @pytest.fixture
    def mock_search_service(self):
        """モックSearchService"""
        mock_service = AsyncMock()
        mock_service.upload_documents = AsyncMock()
        mock_service.health_check = AsyncMock(return_value=True)
        return mock_service

    @pytest.fixture
    def document_pipeline(
        self, mock_blob_storage, mock_document_parser, mock_search_service
    ):
        """DocumentPipelineインスタンス"""
        from services.document_pipeline import DocumentPipeline

        return DocumentPipeline(
            blob_storage=mock_blob_storage,
            document_parser=mock_document_parser,
            search_service=mock_search_service,
        )

    @pytest.mark.asyncio
    async def test_process_document_success(
        self,
        document_pipeline,
        mock_blob_storage,
        mock_document_parser,
        mock_search_service,
    ):
        """ドキュメント処理成功のテスト"""
        test_content = b"Test document content"
        filename = "test.txt"
        content_type = "text/plain"

        result = await document_pipeline.process_document(
            file_content=test_content, filename=filename, content_type=content_type
        )

        # 結果の検証
        from services.document_pipeline import ProcessingResult

        assert isinstance(result, ProcessingResult)
        assert result.blob_url == "https://test.blob.core.windows.net/test.txt"
        assert result.chunks_count == 1
        assert result.indexed_chunks == 1
        assert result.processing_time > 0
        assert len(result.errors) == 0

        # 各サービスが適切に呼ばれたか検証
        mock_document_parser.parse.assert_called_once()
        mock_blob_storage.upload_document.assert_called_once()
        mock_search_service.upload_documents.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_document_with_custom_metadata(self, document_pipeline):
        """カスタムメタデータ付きドキュメント処理のテスト"""
        test_content = b"Test document content"
        filename = "test.txt"
        content_type = "text/plain"
        custom_metadata = {"source": "test", "category": "sample"}

        result = await document_pipeline.process_document(
            file_content=test_content,
            filename=filename,
            content_type=content_type,
            metadata=custom_metadata,
        )

        # カスタムメタデータが含まれていることを確認
        assert "source" in result.metadata
        assert result.metadata["source"] == "test"

    @pytest.mark.asyncio
    async def test_process_document_parsing_error(
        self, document_pipeline, mock_document_parser
    ):
        """ドキュメント解析エラーのテスト"""
        from services.document_parser import DocumentParserError
        from services.document_pipeline import DocumentPipelineError

        # パーサーでエラーを発生させる
        mock_document_parser.parse.side_effect = DocumentParserError("Parsing failed")

        with pytest.raises(DocumentPipelineError, match="Document parsing failed"):
            await document_pipeline.process_document(
                file_content=b"test", filename="test.txt", content_type="text/plain"
            )

    @pytest.mark.asyncio
    async def test_process_document_blob_storage_error(
        self, document_pipeline, mock_blob_storage
    ):
        """Blob Storageエラーのテスト"""
        from services.blob_storage_service import BlobStorageError
        from services.document_pipeline import DocumentPipelineError

        # Blob Storageでエラーを発生させる
        mock_blob_storage.upload_document.side_effect = BlobStorageError(
            "Upload failed"
        )

        with pytest.raises(DocumentPipelineError, match="Blob storage upload failed"):
            await document_pipeline.process_document(
                file_content=b"test", filename="test.txt", content_type="text/plain"
            )

    @pytest.mark.asyncio
    async def test_process_document_indexing_error(
        self, document_pipeline, mock_search_service
    ):
        """インデックス登録エラーのテスト"""
        from services.document_pipeline import DocumentPipelineError

        # Search Serviceでエラーを発生させる
        mock_search_service.upload_documents.side_effect = Exception("Indexing failed")

        with pytest.raises(DocumentPipelineError, match="Document indexing failed"):
            await document_pipeline.process_document(
                file_content=b"test", filename="test.txt", content_type="text/plain"
            )

    @pytest.mark.asyncio
    async def test_get_processing_status(self, document_pipeline):
        """処理状況取得のテスト"""
        test_content = b"Test document content"
        document_id = "test-doc-123"

        # ドキュメント処理を開始
        result = await document_pipeline.process_document(
            file_content=test_content,
            filename="test.txt",
            content_type="text/plain",
            document_id=document_id,
        )

        # 処理状況を取得
        status = await document_pipeline.get_processing_status(document_id)

        assert status is not None
        assert status.document_id == document_id
        assert status.status == "completed"
        assert status.progress == 1.0
        assert status.result == result

    @pytest.mark.asyncio
    async def test_health_check_all_healthy(self, document_pipeline):
        """全コンポーネント正常時のヘルスチェック"""
        health = await document_pipeline.health_check()

        assert health["status"] == "healthy"
        assert "blob_storage" in health["components"]
        assert "search_service" in health["components"]
        assert "document_parser" in health["components"]
        assert all(
            comp["status"] == "healthy" for comp in health["components"].values()
        )

    @pytest.mark.asyncio
    async def test_health_check_degraded(self, document_pipeline, mock_blob_storage):
        """一部コンポーネント異常時のヘルスチェック"""
        # Blob Storageを異常状態にする
        mock_blob_storage.health_check.return_value = False

        health = await document_pipeline.health_check()

        assert health["status"] == "degraded"
        assert health["components"]["blob_storage"]["status"] == "unhealthy"

    def test_get_supported_file_types(self, document_pipeline, mock_document_parser):
        """サポートファイル形式取得のテスト"""
        supported_types = document_pipeline.get_supported_file_types()

        mock_document_parser.get_supported_types.assert_called_once()
        assert supported_types == {"text/plain": "txt"}

    def test_is_supported_file_type(self, document_pipeline, mock_document_parser):
        """ファイル形式サポート判定のテスト"""
        result = document_pipeline.is_supported_file_type("text/plain")

        mock_document_parser.is_supported_type.assert_called_once_with("text/plain")
        assert result is True
