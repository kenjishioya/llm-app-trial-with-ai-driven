"""DecideNode for LangGraph Deep Research workflow."""

from typing import Dict, Any
import logging

from .state import AgentState, get_high_relevance_docs

logger = logging.getLogger(__name__)


class DecideNode:
    """検索結果の十分性を判定し、次のアクションを決定するノード."""

    def __init__(self, relevance_threshold: float = 0.7, min_documents: int = 5):
        self.relevance_threshold = relevance_threshold
        self.min_documents = min_documents

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """
        検索結果を評価し、十分かどうかを判定する.

        Args:
            state: 現在のエージェント状態

        Returns:
            判定結果を含む状態の辞書
        """
        logger.info("DecideNode: 検索結果の十分性を判定中")

        # 高関連度のドキュメントを取得
        high_relevance_docs = get_high_relevance_docs(state)
        total_docs = len(state["search_results"])
        high_relevance_count = len(high_relevance_docs)

        logger.info(
            f"DecideNode: 総ドキュメント数={total_docs}, 高関連度={high_relevance_count}"
        )

        # 判定ロジック
        is_sufficient = self._evaluate_sufficiency(state, high_relevance_docs)

        # 次のノードを決定
        if is_sufficient:
            next_node = "answer"
            logger.info("DecideNode: 十分な情報が得られました → Answer へ")
        elif state["search_count"] >= state["max_searches"]:
            next_node = "answer"  # 最大検索回数に達した場合も Answer へ
            logger.info("DecideNode: 最大検索回数に達しました → Answer へ")
        else:
            next_node = "retrieve"
            logger.info("DecideNode: 追加検索が必要です → Retrieve へ")

        return {
            **state,
            "is_sufficient": is_sufficient,
            "current_node": "decide",
            "next_node": next_node,
        }

    def _evaluate_sufficiency(
        self, state: AgentState, high_relevance_docs: list
    ) -> bool:
        """
        検索結果の十分性を評価する.

        Args:
            state: エージェント状態
            high_relevance_docs: 高関連度ドキュメントのリスト

        Returns:
            十分かどうかのブール値
        """
        # 基本的な数量チェック
        if len(high_relevance_docs) < self.min_documents:
            logger.debug(
                f"高関連度ドキュメント不足: {len(high_relevance_docs)} < {self.min_documents}"
            )
            return False

        # 内容の多様性チェック（異なるソースからの情報）
        unique_sources = set(doc.source for doc in high_relevance_docs)
        if len(unique_sources) < 3:  # 最低3つの異なるソース
            logger.debug(f"ソースの多様性不足: {len(unique_sources)} < 3")
            return False

        # 平均スコアチェック
        avg_score = sum(doc.score for doc in high_relevance_docs) / len(
            high_relevance_docs
        )
        if avg_score < self.relevance_threshold + 0.1:  # 閾値より少し高いスコアを要求
            logger.debug(
                f"平均スコア不足: {avg_score:.3f} < {self.relevance_threshold + 0.1}"
            )
            return False

        # 総文字数チェック（十分な情報量）
        total_content_length = sum(len(doc.content) for doc in high_relevance_docs)
        min_content_length = 5000  # 最低5000文字
        if total_content_length < min_content_length:
            logger.debug(
                f"コンテンツ量不足: {total_content_length} < {min_content_length}"
            )
            return False

        logger.info("DecideNode: すべての十分性条件を満たしています")
        return True

    def get_decision_summary(self, state: AgentState) -> str:
        """判定結果のサマリーを生成（デバッグ用）."""
        high_relevance_docs = get_high_relevance_docs(state)
        unique_sources = set(doc.source for doc in high_relevance_docs)
        avg_score = (
            sum(doc.score for doc in high_relevance_docs) / len(high_relevance_docs)
            if high_relevance_docs
            else 0
        )
        total_content = sum(len(doc.content) for doc in high_relevance_docs)

        return f"""判定サマリー:
- 高関連度ドキュメント: {len(high_relevance_docs)}/{self.min_documents}
- ユニークソース: {len(unique_sources)}/3
- 平均スコア: {avg_score:.3f}/{self.relevance_threshold + 0.1}
- 総コンテンツ量: {total_content}/5000文字
- 検索回数: {state["search_count"]}/{state["max_searches"]}
- 判定結果: {'十分' if state["is_sufficient"] else '不十分'}"""
