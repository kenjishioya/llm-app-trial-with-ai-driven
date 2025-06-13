from __future__ import annotations

import asyncio
from typing import List, Dict, Any
import logging

from langgraph.graph import Node

from services.search_service import SearchService
from .state import AgentState, SearchResult

logger = logging.getLogger(__name__)


class RetrieveNode(Node[AgentState, AgentState]):
    """RetrieveNode – Azure AI Search で関連ドキュメントを取得するノード。

    This node adds search results to ``state.retrieved_docs`` and records the
    executed query in ``state.search_queries``.
    """

    def __init__(
        self, search_service: SearchService | None = None, *, top_k: int = 10
    ) -> None:  # noqa: D401
        self._search = search_service or SearchService()
        self._top_k = top_k

    async def __call__(self, state: AgentState) -> Dict[str, Any]:
        """
        検索を実行し、結果を状態に追加する.

        Args:
            state: 現在のエージェント状態

        Returns:
            更新された状態の辞書
        """
        logger.info(
            f"RetrieveNode: 検索実行 (試行 {state.search_count + 1}/{state.max_searches})"
        )

        try:
            # 検索クエリを生成（質問をそのまま使用、将来的にはクエリ拡張も可能）
            search_query = state.question

            # Azure AI Search で検索実行
            search_response = await self._search.search_documents(
                query=search_query, top=self._top_k
            )

            # 検索結果を SearchResult オブジェクトに変換
            search_results = []
            for doc in search_response.get("documents", []):
                search_result = SearchResult(
                    content=doc.get("content", ""),
                    source=doc.get("source", "unknown"),
                    score=doc.get("@search.score", 0.0),
                    metadata={
                        "title": doc.get("title", ""),
                        "url": doc.get("url", ""),
                        "chunk_id": doc.get("chunk_id", ""),
                    },
                )
                search_results.append(search_result)

            # 状態を更新
            state.add_search_results(search_results)
            state.current_node = "retrieve"

            logger.info(f"RetrieveNode: {len(search_results)} 件のドキュメントを取得")

            return {
                "search_results": state.search_results,
                "search_count": state.search_count,
                "current_node": state.current_node,
            }

        except Exception as e:
            logger.error(f"RetrieveNode: 検索エラー - {str(e)}")
            return {"error_message": f"検索エラー: {str(e)}", "current_node": "error"}

    async def search_with_multiple_queries(
        self, queries: List[str]
    ) -> List[SearchResult]:
        """
        複数のクエリで並列検索を実行（将来の拡張用）.

        Args:
            queries: 検索クエリのリスト

        Returns:
            統合された検索結果
        """
        tasks = []
        for query in queries:
            task = self._search.search_documents(query=query, top=self._top_k)
            tasks.append(task)

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        all_results = []
        for response in responses:
            if isinstance(response, Exception):
                logger.warning(f"並列検索でエラー: {response}")
                continue

            if not isinstance(response, dict):
                logger.warning(f"予期しないレスポンス型: {type(response)}")
                continue

            for doc in response.get("documents", []):
                search_result = SearchResult(
                    content=doc.get("content", ""),
                    source=doc.get("source", "unknown"),
                    score=doc.get("@search.score", 0.0),
                    metadata={
                        "title": doc.get("title", ""),
                        "url": doc.get("url", ""),
                        "chunk_id": doc.get("chunk_id", ""),
                    },
                )
                all_results.append(search_result)

        return all_results

    # --------------------------------------------------
    # internal helpers
    # --------------------------------------------------
    def _build_query(self, state: AgentState) -> str:
        """Generate search query string based on current cycle."""
        if state.cycle_count == 0:
            return state.question
        return f"{state.question} 詳細 {state.cycle_count}"
