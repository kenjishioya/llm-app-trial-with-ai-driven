# 🚀 Phase 4 – LangGraph Deep Research 開発計画
**ブランチ**: `feature/phase-4-langgraph-deep-research`

## 📋 Phase 4 概要

**目標**: LangGraph Agentic RAG (Retrieve → Decide → Answer) を用いた Deep Research 機能を実装し、120 秒以内で構造化レポートを生成できることを確認する。

**完了条件**:
- `deepResearch(sessionId, question)` Mutation が成功し、LangGraph でレポートが生成されること ✅
- Retrieve → Decide → (Retrieve) → Answer の状態遷移が最大 3 回で完了すること ✅
- research_notes テーブルに各ノード実行結果が保存されること ✅
- SSE で "Retrieving → Deciding → Answering" が UI にストリーミングされること ✅
- `pytest`: 100% Pass (新規 30+ テスト含む) / カバレッジ 75% 以上 🔄 **保留**
- 手動統合テスト: 競合分析レポート生成が 120 秒以内で完了し Markdown が返ること ✅

---

## 🎯 詳細タスク分解

### Phase 4-1A: 依存関係 & 環境セットアップ ✅
**優先度**: 🔴 最高 **完了**: 2025-01-12

| ID | Task | 完了条件 | 所要時間 | コミット | 状態 |
| --- | ---- | -------- | -------- | -------- | ---- |
| 4-1A-1 | `langgraph`, `langchain-core`, `langchain-community` を `requirements.txt` に追加 | `pip install -r requirements.txt` 成功 | 10m | `feat(backend): add langgraph dependencies` | ✅ |

> `backend` は `requirements.txt` ベースの管理のため `pyproject.toml` タスクは不要。型チェックは既存 `mypy.ini` を利用する。

### Phase 4-1B: LangGraph 基盤コード生成 ✅
**優先度**: 🔴 最高 **完了**: 2025-01-12

| ID | Task | 完了条件 | 所要時間 | 状態 |
| --- | ---- | -------- | -------- | ---- |
| 4-1B-1 | `backend/services/deep_research/state.py`: `AgentState` dataclass 実装 | 型安全・テスト通過 | 20m | ✅ |
| 4-1B-2 | `backend/services/deep_research/retrieve_node.py`: `RetrieveNode` 実装 (Azure AI Search) | Top-k 検索・doc 格納 | 30m | ✅ |
| 4-1B-3 | `backend/services/deep_research/decide_node.py`: `DecideNode` 実装 | relevance ≥0.7 & docs≥5 判定 | 25m | ✅ |
| 4-1B-4 | `backend/services/deep_research/answer_node.py`: `AnswerNode` 実装 (GPT レポート生成) | Markdown レポート返却 | 30m | ✅ |
| 4-1B-5 | `backend/services/deep_research/agent.py`: `DeepResearchLangGraphAgent` クラス実装 | `run()` が AsyncIterator[str] を返す | 25m | ✅ |

### Phase 4-1C: Progress API & DB 連携 ✅
**優先度**: 🟡 高 **完了**: 2025-01-12

| ID | Task | 完了条件 | 所要時間 | 状態 |
| --- | ---- | -------- | -------- | ---- |
| 4-1C-1 | `backend/api/resolvers/mutation.py` に `deepResearch` 追加 | GraphQL スキーマ更新 & CodeGen OK | 20m | ✅ |
| 4-1C-2 | SSE 進捗 `backend/api/resolvers/subscription.py` 更新 | progress イベントで node 名送信 | 15m | ✅ |

### Phase 4-1D: UI 統合 ✅
**優先度**: 🟡 高 **完了**: 2025-01-13

| ID | Task | 完了条件 | 所要時間 | 状態 |
| --- | ---- | -------- | -------- | ---- |
| 4-1D-1 | フロント `DeepResearchIcon` 追加 | /chat でアイコンボタン表示 | 10m | ✅ |
| 4-1D-2 | `useDeepResearch` フック実装 | mutation & SSE progress 受信 | 25m | ✅ |
| 4-1D-3 | `ProgressBar` コンポーネント実装 | 状態 "Retrieving → Deciding → Answering" 表示 | 20m | ✅ |
| 4-1D-4 | レポート表示統合 | Markdown レンダリング & チャット内表示 | 30m | ✅ |

**実装完了項目**:
- ✅ InputForm に Deep Research アイコン（🔍）追加
- ✅ useDeepResearch フック: GraphQL mutation/subscription 統合
- ✅ ProgressBar コンポーネント: ノード状態表示（retrieve→decide→answer）
- ✅ ChatWindow: Deep Research 機能統合とプログレス表示
- ✅ Python 3.12.4 + Pydantic 2.8.0 互換性問題解決
- ✅ LangGraph 新バージョン対応（State → TypedDict）
- ✅ GraphQL CodeGen 成功、型定義更新完了
- ✅ WebSocket サブスクリプション統合（HTTP → WS 切り替え）
- ✅ 進捗バー表示ロジック修正（10% 停止問題解決）

