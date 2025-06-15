"""
セッション管理サービス
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, or_, and_
from sqlalchemy.orm import selectinload

from models.session import Session
from models.message import Message


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
        session = result.scalar_one_or_none()
        return session if isinstance(session, Session) else None

    async def get_session_with_messages(self, session_id: str) -> Optional[Session]:
        """メッセージ付きでセッションを取得"""
        stmt = (
            select(Session)
            .options(selectinload(Session.messages))
            .where(Session.id == session_id)
        )
        result = await self.db.execute(stmt)
        session = result.scalar_one_or_none()
        return session if isinstance(session, Session) else None

    async def get_sessions(self, limit: int = 50, offset: int = 0) -> List[Session]:
        """セッション一覧を取得"""
        stmt = (
            select(Session)
            .order_by(Session.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        sessions = result.scalars().all()
        return [s for s in sessions if isinstance(s, Session)]

    async def get_sessions_with_messages(
        self, limit: int = 50, offset: int = 0
    ) -> List[Session]:
        """メッセージ付きでセッション一覧を取得"""
        stmt = (
            select(Session)
            .options(selectinload(Session.messages))
            .order_by(Session.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        sessions = result.scalars().all()
        return [s for s in sessions if isinstance(s, Session)]

    async def get_sessions_filtered(
        self,
        search_query: Optional[str] = None,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        has_messages: Optional[bool] = None,
        sort_field: str = "created_at",
        sort_order: str = "desc",
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        include_messages: bool = False,
    ) -> Dict[str, Any]:
        """フィルタリング・ソート機能付きセッション一覧取得"""

        # ベースクエリ
        if include_messages:
            stmt = select(Session).options(selectinload(Session.messages))
        else:
            stmt = select(Session)

        # フィルタリング条件を構築
        conditions = []

        # 検索クエリ（タイトルまたはメッセージ内容）
        if search_query:
            search_conditions = [Session.title.ilike(f"%{search_query}%")]

            # メッセージ内容も検索対象に含める
            if include_messages:
                search_conditions.append(
                    Session.messages.any(Message.content.ilike(f"%{search_query}%"))
                )

            conditions.append(or_(*search_conditions))

        # 作成日時フィルタ
        if created_after:
            conditions.append(Session.created_at >= created_after)

        if created_before:
            conditions.append(Session.created_at <= created_before)

        # メッセージ有無フィルタ
        if has_messages is not None:
            if has_messages:
                conditions.append(Session.messages.any())
            else:
                conditions.append(~Session.messages.any())

        # 条件を適用
        if conditions:
            stmt = stmt.where(and_(*conditions))

        # ソート
        sort_column = getattr(Session, sort_field, Session.created_at)
        if sort_order.lower() == "asc":
            stmt = stmt.order_by(sort_column.asc())
        else:
            stmt = stmt.order_by(sort_column.desc())

        # 総件数を取得（ページネーション用）
        count_stmt = select(func.count(Session.id))
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))

        count_result = await self.db.execute(count_stmt)
        total_count = count_result.scalar() or 0

        # ページネーション
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)

        # 実行
        result = await self.db.execute(stmt)
        sessions = result.scalars().all()

        # has_moreフラグを計算
        has_more = False
        if limit is not None and offset is not None:
            has_more = (offset + limit) < total_count

        return {
            "sessions": [s for s in sessions if isinstance(s, Session)],
            "total_count": total_count,
            "has_more": has_more,
        }

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
        session = result.scalar_one_or_none()
        return session if isinstance(session, Session) else None

    async def update_session_title(
        self, session_id: str, title: str
    ) -> Optional[Session]:
        """セッションタイトルのみを更新"""
        return await self.update_session(session_id, title)

    async def delete_session(self, session_id: str) -> bool:
        """セッションを削除（メッセージも含めてカスケード削除）"""
        # セッションを取得
        session = await self.get_session(session_id)
        if not session:
            return False

        # オブジェクトレベルで削除（cascadeが有効になる）
        await self.db.delete(session)
        await self.db.commit()
        return True

    async def delete_multiple_sessions(self, session_ids: List[str]) -> int:
        """複数のセッションを一括削除（メッセージも含めてカスケード削除）"""
        if not session_ids:
            return 0

        deleted_count = 0
        for session_id in session_ids:
            session = await self.get_session(session_id)
            if session:
                await self.db.delete(session)
                deleted_count += 1

        await self.db.commit()
        return deleted_count

    async def get_session_count(self) -> int:
        """総セッション数を取得"""
        stmt = select(func.count(Session.id))
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def search_sessions(self, query: str, limit: int = 20) -> List[Session]:
        """セッション検索（簡易版）"""
        stmt = (
            select(Session)
            .where(
                or_(
                    Session.title.ilike(f"%{query}%"),
                    Session.messages.any(Message.content.ilike(f"%{query}%")),
                )
            )
            .order_by(Session.updated_at.desc())
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        sessions = result.scalars().all()
        return [s for s in sessions if isinstance(s, Session)]
