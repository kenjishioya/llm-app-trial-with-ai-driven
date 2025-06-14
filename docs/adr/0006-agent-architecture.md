# 0006 – Deep Research Agent にLangGraph Agentic RAG設計採用

*Status*: **Accepted** (Revised)
*Date*: 2025-06-12 (Updated)

## 背景

* 単純なRAG応答では満足できない複雑な質問（競合分析、市場調査など）に対応したい。
* ユーザーが「Deep Research」ボタンを押した場合は、多段階の調査プロセスを自動実行する。
* LLM自身にリサーチ計画を立てさせ、検索→要約→さらに検索のループで深掘りしたい。
* **LangGraphチュートリアルが示すAgentic RAG**：状態マシンでRetrieve ↔ Decide ↔ Answerを循環させる設計を採用したい。
* 余計なベクトル検索を省きコスト最適化を実現したい。

## 決定

* **LangGraph Agentic RAG設計**を採用。

  1. **RetrieveNode**: Azure AI Searchで関連ドキュメントを検索・収集。
  2. **DecideNode**: 検索結果の十分性を判定し、追加検索要否を決定。
  3. **AnswerNode**: 収集した情報から構造化レポートを生成。
  4. **状態循環**: Retrieve → Decide → (必要に応じてRetrieve) → Answer

## 根拠・代替案

| 代替                        | 理由                     | 採用/却下理由                                        |
| ------------------------- | ---------------------- | ------------------------------------------- |
| **LangGraph DAG** ✅         | グラフベース、分岐・並列処理に強い    | **採用**: 状態管理が明確、デバッグ可能、コスト最適化に優れる                |
| **ループベース設計**    | 実装がシンプル            | 却下: 状態管理が複雑、無駄な検索が発生しやすい       |
| **Single-shot プロンプト**    | 実装が最もシンプル            | 却下: 長文生成で品質低下、引用管理が困難、トークン制限に引っかかりやすい       |
| **Agent Framework (AutoGEN)** | 複数エージェント対話で高品質     | 却下: 依存関係が重い、Azure OpenAI との統合が複雑、無料枠でのコスト心配 |

LangGraph設計は**状態遷移が明確**で、各ノードの実行結果を確認でき、問題箇所の特定が容易。
**コスト最適化**：DecideNodeで検索結果十分性を判定し、不要な検索を回避。

## 影響範囲

* **コンポーネント**: `DeepResearchLangGraphAgent` クラスを新規作成。
* **依存関係**: `langgraph`, `langchain-core`, `langchain-community` 追加。
* **データモデル**: `research_notes` テーブルで各ノード実行結果を保存。
* **UI**: 進行状況表示（"Retrieving... → Deciding... → Answering..."）。
* **パフォーマンス**: 最大3回のRetrieve-Decide循環で120秒以内の目標達成。

## フォローアップ

* LangGraphノードの並列実行可能性を検証（複数検索クエリの同時実行）。
* DecideNodeの判定ロジック最適化（検索結果十分性の閾値調整）。
* 高品質なレポート生成のためのAnswerNodeプロンプトエンジニアリング。