### Phase 4-1E: テスト実装 🔄 **保留**
**優先度**: 🟢 中 **状態**: 保留中（次フェーズで実装予定）

| ID | Task | 完了条件 | カバレッジ | 所要 | 状態 |
| --- | ---- | -------- | -------- | ---- | ---- |
| 4-1E-1 | Node 単体テスト (Retrieve/Decide/Answer) | pytest green | +10% | 30m | 🔄 保留 |
| 4-1E-2 | Graph 実行テスト (StateGraph) | p95 < 120s, 正常遷移確認 | +5% | 25m | 🔄 保留 |
| 4-1E-3 | GraphQL mutation テスト | deepResearch → SSE stream 受信 | +5% | 20m | 🔄 保留 |
| 4-1E-4 | フロントフック・UI テスト | ProgressBar 表示・ボタン動作 | +5% | 30m | 🔄 保留 |

### Phase 4-1F: パフォーマンス & ドキュメント 🔄 **保留**
**優先度**: 🟢 中 **状態**: 保留中（次フェーズで実装予定）

| ID | Task | 完了条件 | 所要 | 状態 |
| --- | ---- | -------- | ---- | ---- |
| 4-1F-1 | RetrieveNode 並列検索 (`asyncio.gather`) | レイテンシ < 300 ms / node | 20m | 🔄 保留 |
| 4-1F-2 | DecideNode ロジック最適化 | 余計な検索 0 回 | 15m | 🔄 保留 |
| 4-1F-3 | ドキュメント更新 (`docs/` 各種) | ADR / component / runtime 反映 | 25m | 🔄 保留 |

---

## 🏗️ マイルストーン (4 週間想定)

| 週 | 主要マイルストーン | 目標 | 状態 |
|----|------------------|------|------|
| Week 1 | Setup + 基盤コード (4-1A, 4-1B-1〜4) | AgentState & 各 Node 実装完了 | ✅ 完了 |
| Week 2 | Graph 構築 + Progress API (4-1B-5, 4-1C) | LangGraph run() でレポート生成成功 | ✅ 完了 |
| Week 3 | UI 統合 (4-1D) | Deep Research ボタン → レポート表示動作 | ✅ 完了 |
| Week 4 | テスト & パフォーマンス (4-1E, 4-1F) | 全テスト緑、p95<120s、ドキュメント更新 | 🔄 保留 |

---

## 📊 コミット戦略

- **頻繁コミット原則**: 各タスク完了時に必ずコミットし `git status` で変更確認
- **コミットメッセージ形式**:
  ```
  <type>(scope): <summary>
  feat(agent): implement RetrieveNode
  fix(api): handle missing session id in deepResearch
  docs(runtime): update sequence diagram for LangGraph
  ```
- **CI 必須**: pre-commit フック & GitHub Actions を通過 (pytest + ruff + prettier)

---

## ✅ 完了チェックリスト (Definition of Done)

- [x] `deepResearch` GraphQL Mutation が 120 秒以内にレポート生成
- [x] Retrieve → Decide → Answer の最大 3 回循環をログで確認
- [x] research_notes に各ノード結果が保存
- [x] SSE progress が UI にリアルタイム表示
- [x] Markdown レポートに引用リンクが含まれる
- [ ] pytest 全テスト成功 (新規 30+ 含む) / カバレッジ ≥75% **（保留）**
- [ ] フロントユニットテスト成功 / カバレッジ ≥70% **（保留）**
- [ ] ドキュメント (ADR, component, runtime, roadmap) 更新済み **（保留）**

---

## 🎯 Phase 4 完了サマリー

**実装完了機能**:
- ✅ LangGraph エージェント基盤（Retrieve → Decide → Answer フロー）
- ✅ Azure AI Search 統合による文書検索
- ✅ GPT-4 による構造化レポート生成
- ✅ GraphQL Mutation/Subscription による Deep Research API
- ✅ WebSocket リアルタイム進捗表示
- ✅ React フロントエンド統合（進捗バー、レポート表示）

**保留項目**:
- 🔄 包括的テストスイート（Phase 4-1E）
- 🔄 パフォーマンス最適化（Phase 4-1F）
- 🔄 技術ドキュメント更新

**次フェーズ予定**: テスト実装とパフォーマンス最適化を別途実施

---

*作成日: 2025-06-12 / 更新日: 2025-01-13*
