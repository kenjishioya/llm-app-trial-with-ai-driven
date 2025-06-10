# API 仕様 – QRAI (MVP)

> **目的** — フロントエンド実装者・外部連携者が参照する一次情報として、GraphQL スキーマ・REST ヘルスエンドポイントをまとめる。*本ファイルはコードから自動生成されるわけではないため、インターフェイス変更時は必ず更新してください。*

---

## 1. エンドポイント一覧

| プロトコル            | URL (dev)                               | 用途                  | 認証       |
| ---------------- | --------------------------------------- | ------------------- | -------- |
| GraphQL HTTP     | `https://localhost:8000/graphql`        | クエリ・ミューテーション        | 省略可（匿名可） |
| GraphQL WS (SSE) | `https://localhost:8000/graphql/stream` | ストリーミングレスポンス        | 同上       |
| OpenAPI JSON     | `https://localhost:8000/openapi.json`   | FastAPI 自動ドキュメント    | Public   |
| Swagger UI       | `https://localhost:8000/docs`           | フォームテスト             | Public   |
| Healthcheck      | `https://localhost:8000/health`         | コンテナ Liveness Probe | Public   |

---

## 2. GraphQL Schema Snapshot (SDL)

```graphql
"質問を送信し、RAG または Deep Research 応答を受け取る"
input AskInput {
  question: String!
  deepResearch: Boolean = false
}

type AskPayload {
  sessionId: ID!
  messageId: ID!
  stream: String! # SSE endpoint: /graphql/stream?id=<messageId>
}

"過去セッションを取得"
input SessionFilter {
  userId: String
  limit: Int = 20
}

type Session {
  id: ID!
  startedAt: DateTime!
  endedAt: DateTime
  mode: String!
  messages(limit: Int = 50): [Message!]!
}

type Message {
  id: ID!
  role: String! # user | assistant | system
  content: String!
  citations: [Citation!]
  createdAt: DateTime!
}

type Citation {
  url: String!
  title: String
  snippet: String
}

type Query {
  sessions(filter: SessionFilter): [Session!]!
}

type Mutation {
  ask(input: AskInput!): AskPayload!
}
```

> **NOTE:** 詳細な型や Directive (`@stream`) は `backend/schema/schema.graphql` を参照。

---

## 3. 典型的な呼び出し例

### 3‑1 通常質問 (RAG)

```graphql
mutation AskRag {
  ask(input: {question: "社内勤怠ポリシーを教えて"}) {
    sessionId
    messageId
    stream  # => wss/SSE で返却される URL
  }
}
```

クライアントは `stream` URL へ接続し、チャンクごとに UI へ表示。

### 3‑2 Deep Research

```graphql
mutation AskDR {
  ask(input: {question: "新製品の競合分析", deepResearch: true}) {
    sessionId
    messageId
    stream
  }
}
```

ステップ完了ごとに `progress` イベントが届く。

### 3‑3 セッション履歴

```graphql
query MySessions {
  sessions(filter: {userId: "aad|123", limit: 10}) {
    id
    startedAt
    mode
    messages(limit: 1) { content }
  }
}
```

---

## 4. HTTP 契約

| エンドポイント           | メソッド      | レイテンシ目標          |
| ----------------- | --------- | ---------------- |
| `/health`         | GET       | ≤ 50 ms          |
| `/graphql`        | POST      | p95 < 10 s (RAG) |
| `/graphql/stream` | GET (SSE) | 1st byte ≤ 1 s   |

---

## 5. エラーハンドリング

包括的なエラーハンドリング戦略については **[docs/architecture/error_handling.md](architecture/error_handling.md)** を参照してください。

基本的なHTTPステータスコード:
- **400**: バリデーションエラー
- **429**: Rate Limit超過
- **500**: 内部サーバーエラー

GraphQLエラーレスポンスは [GraphQL over HTTP仕様](https://graphql.org/learn/serving-over-http/) に準拠し、`errors` 配列でエラー詳細を返却します。

---

## 6. 今後の予定 (API Roadmap)

* Webhook で回答ログを外部 BI にプッシュ (`@asyncStreaming`)
* Management API (`/admin/*`) でドキュメント再インデックスをトリガー

---

*Last updated: 2025-06-03*
