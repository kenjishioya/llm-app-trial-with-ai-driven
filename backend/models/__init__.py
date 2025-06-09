"""
データベースモデル
"""

from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import settings  # type: ignore[attr-defined]

# SQLAlchemy設定
engine = create_async_engine(settings.database_url, echo=settings.debug, future=True)

Base = declarative_base()

AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

# 型チェック時のみインポート
if TYPE_CHECKING:
    from .session import Session
    from .message import Message, MessageRole
else:
    # モデルをインポート（循環参照回避のため最後に）
    from .session import Session  # noqa: E402
    from .message import Message, MessageRole  # noqa: E402

__all__ = ["Base", "AsyncSessionLocal", "Session", "Message", "MessageRole"]
