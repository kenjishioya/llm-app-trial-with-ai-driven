"""
データベースモデル
"""

from typing import TYPE_CHECKING
from sqlalchemy.ext.declarative import declarative_base

# SQLAlchemy Base
Base = declarative_base()

# 型チェック時のみインポート
if TYPE_CHECKING:
    from .session import Session
    from .message import Message, MessageRole
else:
    # モデルをインポート（循環参照回避のため最後に）
    from .session import Session  # noqa: E402
    from .message import Message, MessageRole  # noqa: E402

__all__ = ["Base", "Session", "Message", "MessageRole"]
