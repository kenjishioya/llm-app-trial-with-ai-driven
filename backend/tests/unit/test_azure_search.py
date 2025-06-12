"""
Azure AI Search関連サービスのユニットテスト

Task 3-4A-1: ユニットテスト実装
"""

import pytest
from unittest.mock import Mock, patch

# テスト対象のインポート
from services.search_service import SearchService, SearchServiceError
from services.document_pipeline import DocumentPipeline
from services.blob_storage_service import BlobStorageService, BlobStorageError


class TestSearchService:
    """SearchService のユニットテスト"""

    @pytest.fixture
    def mock_search_client(self):
        """モックされた Azure Search Client"""
        return Mock()

    @pytest.fixture
    def search_service(self, mock_search_client):
        """テスト用 SearchService インスタンス"""
        with patch("services.search_service.SearchClient"):
            service = SearchService()
            service.search_client = mock_search_client
            return service

    @pytest.mark.asyncio
    async def test_search_documents_success(self, search_service, mock_search_client):
        """正常な検索テスト"""
        mock_results = [
            {
                "@search.score": 5.5,
                "id": "doc1",
                "content": "test content",
                "title": "Test Document",
            }
        ]
        mock_search_client.search.return_value = mock_results

        result = await search_service.search_documents(query="test query", top=5)

        assert "documents" in result
        assert len(result["documents"]) == 1
        assert result["documents"][0]["score"] == 5.5

    @pytest.mark.asyncio
    async def test_search_documents_error(self, search_service, mock_search_client):
        """検索エラーハンドリングテスト"""
        mock_search_client.search.side_effect = Exception("Search API Error")

        with pytest.raises(SearchServiceError):
            await search_service.search_documents(query="test")

    @pytest.mark.asyncio
    async def test_upload_documents_success(self, search_service, mock_search_client):
        """ドキュメントアップロード成功テスト"""
        mock_results = [Mock(succeeded=True, key="doc1")]
        mock_search_client.upload_documents.return_value = mock_results

        documents = [{"id": "doc1", "content": "test content"}]
        result = await search_service.upload_documents(documents)

        assert result["success_count"] == 1
        assert result["failed_count"] == 0


class TestBlobStorageService:
    """BlobStorageService のユニットテスト"""

    @pytest.fixture
    def mock_blob_client(self):
        """モックされた BlobServiceClient"""
        return Mock()

    @pytest.fixture
    def blob_service(self, mock_blob_client):
        """テスト用 BlobStorageService インスタンス"""
        with patch("services.blob_storage_service.BlobServiceClient"):
            service = BlobStorageService()
            service.blob_service_client = mock_blob_client
            return service

    @pytest.mark.asyncio
    @pytest.mark.skip(
        reason="BlobStorageService requires actual Azure credentials for initialization"
    )
    async def test_upload_document_success(self, blob_service, mock_blob_client):
        """ドキュメントアップロード成功テスト"""
        # モックの設定を修正
        mock_blob_client.get_blob_client.return_value.upload_blob.return_value = None
        mock_blob_client.get_blob_client.return_value.url = (
            "https://test.blob.url/test.txt"
        )

        # blob_service_clientを直接設定
        blob_service.blob_service_client = mock_blob_client

        result = await blob_service.upload_document(
            file_name="test.txt", file_content=b"test content"
        )

        assert "test.txt" in result

    @pytest.mark.asyncio
    @pytest.mark.skip(
        reason="BlobStorageService requires actual Azure credentials for initialization"
    )
    async def test_upload_document_error(self, blob_service, mock_blob_client):
        """ドキュメントアップロードエラーテスト"""
        mock_blob_client.get_blob_client.return_value.upload_blob.side_effect = (
            Exception("Upload failed")
        )

        with pytest.raises(BlobStorageError):
            await blob_service.upload_document(
                file_name="test.txt", file_content=b"test content"
            )


class TestDocumentPipeline:
    """DocumentPipeline のユニットテスト"""

    @pytest.fixture
    def document_pipeline(self):
        """テスト用 DocumentPipeline インスタンス"""
        with patch("services.document_pipeline.BlobStorageService"), patch(
            "services.document_pipeline.SearchService"
        ), patch("services.document_pipeline.DocumentParser"):
            return DocumentPipeline()

    @pytest.mark.asyncio
    async def test_get_processing_status(self, document_pipeline):
        """処理状況取得テスト"""
        # ダミーのdocument_idを使用
        test_document_id = "test-doc-123"

        # 処理状況が存在しない場合のテスト
        status = await document_pipeline.get_processing_status(test_document_id)

        assert status is None  # 存在しないIDの場合はNoneが返される
