"""
GraphQL Subscription リゾルバ
"""

import strawberry
import uuid
from typing import AsyncGenerator, Optional
from dataclasses import dataclass
import json

from services import RAGService
from services.deep_research import DeepResearchLangGraphAgent
from models.message import Message, MessageRole
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
    async def streamDeepResearch(
        self,
        research_id: str,
        session_id: str,
        question: str,
    ) -> AsyncGenerator[DeepResearchProgress, None]:
        """Deep Research進捗ストリーミング"""
        # ログ追加: パラメータ受信確認
        print("🔍 Deep Research Subscription called with:")
        print(f"  research_id: '{research_id}'")
        print(f"  session_id: '{session_id}'")
        print(f"  question: '{question}'")

        try:
            # 空文字列チェック
            if not research_id or not session_id or not question:
                error_msg = f"Missing required parameters: research_id='{research_id}', session_id='{session_id}', question='{question}'"
                print(f"❌ {error_msg}")
                yield DeepResearchProgress(
                    content=f"Error: {error_msg}",
                    research_id=research_id or "unknown",
                    session_id=session_id or "unknown",
                    is_complete=True,
                    current_node="error",
                    progress_percentage=0,
                )
                return

            # セッションIDをUUIDに変換
            try:
                session_uuid = uuid.UUID(session_id)
                print("✅ Session ID validation passed")
            except ValueError:
                error_msg = f"Invalid session ID format: {session_id}"
                print(f"❌ {error_msg}")
                yield DeepResearchProgress(
                    content=error_msg,
                    research_id=research_id,
                    session_id=session_id,
                    is_complete=True,
                    current_node="error",
                    progress_percentage=0,
                )
                return

            print("🚀 Starting Deep Research agent...")

            # Deep Research エージェントを初期化
            agent = DeepResearchLangGraphAgent()

            progress_count = 0
            total_steps = 10  # 概算のステップ数
            final_report = None

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

                # レポート本文(最終)の判定: Markdown ヘッダーで始まる長文
                is_report = progress_message.lstrip().startswith("# ")

                # 完了判定
                is_error = "エラー" in progress_message
                is_final_step = progress_percentage >= 100 or is_report
                if is_final_step:
                    current_node = "complete"
                    progress_percentage = 100
                    if is_report:
                        final_report = progress_message

                is_complete = is_error or is_final_step

                print(
                    f"📊 Progress: {progress_percentage}% - {current_node} - {progress_message[:50]}..."
                )

                yield DeepResearchProgress(
                    content=progress_message,
                    research_id=research_id,
                    session_id=session_id,
                    is_complete=is_complete,
                    current_node=current_node,
                    progress_percentage=progress_percentage,
                )

                if is_complete:
                    print("✅ Deep Research completed")

                    # 最終レポートをアシスタントメッセージとして保存
                    if final_report:
                        try:
                            async for db in get_db():
                                # アシスタントメッセージを作成・保存
                                assistant_message = Message(
                                    session_id=str(session_uuid),
                                    role=MessageRole.ASSISTANT,
                                    content=final_report,
                                    citations=None,
                                    meta_data=json.dumps(
                                        {
                                            "research_id": research_id,
                                            "type": "deep_research_report",
                                        }
                                    ),
                                )
                                db.add(assistant_message)
                                await db.commit()
                                await db.refresh(assistant_message)
                                print("✅ Deep Research report saved to database")
                                break
                        except Exception as save_error:
                            print(
                                f"❌ Failed to save Deep Research report: {str(save_error)}"
                            )

                    break

        except Exception as e:
            error_msg = f"Deep Research Error: {str(e)}"
            print(f"❌ {error_msg}")
            print(f"❌ Exception type: {type(e).__name__}")
            import traceback

            print(f"❌ Traceback: {traceback.format_exc()}")

            yield DeepResearchProgress(
                content=error_msg,
                research_id=research_id or "unknown",
                session_id=session_id or "unknown",
                is_complete=True,
                current_node="error",
                progress_percentage=0,
            )
