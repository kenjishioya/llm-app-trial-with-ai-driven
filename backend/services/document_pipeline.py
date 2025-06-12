"""
ドキュメント処理パイプラインサービス
アップロード → 解析 → チャンク分割 → Blob Storage → AI Search 登録の統合処理
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from services.blob_storage_service import BlobStorageService, BlobStorageError
from services.document_parser import DocumentParser, DocumentParserError, ParsedDocument
from services.search_service import SearchService

logger = logging.getLogger(__name__)


class DocumentPipelineError(Exception):
    """ドキュメント処理パイプラインエラー"""

    pass


@dataclass
class ProcessingResult:
    """処理結果"""

    document_id: str
    blob_url: str
    chunks_count: int
    indexed_chunks: int
    processing_time: float
    metadata: Dict[str, Any]
    errors: List[str]


@dataclass
class ProcessingStatus:
    """処理ステータス"""

    document_id: str
    status: str  # "processing", "completed", "failed"
    progress: float  # 0.0 - 1.0
    current_step: str
    message: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[ProcessingResult] = None


class DocumentPipeline:
    """ドキュメント処理パイプライン"""

    def __init__(
        self,
        blob_storage: Optional[BlobStorageService] = None,
        document_parser: Optional[DocumentParser] = None,
        search_service: Optional[SearchService] = None,
    ):
        """初期化"""
        self.blob_storage = blob_storage or BlobStorageService()
        self.document_parser = document_parser or DocumentParser()
        self.search_service = search_service or SearchService()

        # 処理状況の追跡
        self._processing_status: Dict[str, ProcessingStatus] = {}

    async def process_document(
        self,
        file_content: bytes,
        filename: str,
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        document_id: Optional[str] = None,
    ) -> ProcessingResult:
        """ドキュメントの完全処理"""
        if document_id is None:
            document_id = str(uuid.uuid4())

        start_time = datetime.now()
        errors: List[str] = []

        # 処理状況の初期化
        status = ProcessingStatus(
            document_id=document_id,
            status="processing",
            progress=0.0,
            current_step="initializing",
            message="Processing started",
            started_at=start_time,
        )
        self._processing_status[document_id] = status

        try:
            # Step 1: ドキュメント解析
            status.current_step = "parsing"
            status.progress = 0.2
            status.message = "Parsing document content"
            logger.info(f"Starting document parsing for {filename}")

            parsed_doc = await self._parse_document(
                file_content, content_type, filename, metadata
            )

            # Step 2: Blob Storage アップロード
            status.current_step = "uploading"
            status.progress = 0.4
            status.message = "Uploading to blob storage"
            logger.info(f"Uploading document {filename} to blob storage")

            blob_url = await self._upload_to_blob_storage(
                file_content, filename, content_type, parsed_doc.metadata
            )

            # Step 3: チャンクのインデックス登録
            status.current_step = "indexing"
            status.progress = 0.6
            status.message = "Indexing document chunks"
            logger.info(f"Indexing {len(parsed_doc.chunks)} chunks for {filename}")

            indexed_chunks = await self._index_chunks(parsed_doc, document_id, blob_url)

            # Step 4: 完了処理
            status.current_step = "completed"
            status.progress = 1.0
            status.message = "Processing completed successfully"
            status.status = "completed"
            status.completed_at = datetime.now()

            processing_time = (datetime.now() - start_time).total_seconds()

            result = ProcessingResult(
                document_id=document_id,
                blob_url=blob_url,
                chunks_count=len(parsed_doc.chunks),
                indexed_chunks=indexed_chunks,
                processing_time=processing_time,
                metadata={
                    **parsed_doc.metadata,
                    "processed_at": datetime.utcnow().isoformat(),
                    "pipeline_version": "1.0",
                },
                errors=errors,
            )

            status.result = result
            logger.info(
                f"Document processing completed for {filename}: {indexed_chunks} chunks indexed"
            )

            return result

        except Exception as e:
            # エラー処理
            status.status = "failed"
            status.current_step = "error"
            status.message = f"Processing failed: {str(e)}"
            status.completed_at = datetime.now()

            error_msg = f"Document processing failed for {filename}: {e}"
            logger.error(error_msg)
            errors.append(error_msg)

            # 部分的な結果でも返す
            processing_time = (datetime.now() - start_time).total_seconds()
            result = ProcessingResult(
                document_id=document_id,
                blob_url="",
                chunks_count=0,
                indexed_chunks=0,
                processing_time=processing_time,
                metadata=metadata or {},
                errors=errors,
            )

            status.result = result
            raise DocumentPipelineError(error_msg) from e

    async def _parse_document(
        self,
        file_content: bytes,
        content_type: str,
        filename: str,
        metadata: Optional[Dict[str, Any]],
    ) -> ParsedDocument:
        """ドキュメント解析"""
        try:
            return await self.document_parser.parse(
                file_content=file_content,
                content_type=content_type,
                filename=filename,
                metadata=metadata,
            )
        except DocumentParserError as e:
            raise DocumentPipelineError(f"Document parsing failed: {e}") from e

    async def _upload_to_blob_storage(
        self,
        file_content: bytes,
        filename: str,
        content_type: str,
        metadata: Dict[str, Any],
    ) -> str:
        """Blob Storageへのアップロード"""
        try:
            return await self.blob_storage.upload_document(
                file_name=filename,
                file_content=file_content,
                content_type=content_type,
                metadata=metadata,
            )
        except BlobStorageError as e:
            raise DocumentPipelineError(f"Blob storage upload failed: {e}") from e

    async def _index_chunks(
        self, parsed_doc: ParsedDocument, document_id: str, blob_url: str
    ) -> int:
        """チャンクのインデックス登録"""
        try:
            # チャンクをAI Search用のドキュメント形式に変換
            search_documents = []

            for chunk in parsed_doc.chunks:
                search_doc = {
                    "id": f"{document_id}_chunk_{chunk.chunk_index}",
                    "document_id": document_id,
                    "chunk_id": f"chunk_{chunk.chunk_index}",
                    "title": parsed_doc.metadata.get(
                        "title", parsed_doc.metadata.get("filename", "")
                    ),
                    "content": chunk.content,
                    "summary": (
                        chunk.content[:200] + "..."
                        if len(chunk.content) > 200
                        else chunk.content
                    ),
                    "file_name": parsed_doc.metadata.get("filename", ""),
                    "file_type": parsed_doc.file_type,
                    "file_size": parsed_doc.metadata.get("file_size", 0),
                    "created_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "updated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "chunk_index": chunk.chunk_index,
                    "chunk_count": len(parsed_doc.chunks),
                    "chunk_overlap": chunk.chunk_overlap,
                    "source_url": blob_url,
                    "page_number": chunk.metadata.get("page_number", 0),
                    "category": parsed_doc.metadata.get("category", ""),
                    "tags": parsed_doc.metadata.get("tags", []),
                }
                search_documents.append(search_doc)

            # AI Searchにアップロード
            await self.search_service.upload_documents(search_documents)

            return len(search_documents)

        except Exception as e:
            raise DocumentPipelineError(f"Document indexing failed: {e}") from e

    async def get_processing_status(
        self, document_id: str
    ) -> Optional[ProcessingStatus]:
        """処理状況の取得"""
        return self._processing_status.get(document_id)

    async def list_processing_status(self) -> List[ProcessingStatus]:
        """全処理状況の取得"""
        return list(self._processing_status.values())

    async def health_check(self) -> Dict[str, Any]:
        """ヘルスチェック"""
        health_status: Dict[str, Any] = {
            "status": "healthy",
            "components": {},
            "timestamp": datetime.utcnow().isoformat(),
        }

        try:
            # Blob Storage ヘルスチェック
            blob_healthy = await self.blob_storage.health_check()
            health_status["components"]["blob_storage"] = {
                "status": "healthy" if blob_healthy else "unhealthy"
            }

            # Search Service ヘルスチェック
            search_health = await self.search_service.health_check()
            search_healthy = search_health.get("status") == "healthy"
            health_status["components"]["search_service"] = {
                "status": "healthy" if search_healthy else "unhealthy"
            }

            # Document Parser ヘルスチェック（依存関係確認）
            parser_healthy = True
            try:
                # 簡単なテスト解析
                test_content = b"test"
                await self.document_parser.parse(test_content, "text/plain", "test.txt")
            except Exception as e:
                parser_healthy = False
                logger.warning(f"Document parser health check failed: {e}")

            health_status["components"]["document_parser"] = {
                "status": "healthy" if parser_healthy else "unhealthy"
            }

            # 全体ステータスの判定
            all_healthy = all(
                comp["status"] == "healthy"
                for comp in health_status["components"].values()
            )

            if not all_healthy:
                health_status["status"] = "degraded"

        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
            logger.error(f"Pipeline health check failed: {e}")

        return health_status

    async def cleanup_old_status(self, max_age_hours: int = 24) -> int:
        """古い処理状況の削除"""
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        removed_count = 0

        to_remove = []
        for doc_id, status in self._processing_status.items():
            if status.started_at.timestamp() < cutoff_time:
                to_remove.append(doc_id)

        for doc_id in to_remove:
            del self._processing_status[doc_id]
            removed_count += 1

        logger.info(f"Cleaned up {removed_count} old processing status records")
        return removed_count

    def get_supported_file_types(self) -> Dict[str, str]:
        """サポートされるファイル形式の取得"""
        return self.document_parser.get_supported_types()

    def is_supported_file_type(self, content_type: str) -> bool:
        """ファイル形式サポート判定"""
        return self.document_parser.is_supported_type(content_type)
