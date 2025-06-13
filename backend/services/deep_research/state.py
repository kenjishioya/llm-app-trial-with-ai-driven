from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from langgraph.graph import State

# 型エイリアス
Document = Dict[str, Any]  # Azure Search のドキュメント JSON


@dataclass
class SearchResult:
    """検索結果の単一ドキュメント."""

    content: str
    source: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentState(State):
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
    search_results: List[SearchResult] = field(default_factory=list)
    search_queries: List[str] = field(default_factory=list)
    search_count: int = 0
    max_searches: int = 3
    relevance_threshold: float = 0.7
    min_documents: int = 5
    is_sufficient: bool = False
    final_report: str = ""
    current_node: str = "start"
    error_message: Optional[str] = None

    # LangGraph に必要な state_key プロパティ
    @classmethod
    def state_keys(cls):  # type: ignore[override]
        return [
            "question",
            "session_id",
            "search_results",
            "search_queries",
            "search_count",
            "max_searches",
            "relevance_threshold",
            "min_documents",
            "is_sufficient",
            "final_report",
            "current_node",
            "error_message",
        ]

    def add_search_results(self, results: List[SearchResult]) -> None:
        """検索結果を追加し、重複を除去."""
        existing_sources = {r.source for r in self.search_results}
        new_results = [r for r in results if r.source not in existing_sources]
        self.search_results.extend(new_results)
        self.search_count += 1

    def get_high_relevance_docs(self) -> List[SearchResult]:
        """高関連度のドキュメントのみを返す."""
        return [r for r in self.search_results if r.score >= self.relevance_threshold]

    def should_continue_search(self) -> bool:
        """検索を続行すべきかを判定."""
        if self.search_count >= self.max_searches:
            return False

        high_relevance_docs = self.get_high_relevance_docs()
        return len(high_relevance_docs) < self.min_documents
