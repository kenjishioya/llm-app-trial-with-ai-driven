"""AnswerNode for LangGraph Deep Research workflow."""

from typing import Dict, Any
import logging
from datetime import datetime

from services.llm_service import LLMService
from .state import AgentState

logger = logging.getLogger(__name__)


class AnswerNode:
    """収集した情報を基にMarkdownレポートを生成するノード."""

    def __init__(self, llm_service: LLMService = None):
        self.llm_service = llm_service or LLMService()
        self.max_report_length = 8000  # 最大レポート長

    async def __call__(self, state: AgentState) -> Dict[str, Any]:
        """
        収集した情報を基にレポートを生成する.

        Args:
            state: 現在のエージェント状態

        Returns:
            生成されたレポートを含む状態の辞書
        """
        logger.info("AnswerNode: レポート生成を開始")

        try:
            # 高関連度のドキュメントを取得
            high_relevance_docs = state.get_high_relevance_docs()

            if not high_relevance_docs:
                # 高関連度ドキュメントがない場合は全ドキュメントを使用
                high_relevance_docs = state.search_results
                logger.warning("高関連度ドキュメントがないため、全検索結果を使用")

            # レポート生成用のプロンプトを構築
            report_prompt = self._build_report_prompt(
                state.question, high_relevance_docs
            )

            # LLMでレポート生成
            llm_response = await self.llm_service.generate_response(
                prompt=report_prompt,
                max_tokens=3000,
                temperature=0.3,  # 一貫性のある出力のため低めに設定
            )

            # レポートの後処理
            final_report = self._post_process_report(
                llm_response.content, high_relevance_docs
            )

            state.final_report = final_report
            state.current_node = "answer"

            logger.info(f"AnswerNode: レポート生成完了 ({len(final_report)} 文字)")

            return {"final_report": final_report, "current_node": state.current_node}

        except Exception as e:
            logger.error(f"AnswerNode: レポート生成エラー - {str(e)}")
            error_report = self._generate_error_report(state.question, str(e))
            return {
                "final_report": error_report,
                "current_node": "error",
                "error_message": str(e),
            }

    def _build_report_prompt(self, question: str, documents: list) -> str:
        """レポート生成用のプロンプトを構築."""
        # ドキュメントの内容を整理
        doc_contents = []
        for i, doc in enumerate(documents[:10], 1):  # 最大10件まで
            content = doc.content[:1000]  # 各ドキュメント最大1000文字
            source_info = f"[出典{i}: {doc.source}]"
            doc_contents.append(f"{source_info}\n{content}")

        documents_text = "\n\n---\n\n".join(doc_contents)

        prompt = f"""あなたは専門的なリサーチアナリストです。以下の質問に対して、提供された情報を基に詳細で構造化されたMarkdownレポートを作成してください。

## 質問
{question}

## 参考資料
{documents_text}

## レポート作成指示
1. **構造化**: 適切な見出し（##, ###）を使用して情報を整理
2. **客観性**: 提供された情報に基づいて事実を正確に記述
3. **引用**: 重要な情報には出典番号を明記（例：[出典1]）
4. **完全性**: 質問に対する包括的な回答を提供
5. **読みやすさ**: 箇条書きや表を適切に使用

## 出力形式
Markdownフォーマットで以下の構造を含むレポートを作成：

# [質問に関連するタイトル]

## 概要
- 主要なポイントの要約

## 詳細分析
### [関連するサブトピック1]
### [関連するサブトピック2]

## 結論
- 質問に対する明確な回答
- 重要な洞察

## 参考文献
- 使用した出典のリスト

レポートを作成してください："""

        return prompt

    def _post_process_report(self, report: str, documents: list) -> str:
        """生成されたレポートの後処理."""
        # 基本的なクリーンアップ
        report = report.strip()

        # 長すぎる場合は切り詰め
        if len(report) > self.max_report_length:
            report = (
                report[: self.max_report_length]
                + "\n\n*（レポートが長すぎるため切り詰められました）*"
            )

        # メタデータを追加
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        doc_count = len(documents)
        unique_sources = len(set(doc.source for doc in documents))

        metadata = f"""
---
**レポート生成情報**
- 生成日時: {timestamp}
- 使用ドキュメント数: {doc_count}
- ユニークソース数: {unique_sources}
---
"""

        return report + metadata

    def _generate_error_report(self, question: str, error_message: str) -> str:
        """エラー時のフォールバックレポート."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return f"""# エラーレポート

## 質問
{question}

## エラー内容
レポート生成中にエラーが発生しました：
```
{error_message}
```

## 対処方法
- 質問を簡潔にして再試行してください
- システム管理者にお問い合わせください

---
**エラー発生日時**: {timestamp}
"""

    def get_report_summary(self, report: str) -> str:
        """レポートのサマリーを生成（ログ用）."""
        lines = report.split("\n")
        word_count = len(report.split())
        heading_count = len([line for line in lines if line.startswith("#")])

        return f"レポートサマリー: {len(report)}文字, {word_count}語, {heading_count}見出し"
