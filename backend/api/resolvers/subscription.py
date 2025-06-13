"""
GraphQL Subscription リゾルバ
"""

import strawberry
import uuid
from typing import AsyncGenerator, Optional
from dataclasses import dataclass

from services import RAGService
from services.deep_research import DeepResearchLangGraphAgent
from deps import get_db


@strawberry.type
@dataclass
class StreamChunk:
    """ストリーミングチャンク"""

    content: str
    session_id: str
    is_complete: bool
    message_id: str = ""


@strawberry.type
@dataclass
class DeepResearchProgress:
    """Deep Research進捗チャンク"""

    content: str
    research_id: str
    session_id: str
    is_complete: bool
    current_node: str = ""
    progress_percentage: int = 0


@strawberry.type
class Subscription:
    """GraphQL Subscription"""

    @strawberry.subscription
    async def stream_answer(
        self,
        question: str,
        session_id: Optional[str] = None,
        deep_research: bool = False,
    ) -> AsyncGenerator[StreamChunk, None]:
        """ストリーミング回答"""
        async for db in get_db():
            rag_service = RAGService(db)

            # セッションIDがあればUUIDに変換
            session_uuid = None
            if session_id:
                try:
                    session_uuid = uuid.UUID(session_id)
                except ValueError:
                    yield StreamChunk(
                        content="Invalid session ID format",
                        session_id="",
                        is_complete=True,
                    )
                    return

            # ストリーミング処理
            try:
                async for chunk in rag_service.stream_answer(
                    question=question,
                    session_id=session_uuid,
                    deep_research=deep_research,
                ):
                    if "error" in chunk:
                        yield StreamChunk(
                            content=f"Error: {chunk['error']}",
                            session_id=chunk.get("session_id", ""),
                            is_complete=True,
                        )
                    else:
                        yield StreamChunk(
                            content=chunk.get("chunk", ""),
                            session_id=chunk["session_id"],
                            is_complete=chunk["is_complete"],
                            message_id=chunk.get("message_id", ""),
                        )
            except Exception as e:
                yield StreamChunk(
                    content=f"Error: {str(e)}",
                    session_id=session_id or "",
                    is_complete=True,
                )

    @strawberry.subscription
    async def stream_deep_research(
        self,
        research_id: str,
        session_id: str,
        question: str,
    ) -> AsyncGenerator[DeepResearchProgress, None]:
        """Deep Research進捗ストリーミング"""
        try:
            # セッションIDをUUIDに変換
            try:
                uuid.UUID(session_id)  # バリデーションのみ
            except ValueError:
                yield DeepResearchProgress(
                    content="Invalid session ID format",
                    research_id=research_id,
                    session_id=session_id,
                    is_complete=True,
                    current_node="error",
                    progress_percentage=0,
                )
                return

            # Deep Research エージェントを初期化
            agent = DeepResearchLangGraphAgent()

            progress_count = 0
            total_steps = 10  # 概算のステップ数

            # Deep Research実行
            async for progress_message in agent.run(question, session_id):
                progress_count += 1
                progress_percentage = min(
                    int((progress_count / total_steps) * 100), 100
                )

                # 進捗メッセージから現在のノードを推定
                current_node = "unknown"
                if "検索中" in progress_message:
                    current_node = "retrieve"
                elif "判定" in progress_message or "十分" in progress_message:
                    current_node = "decide"
                elif "レポート" in progress_message:
                    current_node = "answer"
                elif "完了" in progress_message:
                    current_node = "complete"
                    progress_percentage = 100

                is_complete = "完了" in progress_message or "エラー" in progress_message

                yield DeepResearchProgress(
                    content=progress_message,
                    research_id=research_id,
                    session_id=session_id,
                    is_complete=is_complete,
                    current_node=current_node,
                    progress_percentage=progress_percentage,
                )

                if is_complete:
                    break

        except Exception as e:
            yield DeepResearchProgress(
                content=f"Deep Research Error: {str(e)}",
                research_id=research_id,
                session_id=session_id,
                is_complete=True,
                current_node="error",
                progress_percentage=0,
            )
