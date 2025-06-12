"""
ドキュメント関連のGraphQL型定義
"""

import strawberry
from typing import List, Optional
from dataclasses import dataclass


@strawberry.type
@dataclass
class DocumentMetadataType:
    """ドキュメントメタデータ型"""

    file_type: str
    file_size: int
    created_at: str
    chunk_index: int
    chunk_count: int


@strawberry.type
@dataclass
class DocumentType:
    """ドキュメント型"""

    id: str
    title: str
    content: str
    score: float
    source: str
    url: str
    metadata: DocumentMetadataType


@strawberry.type
@dataclass
class SearchResultType:
    """検索結果型"""

    query: str
    total_count: int
    documents: List[DocumentType]
    execution_time_ms: int


@strawberry.input
@dataclass
class SearchInput:
    """検索入力型"""

    query: str
    top_k: Optional[int] = 10
    filters: Optional[str] = None  # JSON文字列として受け取り


@strawberry.input
@dataclass
class UploadDocumentInput:
    """ドキュメントアップロード入力型"""

    file_name: str
    file_content: str  # Base64エンコードされたファイル内容
    file_type: str
    title: Optional[str] = None
    metadata: Optional[str] = None  # JSON文字列として受け取り


@strawberry.type
@dataclass
class UploadDocumentPayload:
    """ドキュメントアップロード結果型"""

    document_id: str
    file_name: str
    status: str
    message: str
    chunks_created: int
