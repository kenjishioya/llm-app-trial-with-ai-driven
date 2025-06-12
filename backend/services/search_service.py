"""
Azure AI Search サービス
Task 3-1A-2: SearchServiceクラス実装
"""

import logging
from typing import List, Dict, Any, Optional
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError

from config import get_settings

logger = logging.getLogger(__name__)


class SearchServiceError(Exception):
    """検索サービス例外"""

    pass


class SearchService:
    """Azure AI Search サービス"""

    def __init__(self) -> None:
        """初期化"""
        self.settings = get_settings()
        self.search_client: Optional[SearchClient] = None
        self.index_client: Optional[SearchIndexClient] = None
        self._initialize_clients()

    def _initialize_clients(self) -> None:
        """Azure AI Searchクライアントを初期化"""
        try:
            if not self.settings.azure_search_endpoint:
                logger.warning("Azure Search endpoint not configured")
                return

            if not self.settings.azure_search_api_key:
                logger.warning("Azure Search API key not configured")
                return

            credential = AzureKeyCredential(self.settings.azure_search_api_key)

            # SearchClientを初期化
            self.search_client = SearchClient(
                endpoint=self.settings.azure_search_endpoint,
                index_name=self.settings.azure_search_index_name,
                credential=credential,
            )

            # SearchIndexClientを初期化
            self.index_client = SearchIndexClient(
                endpoint=self.settings.azure_search_endpoint, credential=credential
            )

            logger.info("Azure AI Search clients initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Azure AI Search clients: {e}")
            raise SearchServiceError(f"Client initialization failed: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """ヘルスチェック"""
        try:
            if not self.search_client or not self.index_client:
                return {
                    "status": "unhealthy",
                    "error": "Clients not initialized",
                    "details": {
                        "search_client": self.search_client is not None,
                        "index_client": self.index_client is not None,
                    },
                }

            # サービス統計を取得してヘルスチェック
            service_stats = self.index_client.get_service_statistics()

            return {
                "status": "healthy",
                "service_stats": {
                    "counters": {
                        "document_count": service_stats.get("counters", {}).get(
                            "document_count", 0
                        ),
                        "index_count": service_stats.get("counters", {}).get(
                            "index_count", 0
                        ),
                        "indexer_count": service_stats.get("counters", {}).get(
                            "indexer_count", 0
                        ),
                        "data_source_count": service_stats.get("counters", {}).get(
                            "data_source_count", 0
                        ),
                        "storage_size": service_stats.get("counters", {}).get(
                            "storage_size", 0
                        ),
                    },
                    "limits": {
                        "max_indexes_allowed": service_stats.get("limits", {}).get(
                            "max_indexes_allowed", 0
                        ),
                        "max_fields_per_index": service_stats.get("limits", {}).get(
                            "max_fields_per_index", 0
                        ),
                        "max_complex_collection_fields_per_index": service_stats.get(
                            "limits", {}
                        ).get("max_complex_collection_fields_per_index", 0),
                        "max_complex_objects_in_collections_per_document": service_stats.get(
                            "limits", {}
                        ).get(
                            "max_complex_objects_in_collections_per_document", 0
                        ),
                    },
                },
            }

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "details": {"exception_type": type(e).__name__},
            }

    async def search_documents(
        self,
        query: str,
        top: int = 10,
        skip: int = 0,
        search_fields: Optional[List[str]] = None,
        select_fields: Optional[List[str]] = None,
        filter_expression: Optional[str] = None,
        order_by: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """ドキュメント検索"""
        try:
            if not self.search_client:
                raise SearchServiceError("Search client not initialized")

            # 検索実行
            results = await self.search_client.search(
                search_text=query,
                top=top,
                skip=skip,
                search_fields=search_fields,
                select=select_fields,
                filter=filter_expression,
                order_by=order_by,
                include_total_count=True,
            )

            # 結果を整理
            documents = []
            async for result in results:
                documents.append(
                    {
                        "score": result.get("@search.score"),
                        "document": {
                            k: v for k, v in result.items() if not k.startswith("@")
                        },
                        "highlights": result.get("@search.highlights", {}),
                    }
                )

            return {
                "documents": documents,
                "total_count": getattr(results, "get_count", lambda: None)(),
                "query": query,
                "parameters": {
                    "top": top,
                    "skip": skip,
                    "search_fields": search_fields,
                    "select_fields": select_fields,
                    "filter": filter_expression,
                    "order_by": order_by,
                },
            }

        except Exception as e:
            logger.error(f"Document search failed: {e}")
            raise SearchServiceError(f"Search failed: {e}")

    async def vector_search(
        self,
        vector: List[float],
        vector_field: str = "content_vector",
        top: int = 10,
        filter_expression: Optional[str] = None,
        select_fields: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """ベクトル検索"""
        try:
            if not self.search_client:
                raise SearchServiceError("Search client not initialized")

            # ベクトル検索クエリを作成
            vector_query = VectorizedQuery(
                vector=vector, k_nearest_neighbors=top, fields=vector_field
            )

            # 検索実行
            results = await self.search_client.search(
                search_text=None,
                vector_queries=[vector_query],
                select=select_fields,
                filter=filter_expression,
                top=top,
            )

            # 結果を整理
            documents = []
            async for result in results:
                documents.append(
                    {
                        "score": result.get("@search.score"),
                        "document": {
                            k: v for k, v in result.items() if not k.startswith("@")
                        },
                    }
                )

            return {
                "documents": documents,
                "vector_field": vector_field,
                "parameters": {
                    "top": top,
                    "filter": filter_expression,
                    "select_fields": select_fields,
                },
            }

        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            raise SearchServiceError(f"Vector search failed: {e}")

    async def hybrid_search(
        self,
        query: str,
        vector: List[float],
        vector_field: str = "content_vector",
        top: int = 10,
        search_fields: Optional[List[str]] = None,
        select_fields: Optional[List[str]] = None,
        filter_expression: Optional[str] = None,
    ) -> Dict[str, Any]:
        """ハイブリッド検索（テキスト + ベクトル）"""
        try:
            if not self.search_client:
                raise SearchServiceError("Search client not initialized")

            # ベクトル検索クエリを作成
            vector_query = VectorizedQuery(
                vector=vector, k_nearest_neighbors=top, fields=vector_field
            )

            # ハイブリッド検索実行
            results = await self.search_client.search(
                search_text=query,
                vector_queries=[vector_query],
                search_fields=search_fields,
                select=select_fields,
                filter=filter_expression,
                top=top,
                include_total_count=True,
            )

            # 結果を整理
            documents = []
            async for result in results:
                documents.append(
                    {
                        "score": result.get("@search.score"),
                        "document": {
                            k: v for k, v in result.items() if not k.startswith("@")
                        },
                        "highlights": result.get("@search.highlights", {}),
                    }
                )

            return {
                "documents": documents,
                "total_count": getattr(results, "get_count", lambda: None)(),
                "query": query,
                "vector_field": vector_field,
                "parameters": {
                    "top": top,
                    "search_fields": search_fields,
                    "select_fields": select_fields,
                    "filter": filter_expression,
                },
            }

        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            raise SearchServiceError(f"Hybrid search failed: {e}")

    async def get_document(self, document_id: str) -> Dict[str, Any]:
        """ドキュメント取得"""
        try:
            if not self.search_client:
                raise SearchServiceError("Search client not initialized")

            document = await self.search_client.get_document(key=document_id)
            return {"document": document}

        except ResourceNotFoundError:
            return {"document": None, "error": "Document not found"}
        except Exception as e:
            logger.error(f"Get document failed: {e}")
            raise SearchServiceError(f"Get document failed: {e}")

    async def upload_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """ドキュメントアップロード"""
        try:
            if not self.search_client:
                raise SearchServiceError("Search client not initialized")

            result = await self.search_client.upload_documents(documents=documents)

            # 結果を整理
            success_count = sum(1 for r in result if r.succeeded)
            failed_count = len(result) - success_count
            errors = [
                {"key": r.key, "error": r.error_message}
                for r in result
                if not r.succeeded
            ]

            return {
                "success_count": success_count,
                "failed_count": failed_count,
                "total_count": len(documents),
                "errors": errors,
            }

        except Exception as e:
            logger.error(f"Upload documents failed: {e}")
            raise SearchServiceError(f"Upload documents failed: {e}")

    async def delete_documents(self, document_ids: List[str]) -> Dict[str, Any]:
        """ドキュメント削除"""
        try:
            if not self.search_client:
                raise SearchServiceError("Search client not initialized")

            # 削除用ドキュメントを作成
            documents_to_delete = [{"id": doc_id} for doc_id in document_ids]

            result = await self.search_client.delete_documents(
                documents=documents_to_delete
            )

            # 結果を整理
            success_count = sum(1 for r in result if r.succeeded)
            failed_count = len(result) - success_count
            errors = [
                {"key": r.key, "error": r.error_message}
                for r in result
                if not r.succeeded
            ]

            return {
                "success_count": success_count,
                "failed_count": failed_count,
                "total_count": len(document_ids),
                "errors": errors,
            }

        except Exception as e:
            logger.error(f"Delete documents failed: {e}")
            raise SearchServiceError(f"Delete documents failed: {e}")

    async def get_index_info(self) -> Dict[str, Any]:
        """インデックス情報取得"""
        try:
            if not self.index_client:
                raise SearchServiceError("Index client not initialized")

            try:
                index = self.index_client.get_index(
                    name=self.settings.azure_search_index_name
                )
                return {
                    "exists": True,
                    "name": index.name,
                    "fields_count": len(index.fields),
                    "fields": [
                        {
                            "name": field.name,
                            "type": str(field.type),
                            "searchable": field.searchable,
                            "filterable": field.filterable,
                            "retrievable": field.retrievable,
                            "sortable": field.sortable,
                            "facetable": field.facetable,
                            "key": field.key,
                        }
                        for field in index.fields
                    ],
                }
            except ResourceNotFoundError:
                return {
                    "exists": False,
                    "name": self.settings.azure_search_index_name,
                    "error": "Index not found",
                }

        except Exception as e:
            logger.error(f"Get index info failed: {e}")
            raise SearchServiceError(f"Get index info failed: {e}")

    def get_service_info(self) -> Dict[str, Any]:
        """サービス情報取得"""
        return {
            "endpoint": self.settings.azure_search_endpoint,
            "index_name": self.settings.azure_search_index_name,
            "clients_initialized": {
                "search_client": self.search_client is not None,
                "index_client": self.index_client is not None,
            },
            "configuration": {
                "endpoint_configured": bool(self.settings.azure_search_endpoint),
                "api_key_configured": bool(self.settings.azure_search_api_key),
                "index_name_configured": bool(self.settings.azure_search_index_name),
            },
        }
