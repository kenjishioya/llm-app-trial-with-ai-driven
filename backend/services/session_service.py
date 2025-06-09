"""
セッション管理サービス
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from models.session import Session


class SessionService:
    """セッション管理サービス"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(self, title: str = "新しいチャット") -> Session:
        """新しいセッションを作成"""
        session = Session(title=title)
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_session(self, session_id: str) -> Optional[Session]:
        """セッションIDでセッションを取得"""
        stmt = select(Session).where(Session.id == session_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_session_with_messages(self, session_id: str) -> Optional[Session]:
        """メッセージ付きでセッションを取得"""
        stmt = (
            select(Session)
            .options(selectinload(Session.messages))
            .where(Session.id == session_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_sessions(self, limit: int = 50, offset: int = 0) -> List[Session]:
        """セッション一覧を取得"""
        stmt = (
            select(Session)
            .order_by(Session.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_session(self, session_id: str, title: str) -> Optional[Session]:
        """セッションを更新"""
        stmt = (
            update(Session)
            .where(Session.id == session_id)
            .values(title=title)
            .returning(Session)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.scalar_one_or_none()

    async def delete_session(self, session_id: str) -> bool:
        """セッションを削除"""
        stmt = delete(Session).where(Session.id == session_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0
