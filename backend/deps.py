"""
依存注入設定
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from models import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """データベースセッション取得"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
