"""
セッション関連のGraphQL型定義
"""

import strawberry
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum

from .message import MessageType


@strawberry.type
@dataclass
class SessionType:
    """セッション型"""

    id: str
    title: str
    created_at: str
    updated_at: Optional[str] = None
    messages: List[MessageType] = strawberry.field(default_factory=list)


@strawberry.input
class SessionInput:
    """セッション入力型"""

    title: str = "新しいチャット"


@strawberry.enum
class SessionSortField(Enum):
    """セッションソートフィールド"""

    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    TITLE = "title"


@strawberry.enum
class SortOrder(Enum):
    """ソート順序"""

    ASC = "asc"
    DESC = "desc"


@strawberry.input
class SessionFilterInput:
    """セッションフィルター入力型"""

    search_query: Optional[str] = None  # タイトルや内容での検索
    created_after: Optional[str] = None  # 作成日時以降
    created_before: Optional[str] = None  # 作成日時以前
    has_messages: Optional[bool] = None  # メッセージがあるかどうか


@strawberry.input
class SessionSortInput:
    """セッションソート入力型"""

    field: SessionSortField = SessionSortField.CREATED_AT
    order: SortOrder = SortOrder.DESC


@strawberry.input
class SessionListInput:
    """セッション一覧取得入力型"""

    filter: Optional[SessionFilterInput] = None
    sort: Optional[SessionSortInput] = None
    limit: Optional[int] = None  # 取得件数制限
    offset: Optional[int] = None  # オフセット（ページネーション用）
    include_messages: bool = False  # メッセージを含めるかどうか


@strawberry.input
class UpdateSessionTitleInput:
    """セッションタイトル更新入力型"""

    title: str


@strawberry.type
@dataclass
class SessionListResult:
    """セッション一覧結果型"""

    sessions: List[SessionType]
    total_count: int
    has_more: bool
