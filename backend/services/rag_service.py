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
from services.search_service import SearchService


class RAGService:
    """RAGサービス"""

    def __init__(
        self, db: AsyncSession, search_service: Optional[SearchService] = None
    ):
        self.db = db
        self.session_service = SessionService(db)
        self.llm_service = LLMService()
        self.search_service = search_service or SearchService()

    async def ask_question(
        self,
        question: str,
        session_id: Optional[uuid.UUID] = None,
        deep_research: bool = False,
    ) -> Dict[str, Any]:
        """質問に回答（Azure AI Search統合版）"""
        try:
            # セッションIDが必須
            if not session_id:
                raise ValueError("Session ID is required")

            # セッション取得
            session = await self.session_service.get_session(str(session_id))
            if not session:
                raise ValueError(f"Session not found: {session_id}")

            # ユーザーメッセージを保存
            user_message = Message(
                session_id=str(session_id), role=MessageRole.USER, content=question
            )
            self.db.add(user_message)
            await self.db.commit()
            await self.db.refresh(user_message)

            # Azure AI Searchでドキュメント検索
            search_results = []
            citations = []
            context_text = ""

            try:
                search_response = await self.search_service.search_documents(
                    query=question,
                    top=3,
                    select_fields=[
                        "id",
                        "title",
                        "content",
                        "file_name",
                        "source_url",
                        "file_type",
                        "file_size",
                        "created_at",
                        "chunk_index",
                        "chunk_count",
                    ],
                )

                search_results = search_response.get("documents", [])

                # 検索結果から引用情報とコンテキストを構築
                for idx, result in enumerate(search_results, 1):
                    doc = result.get("document", {})
                    citations.append(
                        {
                            "id": idx,
                            "title": doc.get("title", "Unknown Document"),
                            "content": doc.get("content", "")[:200] + "...",
                            "score": result.get("score", 0.0),
                            "source": doc.get("file_name", "Unknown Source"),
                            "url": doc.get("source_url", ""),
                        }
                    )

                    # コンテキストテキスト構築
                    context_text += f"[{idx}] {doc.get('title', 'Document')}\n"
                    context_text += f"{doc.get('content', '')}\n\n"

            except Exception as search_error:
                # 検索エラーの場合はログに記録して続行
                print(f"Search error: {search_error}")

            # システムメッセージ構築（検索結果がある場合は引用付き回答を指示）
            if context_text:
                system_message = f"""あなたは親切で知識豊富なAIアシスタントです。
以下の検索結果を参考にして、質問に対して正確で有用な回答を提供してください。
回答には必ず引用番号 [1], [2], [3] を含めて、どの情報源から得た情報かを明示してください。

検索結果:
{context_text}

質問に対して、上記の検索結果を参考にして回答してください。"""
            else:
                system_message = "あなたは親切で知識豊富なAIアシスタントです。質問に対して正確で有用な回答を提供してください。"

            # LLMで回答生成
            llm_response = await self.llm_service.generate_response(
                prompt=question,
                system_message=system_message,
            )

            # アシスタントメッセージを保存
            assistant_message = Message(
                session_id=str(session_id),
                role=MessageRole.ASSISTANT,
                content=llm_response.content,
                citations=json.dumps(citations),  # 引用情報をJSON形式で保存
                meta_data=json.dumps(
                    {
                        "provider": llm_response.provider,
                        "model": llm_response.model,
                        "usage": llm_response.usage,
                        "search_results_count": len(search_results),
                        "has_context": bool(context_text),
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
                "citations": citations,
                "metadata": {
                    "provider": llm_response.provider,
                    "model": llm_response.model,
                    "usage": llm_response.usage,
                    "search_results_count": len(search_results),
                    "has_context": bool(context_text),
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
        """ストリーミング回答（Azure AI Search統合版）"""
        try:
            # セッションIDが必須
            if not session_id:
                yield {
                    "error": "Session ID is required",
                    "session_id": None,
                    "is_complete": True,
                }
                return

            # セッション取得
            session = await self.session_service.get_session(str(session_id))
            if not session:
                yield {
                    "error": f"Session not found: {session_id}",
                    "session_id": str(session_id),
                    "is_complete": True,
                }
                return

            # ユーザーメッセージを保存
            user_message = Message(
                session_id=str(session_id), role=MessageRole.USER, content=question
            )
            self.db.add(user_message)
            await self.db.commit()
            await self.db.refresh(user_message)

            # Azure AI Searchでドキュメント検索
            search_results = []
            citations = []
            context_text = ""

            try:
                search_response = await self.search_service.search_documents(
                    query=question,
                    top=3,
                    select_fields=[
                        "id",
                        "title",
                        "content",
                        "file_name",
                        "source_url",
                        "file_type",
                        "file_size",
                        "created_at",
                        "chunk_index",
                        "chunk_count",
                    ],
                )

                search_results = search_response.get("documents", [])

                # 検索結果から引用情報とコンテキストを構築
                for idx, result in enumerate(search_results, 1):
                    doc = result.get("document", {})
                    citations.append(
                        {
                            "id": idx,
                            "title": doc.get("title", "Unknown Document"),
                            "content": doc.get("content", "")[:200] + "...",
                            "score": result.get("score", 0.0),
                            "source": doc.get("file_name", "Unknown Source"),
                            "url": doc.get("source_url", ""),
                        }
                    )

                    # コンテキストテキスト構築
                    context_text += f"[{idx}] {doc.get('title', 'Document')}\n"
                    context_text += f"{doc.get('content', '')}\n\n"

            except Exception as search_error:
                print(f"Search error: {search_error}")

            # システムメッセージ構築
            if context_text:
                system_message = f"""あなたは親切で知識豊富なAIアシスタントです。
以下の検索結果を参考にして、質問に対して正確で有用な回答を提供してください。
回答には必ず引用番号 [1], [2], [3] を含めて、どの情報源から得た情報かを明示してください。

検索結果:
{context_text}

質問に対して、上記の検索結果を参考にして回答してください。"""
            else:
                system_message = "あなたは親切で知識豊富なAIアシスタントです。質問に対して正確で有用な回答を提供してください。"

            # ストリーミング回答
            full_response = ""
            async for chunk in self.llm_service.stream_response(
                prompt=question,
                system_message=system_message,
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
                citations=json.dumps(citations),
                meta_data=json.dumps(
                    {
                        "provider": "streaming",
                        "search_results_count": len(search_results),
                        "has_context": bool(context_text),
                    }
                ),
            )
            self.db.add(assistant_message)
            await self.db.commit()
            await self.db.refresh(assistant_message)

            # 完了通知
            yield {
                "chunk": "",
                "session_id": str(session_id),
                "message_id": assistant_message.id,
                "citations": citations,
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

    async def search_documents(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """ドキュメント検索（直接検索用）"""
        try:
            # フィルタを文字列に変換（Azure AI Searchのフィルタ形式）
            filter_expression = None
            if filters:
                filter_parts = []
                for key, value in filters.items():
                    if isinstance(value, str):
                        filter_parts.append(f"{key} eq '{value}'")
                    else:
                        filter_parts.append(f"{key} eq {value}")
                filter_expression = " and ".join(filter_parts)

            search_response = await self.search_service.search_documents(
                query=query,
                top=top_k,  # SearchServiceのAPIに合わせてtopパラメータを使用
                select_fields=[
                    "id",
                    "title",
                    "content",
                    "file_name",
                    "source_url",
                    "file_type",
                    "file_size",
                    "created_at",
                    "chunk_index",
                    "chunk_count",
                ],
                filter_expression=filter_expression,
            )

            # 検索結果を整形
            formatted_results = []
            for result in search_response.get("documents", []):
                doc = result.get("document", {})
                formatted_results.append(
                    {
                        "id": doc.get("id", ""),
                        "title": doc.get("title", "Unknown Document"),
                        "content": doc.get("content", ""),
                        "score": result.get("score", 0.0),
                        "source": doc.get("file_name", "Unknown Source"),
                        "url": doc.get("source_url", ""),
                        "metadata": {
                            "file_type": doc.get("file_type", ""),
                            "file_size": doc.get("file_size", 0),
                            "created_at": doc.get("created_at", ""),
                            "chunk_index": doc.get("chunk_index", 0),
                            "chunk_count": doc.get("chunk_count", 1),
                        },
                    }
                )

            return formatted_results

        except Exception as e:
            print(f"Document search error: {e}")
            return []
