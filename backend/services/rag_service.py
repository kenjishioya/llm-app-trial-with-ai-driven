"""
RAGサービス
"""

import json
import uuid
from typing import Optional, List, Dict, Any, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from models.message import Message, MessageRole
from services.session_service import SessionService
from services.llm_service import LLMService


class RAGService:
    """RAGサービス"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.session_service = SessionService(db)
        self.llm_service = LLMService()

    async def ask_question(
        self,
        question: str,
        session_id: Optional[uuid.UUID] = None,
        deep_research: bool = False,
    ) -> Dict[str, Any]:
        """質問に回答（Phase 1簡易実装）"""
        try:
            # セッション取得または作成
            if session_id:
                session = await self.session_service.get_session(str(session_id))
                if not session:
                    raise ValueError(f"Session not found: {session_id}")
            else:
                session = await self.session_service.create_session()
                session_id = session.id

            # ユーザーメッセージを保存
            user_message = Message(
                session_id=str(session_id), role=MessageRole.USER, content=question
            )
            self.db.add(user_message)
            await self.db.commit()
            await self.db.refresh(user_message)

            # LLMで回答生成
            llm_response = await self.llm_service.generate_response(
                prompt=question,
                system_message="あなたは親切で知識豊富なAIアシスタントです。質問に対して正確で有用な回答を提供してください。",
            )

            # アシスタントメッセージを保存
            assistant_message = Message(
                session_id=str(session_id),
                role=MessageRole.ASSISTANT,
                content=llm_response.content,
                citations=json.dumps([]),  # Phase 1では空の引用
                meta_data=json.dumps(
                    {
                        "provider": llm_response.provider,
                        "model": llm_response.model,
                        "usage": llm_response.usage,
                    }
                ),
            )
            self.db.add(assistant_message)
            await self.db.commit()
            await self.db.refresh(assistant_message)

            return {
                "answer": llm_response.content,
                "session_id": str(session_id),
                "message_id": assistant_message.id,
                "citations": [],
                "metadata": {
                    "provider": llm_response.provider,
                    "model": llm_response.model,
                    "usage": llm_response.usage,
                },
            }

        except Exception as e:
            await self.db.rollback()
            raise e

    async def stream_answer(
        self,
        question: str,
        session_id: Optional[uuid.UUID] = None,
        deep_research: bool = False,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """ストリーミング回答（Phase 1簡易実装）"""
        try:
            # セッション取得または作成
            if session_id:
                session = await self.session_service.get_session(str(session_id))
                if not session:
                    raise ValueError(f"Session not found: {session_id}")
            else:
                session = await self.session_service.create_session()
                session_id = session.id

            # ユーザーメッセージを保存
            user_message = Message(
                session_id=str(session_id), role=MessageRole.USER, content=question
            )
            self.db.add(user_message)
            await self.db.commit()
            await self.db.refresh(user_message)

            # ストリーミング回答
            full_response = ""
            async for chunk in self.llm_service.stream_response(
                prompt=question,
                system_message="あなたは親切で知識豊富なAIアシスタントです。質問に対して正確で有用な回答を提供してください。",
            ):
                full_response += chunk.content
                yield {
                    "chunk": chunk.content,
                    "session_id": str(session_id),
                    "is_complete": False,
                }

            # アシスタントメッセージを保存
            assistant_message = Message(
                session_id=str(session_id),
                role=MessageRole.ASSISTANT,
                content=full_response,
                citations=json.dumps([]),
                meta_data=json.dumps({"provider": "streaming"}),
            )
            self.db.add(assistant_message)
            await self.db.commit()
            await self.db.refresh(assistant_message)

            # 完了通知
            yield {
                "chunk": "",
                "session_id": str(session_id),
                "message_id": assistant_message.id,
                "is_complete": True,
            }

        except Exception as e:
            await self.db.rollback()
            yield {
                "error": str(e),
                "session_id": str(session_id) if session_id else None,
                "is_complete": True,
            }

    async def get_message_history(
        self, session_id: uuid.UUID, limit: int = 50
    ) -> List[Message]:
        """メッセージ履歴を取得"""
        try:
            session = await self.session_service.get_session(str(session_id))
            if not session:
                return []

            session_with_messages = (
                await self.session_service.get_session_with_messages(str(session_id))
            )
            if not session_with_messages:
                return []

            # メッセージを作成日時順でソート
            messages = sorted(
                session_with_messages.messages, key=lambda m: m.created_at
            )
            return messages[-limit:] if len(messages) > limit else messages

        except Exception:
            return []
