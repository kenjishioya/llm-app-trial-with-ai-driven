"""
Azure Blob Storage サービス
ドキュメントの保存・取得・メタデータ管理を担当
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from azure.storage.blob.aio import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError

from config import get_settings

logger = logging.getLogger(__name__)


class BlobStorageError(Exception):
    """Blob Storage操作エラー"""

    pass


class BlobStorageService:
    """Azure Blob Storage サービス"""

    def __init__(self) -> None:
        """初期化"""
        self.settings = get_settings()
        self.account_name = self.settings.azure_storage_account_name
        self.account_key = self.settings.azure_storage_account_key
        self.container_name = self.settings.azure_storage_container_name

        self._client: Optional[BlobServiceClient] = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Blob Service Clientの初期化"""
        if not self.account_name or not self.account_key:
            logger.warning("Azure Storage credentials not configured")
            return

        try:
            account_url = f"https://{self.account_name}.blob.core.windows.net"
            self._client = BlobServiceClient(
                account_url=account_url, credential=self.account_key
            )
            logger.info(f"Blob Storage client initialized: {account_url}")
        except Exception as e:
            logger.error(f"Failed to initialize Blob Storage client: {e}")
            raise BlobStorageError(f"Client initialization failed: {e}")

    async def health_check(self) -> bool:
        """ヘルスチェック"""
        if not self._client:
            return False

        try:
            # コンテナの存在確認
            container_client = self._client.get_container_client(self.container_name)
            await container_client.get_container_properties()
            return True
        except ResourceNotFoundError:
            logger.warning(f"Container '{self.container_name}' not found")
            return False
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    async def ensure_container_exists(self) -> bool:
        """コンテナの存在確認・作成"""
        if not self._client:
            raise BlobStorageError("Blob Storage client not initialized")

        try:
            container_client = self._client.get_container_client(self.container_name)
            await container_client.create_container()
            logger.info(f"Container '{self.container_name}' created")
            return True
        except ResourceExistsError:
            logger.debug(f"Container '{self.container_name}' already exists")
            return True
        except Exception as e:
            logger.error(f"Failed to ensure container exists: {e}")
            raise BlobStorageError(f"Container creation failed: {e}")

    async def upload_document(
        self,
        file_name: str,
        file_content: bytes,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        """ドキュメントのアップロード"""
        if not self._client:
            raise BlobStorageError("Blob Storage client not initialized")

        await self.ensure_container_exists()

        try:
            # ファイル名の正規化（パス区切り文字を統一）
            blob_name = file_name.replace("\\", "/")

            # メタデータの準備
            blob_metadata = metadata or {}
            blob_metadata.update(
                {
                    "uploaded_at": datetime.utcnow().isoformat(),
                    "content_type": content_type,
                    "file_size": str(len(file_content)),
                }
            )

            # Blobクライアント取得
            blob_client = self._client.get_blob_client(
                container=self.container_name, blob=blob_name
            )

            # アップロード実行
            await blob_client.upload_blob(
                data=file_content,
                content_type=content_type,
                metadata=blob_metadata,
                overwrite=True,
            )

            blob_url: str = blob_client.url
            logger.info(f"Document uploaded successfully: {blob_name}")
            return blob_url

        except Exception as e:
            logger.error(f"Failed to upload document '{file_name}': {e}")
            raise BlobStorageError(f"Upload failed: {e}")

    async def download_document(self, blob_name: str) -> bytes:
        """ドキュメントのダウンロード"""
        if not self._client:
            raise BlobStorageError("Blob Storage client not initialized")

        try:
            blob_client = self._client.get_blob_client(
                container=self.container_name, blob=blob_name
            )

            download_stream = await blob_client.download_blob()
            content: bytes = await download_stream.readall()

            logger.debug(f"Document downloaded: {blob_name}")
            return content

        except ResourceNotFoundError:
            logger.warning(f"Document not found: {blob_name}")
            raise BlobStorageError(f"Document not found: {blob_name}")
        except Exception as e:
            logger.error(f"Failed to download document '{blob_name}': {e}")
            raise BlobStorageError(f"Download failed: {e}")

    async def get_document_metadata(self, blob_name: str) -> Dict[str, Any]:
        """ドキュメントのメタデータ取得"""
        if not self._client:
            raise BlobStorageError("Blob Storage client not initialized")

        try:
            blob_client = self._client.get_blob_client(
                container=self.container_name, blob=blob_name
            )

            properties = await blob_client.get_blob_properties()

            return {
                "name": blob_name,
                "size": properties.size,
                "content_type": properties.content_settings.content_type,
                "last_modified": (
                    properties.last_modified.isoformat()
                    if properties.last_modified
                    else None
                ),
                "etag": properties.etag,
                "metadata": properties.metadata or {},
            }

        except ResourceNotFoundError:
            logger.warning(f"Document not found: {blob_name}")
            raise BlobStorageError(f"Document not found: {blob_name}")
        except Exception as e:
            logger.error(f"Failed to get metadata for '{blob_name}': {e}")
            raise BlobStorageError(f"Metadata retrieval failed: {e}")

    async def list_documents(self, prefix: str = "") -> List[Dict[str, Any]]:
        """ドキュメント一覧取得"""
        if not self._client:
            raise BlobStorageError("Blob Storage client not initialized")

        try:
            container_client = self._client.get_container_client(self.container_name)

            documents = []
            async for blob in container_client.list_blobs(name_starts_with=prefix):
                documents.append(
                    {
                        "name": blob.name,
                        "size": blob.size,
                        "content_type": (
                            blob.content_settings.content_type
                            if blob.content_settings
                            else None
                        ),
                        "last_modified": (
                            blob.last_modified.isoformat()
                            if blob.last_modified
                            else None
                        ),
                        "etag": blob.etag,
                        "metadata": blob.metadata or {},
                    }
                )

            logger.debug(f"Listed {len(documents)} documents with prefix '{prefix}'")
            return documents

        except Exception as e:
            logger.error(f"Failed to list documents: {e}")
            raise BlobStorageError(f"List operation failed: {e}")

    async def delete_document(self, blob_name: str) -> bool:
        """ドキュメントの削除"""
        if not self._client:
            raise BlobStorageError("Blob Storage client not initialized")

        try:
            blob_client = self._client.get_blob_client(
                container=self.container_name, blob=blob_name
            )

            await blob_client.delete_blob()
            logger.info(f"Document deleted: {blob_name}")
            return True

        except ResourceNotFoundError:
            logger.warning(f"Document not found for deletion: {blob_name}")
            return False
        except Exception as e:
            logger.error(f"Failed to delete document '{blob_name}': {e}")
            raise BlobStorageError(f"Delete failed: {e}")

    async def get_service_info(self) -> Dict[str, Any]:
        """サービス情報取得"""
        if not self._client:
            return {
                "status": "not_configured",
                "account_name": None,
                "container_name": None,
            }

        try:
            # アカウント情報取得
            account_info = await self._client.get_account_information()

            # コンテナ情報取得
            container_client = self._client.get_container_client(self.container_name)
            container_props = await container_client.get_container_properties()

            return {
                "status": "healthy",
                "account_name": self.account_name,
                "container_name": self.container_name,
                "account_kind": account_info.get("account_kind"),
                "sku_name": account_info.get("sku_name"),
                "container_last_modified": (
                    container_props.last_modified.isoformat()
                    if container_props.last_modified
                    else None
                ),
            }

        except Exception as e:
            logger.error(f"Failed to get service info: {e}")
            return {
                "status": "error",
                "account_name": self.account_name,
                "container_name": self.container_name,
                "error": str(e),
            }

    async def close(self) -> None:
        """リソースのクリーンアップ"""
        if self._client:
            await self._client.close()
            logger.debug("Blob Storage client closed")
