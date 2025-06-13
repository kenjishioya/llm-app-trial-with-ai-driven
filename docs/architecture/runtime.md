# ランタイムビュー – QRAI

> **目的** — 実行時のデータフローとコンポーネント相互作用を時系列で示し、パフォーマンス最適化やデバッグ時にどこでレイテンシが発生するかを可視化する。RAG（通常質問）と Deep Research の 2 つの主要ワークフローをそれぞれシーケンス図で定義。

---

## 1. RAG ワークフロー（通常質問）

```mermaid
sequenceDiagram
  autonumber
  participant User as 🧑 利用者 (Browser)
  participant UI as Next.js UI
  participant API as FastAPI Gateway
  participant RET as RagService
  participant SEARCH as Azure AI Search
  participant GPT as GPT-4o (Azure OpenAI)
  participant DB as Cosmos DB (PG)

  User->>UI: 入力: "〇〇について教えて"
  UI->>API: GraphQL mutation ask()
  API->>RET: ask(question)
  RET->>SEARCH: top-k search (REST)
  SEARCH-->>RET: doc snippets (k=3)
  RET->>GPT: chatCompletion(prompt+snippets)
  GPT-->>RET: streamed tokens
  RET->>API: chunks (Markdown w/ citations)
  API->>DB: INSERT messages
  API-->>UI: SSE stream
  UI-->>User: 1st token < 1s, 完了まで ~3s
```

### レイテンシ目安 (p95 開発環境)

| 区間           | 目標         | 備考                               |
| ------------ | ---------- | -------------------------------- |
| UI→API       | ≤ 100 ms   | LAN + GraphQL                    |
| AI Search    | ≤ 300 ms   | Free SKU, キャッシュ未使用時              |
| GPT-4o       | ≤ 1,500 ms | `gpt-4o-mini`, `max_tokens=1024` |
| 最初の SSE トークン | ≤ 1 s      | UX 要件 (NFR-01)                   |
| 全文ストリーム完了    | ≤ 10 s     | NFR-01 p95                       |

---

## 2. Deep Research ワークフロー

```mermaid
sequenceDiagram
  autonumber
  participant User as 🧑 利用者
  participant UI as Next.js UI
  participant API as FastAPI
  participant AG as DeepResearchLangGraphAgent
  participant RN as RetrieveNode
  participant DN as DecideNode
  participant AN as AnswerNode
  participant SEARCH as Azure AI Search
  participant DB as Cosmos DB

  User->>UI: Deep Research ボタン押下 + 質問
  UI->>API: mutation deepResearch()
  API->>AG: run(question)
  loop Retrieve-Decide循環 (最大3回)
    AG->>RN: execute(state)
    RN->>SEARCH: search(query)
    SEARCH-->>RN: documents
    RN-->>AG: state with retrieved_docs
    AG->>DB: INSERT research_notes(retrieve_step)
    AG->>API: progress("Retrieving...")
    API-->>UI: SSE progress

    AG->>DN: execute(state)
    DN->>DN: 検索結果十分性判定
    DN-->>AG: continue/stop decision
    AG->>DB: INSERT research_notes(decide_step)
    AG->>API: progress("Deciding...")
    API-->>UI: SSE progress

    alt 検索結果不十分 & cycle < MAX
      Note over AG: 次の循環へ
    else 検索結果十分 or cycle >= MAX
      break 循環終了
    end
  end
  AG->>AN: execute(state)
  AN->>AN: 構造化レポート生成
  AN-->>AG: final_report.md
  AG->>DB: INSERT messages(final)
  AG->>API: progress("Answering...")
  API-->>UI: SSE progress
  AG-->>API: stream(report.md)
  API-->>UI: SSE report
  UI-->>User: 完了 (最大 120 s)
```

### ランタイム特性

* **コスト最適化** — `DecideNode` で検索結果十分性を判定し、不要な検索を回避してトークン使用量を削減。
* **ステータス更新** — UI へは `progress` イベントを各ノード実行ごとに送信し "Retrieving... → Deciding... → Answering..." を表示。
* **キャンセル** — ユーザーが Esc／Cancel を押下すると SSE で `STOP` を送信し、LangGraph実行の `asyncio.CancelledError` をトリガして全ノード実行をキャンセル。

---

## 3. 例外フロー・障害対応

詳細なエラーハンドリング戦略については **[error_handling.md](error_handling.md)** を参照してください。

ランタイム特有の重要ポイント:
- **並列処理でのエラー**: `asyncio.gather` の例外は個別に捕捉し、部分的な結果を返却
- **キャンセル処理**: ユーザーが Esc/Cancel を押下すると SSE で `STOP` を送信し、Agent の `asyncio.CancelledError` をトリガして全 LLM 呼び出しをキャンセル

---

## 4. ランタイム計測・可視化

* **OpenTelemetry** を FastAPI / RagService / DeepResearchLangGraphAgent に組み込み、Span 名は `rag.search`, `rag.gpt`, `agent.retrieve`, `agent.decide`, `agent.answer` など。
* 開発環境では `OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4318` で Jaeger UI にタイムライン表示。
* NFR-01/02 に準拠しているか CI の E2E テスト (`pytest + locust`) で計測。

---

## 5. 将来拡張ポイント

1. **Chunk 並列要約のワーカー化** — Celery / RQ でタスクキューを分離し GPT 呼び出しを後段にオフロード。
2. **Retry Budget** — GPT / Search のリトライ上限を 1 分間窓で 5 回に制限し、無料枠爆発を防ぐ。
3. **Web 検索ツール** — `SearchTool` をインターフェイス化済みのため plug‑in で追加可能。

---

*Last updated: 2025-06-03*
