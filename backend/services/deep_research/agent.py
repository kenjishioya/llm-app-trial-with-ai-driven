"""DeepResearchLangGraphAgent - Main agent class using LangGraph."""

from typing import AsyncIterator, Dict, Any
import logging

from langgraph.graph import StateGraph, END
from langgraph.graph.graph import CompiledGraph

from services.search_service import SearchService
from services.llm_service import LLMService
from .state import AgentState, create_initial_state
from .retrieve_node import RetrieveNode
from .decide_node import DecideNode
from .answer_node import AnswerNode

logger = logging.getLogger(__name__)


class DeepResearchLangGraphAgent:
    """LangGraph を使用した Deep Research エージェント."""

    def __init__(
        self, search_service: SearchService = None, llm_service: LLMService = None
    ):
        self.search_service = search_service or SearchService()
        self.llm_service = llm_service or LLMService()

        # ノードの初期化
        self.retrieve_node = RetrieveNode(self.search_service)
        self.decide_node = DecideNode()
        self.answer_node = AnswerNode(self.llm_service)

        # グラフの構築
        self.graph = self._build_graph()

    def _build_graph(self) -> CompiledGraph:
        """LangGraph StateGraph を構築."""
        workflow = StateGraph(AgentState)

        # ノードを追加
        workflow.add_node("retrieve", self.retrieve_node)
        workflow.add_node("decide", self.decide_node)
        workflow.add_node("answer", self.answer_node)

        # エッジを定義
        workflow.set_entry_point("retrieve")

        # retrieve → decide
        workflow.add_edge("retrieve", "decide")

        # decide → retrieve または answer (条件分岐)
        workflow.add_conditional_edges(
            "decide",
            self._should_continue,
            {"continue": "retrieve", "finish": "answer"},
        )

        # answer → END
        workflow.add_edge("answer", END)

        return workflow.compile()

    def _should_continue(self, state: AgentState) -> str:
        """次のノードを決定する条件分岐関数."""
        if state["is_sufficient"] or state["search_count"] >= state["max_searches"]:
            return "finish"
        else:
            return "continue"

    async def run(self, question: str, session_id: str) -> AsyncIterator[str]:
        """
        Deep Research を実行し、進捗をストリーミングで返す.

        Args:
            question: 研究質問
            session_id: セッションID

        Yields:
            進捗メッセージ
        """
        logger.info(f"DeepResearchAgent: 開始 - Question: {question[:100]}...")

        # 初期状態を作成
        initial_state = create_initial_state(question, session_id)

        try:
            # 進捗メッセージを送信
            yield "🔍 Deep Research を開始しています..."

            # グラフを実行
            async for event in self.graph.astream(initial_state):
                # イベントから現在のノードを特定
                current_node = self._get_current_node_from_event(event)

                if current_node == "retrieve":
                    search_count = event.get("search_count", 0)
                    yield f"📚 情報を検索中... ({search_count}/{initial_state['max_searches']})"

                elif current_node == "decide":
                    is_sufficient = event.get("is_sufficient", False)
                    if is_sufficient:
                        yield "✅ 十分な情報が収集されました"
                    else:
                        yield "🔄 追加の情報収集が必要です"

                elif current_node == "answer":
                    yield "📝 レポートを生成中..."

            # 最終結果を取得
            final_state = await self._get_final_state(initial_state)

            if final_state["error_message"]:
                yield f"❌ エラーが発生しました: {final_state['error_message']}"
            else:
                yield "✅ Deep Research が完了しました"
                yield f"📊 レポート生成完了 ({len(final_state['final_report'])} 文字)"

                # 最終レポートを返す
                yield final_state["final_report"]

        except Exception as e:
            logger.error(f"DeepResearchAgent: 実行エラー - {str(e)}")
            yield f"❌ システムエラー: {str(e)}"

    def _get_current_node_from_event(self, event: Dict[str, Any]) -> str:
        """イベントから現在のノード名を取得."""
        # LangGraphのイベント構造に基づいてノード名を抽出
        if isinstance(event, dict):
            current_node = event.get("current_node")
            return current_node if isinstance(current_node, str) else "unknown"
        return "unknown"

    async def _get_final_state(self, initial_state: AgentState) -> AgentState:
        """最終状態を取得（同期実行）."""
        try:
            final_result = await self.graph.ainvoke(initial_state)
            if isinstance(final_result, dict):
                return final_result  # type: ignore[return-value]
            else:
                # 予期しない型の場合はエラー状態を返す
                error_state = initial_state.copy()
                error_state["error_message"] = (
                    "Unexpected result type from graph execution"
                )
                error_state["final_report"] = (
                    "# エラーレポート\n\n予期しない実行結果です"
                )
                return error_state
        except Exception as e:
            logger.error(f"最終状態取得エラー: {str(e)}")
            # エラー時のフォールバック状態
            error_state = initial_state.copy()
            error_state["error_message"] = str(e)
            error_state["final_report"] = (
                f"# エラーレポート\n\n実行中にエラーが発生しました: {str(e)}"
            )
            return error_state

    async def run_sync(self, question: str, session_id: str) -> Dict[str, Any]:
        """
        同期的にDeep Researchを実行（テスト用）.

        Args:
            question: 研究質問
            session_id: セッションID

        Returns:
            実行結果の辞書
        """
        initial_state = create_initial_state(question, session_id)

        try:
            final_state = await self.graph.ainvoke(initial_state)

            return {
                "success": True,
                "report": final_state["final_report"],
                "search_count": final_state["search_count"],
                "document_count": len(final_state["search_results"]),
                "high_relevance_count": len(
                    [
                        r
                        for r in final_state["search_results"]
                        if r.score >= final_state["relevance_threshold"]
                    ]
                ),
                "error": None,
            }

        except Exception as e:
            logger.error(f"同期実行エラー: {str(e)}")
            return {
                "success": False,
                "report": None,
                "search_count": 0,
                "document_count": 0,
                "high_relevance_count": 0,
                "error": str(e),
            }

    def get_graph_visualization(self) -> str:
        """グラフの可視化情報を返す（デバッグ用）."""
        return """
Deep Research LangGraph Flow:
┌─────────────┐
│   START     │
└─────┬───────┘
      │
      v
┌─────────────┐
│  RETRIEVE   │ ←─────┐
│ (検索実行)   │       │
└─────┬───────┘       │
      │               │
      v               │
┌─────────────┐       │
│   DECIDE    │       │
│ (十分性判定) │       │
└─────┬───────┘       │
      │               │
      v               │
   十分？ ────No──────┘
      │
     Yes
      │
      v
┌─────────────┐
│   ANSWER    │
│(レポート生成)│
└─────┬───────┘
      │
      v
┌─────────────┐
│    END      │
└─────────────┘
"""
