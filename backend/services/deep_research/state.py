from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from typing_extensions import TypedDict

# 型エイリアス
Document = Dict[str, Any]  # Azure Search のドキュメント JSON


@dataclass
class SearchResult:
    """検索結果の単一ドキュメント."""

    content: str
    source: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentState(TypedDict):
    """LangGraph Deep Research エージェントで共有される状態。

    Attributes
    ----------
    question: str
        ユーザーからの元質問。
    search_results: List[SearchResult]
        検索で取得したドキュメントのリスト。
    search_queries: List[str]
        現在までに実行した検索クエリ履歴。
    search_count: int
        検索実行回数。
    max_searches: int
        最大検索回数。
    relevance_threshold: float
        関連度の閾値。
    min_documents: int
        最低必要ドキュメント数。
    is_sufficient: bool
        情報が十分かどうか。
    final_report: str
        生成されたレポート。
    session_id: str
        セッションID。
    current_node: str
        現在のノード名。
    error_message: Optional[str]
        エラーメッセージ。
    """

    question: str
    session_id: str
    search_results: List[SearchResult]
    search_queries: List[str]
    search_count: int
    max_searches: int
    relevance_threshold: float
    min_documents: int
    is_sufficient: bool
    final_report: str
    current_node: str
    error_message: Optional[str]


def create_initial_state(question: str, session_id: str) -> AgentState:
    """初期状態を作成する."""
    return AgentState(
        question=question,
        session_id=session_id,
        search_results=[],
        search_queries=[],
        search_count=0,
        max_searches=3,
        relevance_threshold=0.7,
        min_documents=5,
        is_sufficient=False,
        final_report="",
        current_node="start",
        error_message=None,
    )


def add_search_results(state: AgentState, results: List[SearchResult]) -> AgentState:
    """検索結果を追加し、重複を除去."""
    existing_sources = {r.source for r in state["search_results"]}
    new_results = [r for r in results if r.source not in existing_sources]

    return {
        **state,
        "search_results": state["search_results"] + new_results,
        "search_count": state["search_count"] + 1,
    }


def get_high_relevance_docs(state: AgentState) -> List[SearchResult]:
    """高関連度のドキュメントのみを返す."""
    return [
        r for r in state["search_results"] if r.score >= state["relevance_threshold"]
    ]


def should_continue_search(state: AgentState) -> bool:
    """検索を続行すべきかを判定."""
    if state["search_count"] >= state["max_searches"]:
        return False

    high_relevance_docs = get_high_relevance_docs(state)
    return len(high_relevance_docs) < state["min_documents"]
