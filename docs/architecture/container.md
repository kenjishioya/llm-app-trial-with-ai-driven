# C4 Container 図 – QRAI

> **目的** — QRAI 内部をデプロイ単位で分割し、外部依存（PaaS）は灰色で区別する。内部詳細は Component 図以降へ委譲。

---

## 1. Mermaid 図

```mermaid
%% C4Container – Internal containers + external PaaS
C4Container
  title QRAI – Container Diagram

  %% Actors
  Person(employee, "社員 / 利用者")
  Person(admin, "管理者")

  %% Boundary: QRAI internal
  System_Boundary(qrai, "QRAI Application") {
    Container(frontend, "Next.js 14 UI", "React / TypeScript", "チャット UI・セッション一覧")
    Container(api, "FastAPI Gateway", "Python / ASGI", "GraphQL API、RAG・Deep Research 制御")
    Container(rag_service, "RagService", "Python Module", "検索 + GPT 回答生成 (引用付き)")
    Container(agent_service, "DeepResearchLangGraphAgent", "LangGraph StateGraph", "Agentic RAG (Retrieve→Decide→Answer)")
    ContainerDb(db, "Cosmos DB for PostgreSQL", "Managed DB", "セッション・メッセージ格納")
  }

  %% External PaaS (grey)
  Container_Ext(search_ext, "Azure AI Search", "Search Svc", "全文・ベクトル検索")
  Container_Ext(openai_ext, "Azure OpenAI GPT‑4o", "LLM Svc", "生成・要約・埋め込み API")

  %% Relationships
  Rel(employee, frontend, "ブラウザで質問 / レポート閲覧")
  Rel(frontend, api, "GraphQL over HTTPS")
  Rel(api, rag_service, "関数呼び出し")
  Rel(api, agent_service, "関数呼び出し")
  Rel(rag_service, search_ext, "Top‑k 検索 (REST)")
  Rel(rag_service, openai_ext, "GPT Completion")
  Rel(agent_service, search_ext, "反復検索")
  Rel(agent_service, openai_ext, "Plan / Summarize / Write")
  Rel(api, db, "SQLAlchemy")
  Rel(admin, db, "SQL Console / Backup")
  Rel(admin, search_ext, "Portal 設定")
  Rel(admin, api, "Indexer CLI 実行")
```

---

## 2. コンテナ説明

| 種別           | コンテナ              | スタック            | 主な責務                  |
| ------------ | ----------------- | --------------- | --------------------- |
| **Internal** | Next.js UI        | React 18, SWR   | チャット入力・ストリーミング・履歴閲覧   |
|              | FastAPI Gateway   | FastAPI+GraphQL | 認証、RAG・DR モジュール呼び出し   |
|              | RagService        | Python          | AI Search & GPT で回答生成 |
|              | DeepResearchLangGraphAgent | LangGraph StateGraph | Retrieve / Decide / Answer ノード  |
|              | Cosmos DB (PG)    | PaaS            | 永続化                   |
| **External** | Azure AI Search   | PaaS            | 文書検索 API              |
|              | Azure OpenAI      | PaaS            | 生成・要約・埋め込み            |

---

## 3. 開発と運用視点

* **内外分離** — PaaS を `Container_Ext` として灰色表示し、責務と管理範囲を明確化。
* **スケールパス** — RagService / AgentService は将来独立コンテナへ分離し易い構成。
* **コスト管理** — 外部 PaaS への呼び出し回数を RagService で一元制御。

---

*Last updated: 2025‑06‑03*
