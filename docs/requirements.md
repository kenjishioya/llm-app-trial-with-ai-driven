# 要件定義書 (MVP)

> **ドキュメント目的** — 「llm-app-trial-with-ai-driven」MVP で実装・検証すべき最小限の機能および品質を明文化し、開発チームとステークホルダー間で共通認識を持つ。

---

## 1. 用語定義

| 略語/用語                 | 説明                                                              |
| --------------------- | --------------------------------------------------------------- |
| **RAG**               | Retrieval‑Augmented Generation。検索結果を LLM プロンプトに組み込み回答精度を高めるパターン |
| **Deep Research モード** | Retrieve→Decide→Answer のLangGraph Agentic RAGフロー                    |
| **セッション**             | 1 ユーザーとのチャット対話を表す単位。Deep Research 実行履歴も含む                       |
| **無料枠 (Free Tier)**   | Azure 無料プランで課金が発生しない SKU / 使用量                                  |

---

## 2. 機能要件 (Functional Requirements)

| ID        | 分類                | 要件                                                                 | 受け入れ基準                                                             |
| --------- | ----------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------ |
| **FR-01** | チャット & Q\&A (RAG) | ユーザーはブラウザ UI で自然文の質問を送信できる                                         | Next.js 14 UI の入力欄にテキストを送信し、API 呼び出しが行われることを確認                     |
| **FR-02** | チャット & Q\&A (RAG) | バックエンドは Azure AI Search で上位 *k* 件 (既定 3) のドキュメントを取得し GPT‑4o へ渡す    | FastAPI ログに `search_top_k=3` が出力され、検索結果がプロンプトに含まれていることをユニットテストで検証  |
| **FR-03** | チャット & Q\&A (RAG) | GPT‑4o から生成した回答を引用付きで返却する                                          | レスポンス JSON に `citations` フィールドが含まれ、UI が脚注リンクを表示                    |
| **FR-04** | チャット & Q\&A (RAG) | 応答はストリーミングで逐次フロントへ送信される                                            | SSE / WebSocket でチャンクが送られ、入力後 1 秒以内に最初のトークンが到着                     |
| **FR-05** | Deep Research モード | チャット UI で **「Deep Research」ボタン／アイコン** を押すと Deep Research モードが有効になる | ボタン押下後、UI が "Researching…" 状態に変わり、バックエンド側で Retrieve→Decide→Answer循環が開始   |
| **FR-06** | Deep Research モード | Deep Research モードでは検索・要約を繰り返し、最終レポートを構造化 (章立て) で生成する               | レポートが Markdown もしくは HTML セクション構造で返却されることを E2E テストで確認               |
| **FR-07** | Deep Research モード | フロントは Deep Research の進捗タイムライン (例: Step 1/3) を表示する                  | UI にステップ数と現在処理中サブタスクがリアルタイムに表示                                     |
| **FR-08** | セッション管理           | すべてのメッセージ・引用・Deep Research ノートは DB に保存される                          | Cosmos DB の `sessions` / `messages` / `research_notes` テーブルにレコード挿入 |
| **FR-09** | セッション管理           | ユーザーは過去セッションを一覧し再読できる                                              | UI 左ペインにセッション履歴リスト、クリックでチャットが再表示                                   |
| **FR-10** | 管理 CLI            | 管理 CLI `python scripts/index_docs.py <dir>` で社内ドキュメントを一括インデックス化    | 実行後に AI Search のインデックス件数が増えることを確認                                  |

## 3. 非機能要件 (Non-Functional Requirements). 非機能要件 (Non‑Functional Requirements)

| カテゴリ        | ID     | 要件                              | 受け入れ基準                      |
| ----------- | ------ | ------------------------------- | --------------------------- |
| **パフォーマンス** | NFR‑01 | RAG 応答は 10 秒以内 (95 パーセンタイル)     | JMeter 測定 p95 < 10s         |
|             | NFR‑02 | Deep Research 完了は 120 秒以内       | p95 < 120s                  |
| **信頼性**     | NFR‑03 | 主要ワークフロー E2E テストパス率 100%        | GitHub Actions CI で成功       |
| **セキュリティ**  | NFR‑04 | 秘匿情報を Git にコミットしない              | pre‑commit フックで検出 ⇒ CI fail |
| **運用性**     | NFR‑05 | `docker compose up` 1 コマンドで環境構築 | README 手順通り実行で成功            |
| **コスト**     | NFR‑06 | Free Tier リソースのみ IaC で作成        | `terraform plan` に課金 SKU 無し |

---

## 4. MVP 完了の定義 (Definition of Done)

* 上記 FR‑01〜FR‑10 と NFR‑01〜NFR‑06 が全て ✅ 済み
* README に起動 → 動作確認 → 終了手順が記載されている
* GitHub Actions で `main` ブランチ Push 時にユニット + E2E テストが自動実行され成功

---

## 5. 範囲外 (Out of Scope)

* SSO / 多要素認証
* 本番環境 (課金リソース) へのデプロイ
* SLA/監視/アラート設定
* 多言語サポート (UI・回答は日本語のみ)

---

*このドキュメントは MVP 期間中に随時アップデートされる予定です。*
