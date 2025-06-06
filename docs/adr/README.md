# ADR ポータル – Architecture Decision Records

**ADR (Architecture Decision Record)** は「なぜその技術／構成を選んだか」を 1 決定 = 1 Markdown で残す軽量ドキュメントです。ここでは QRAI プロジェクト内の ADR を一覧し、追跡できるようにします。

---

## 1. ADR 一覧

| ID   | タイトル                                   | ステータス   | 作成日     | 備考                             |
| ---- | ------------------------------------------ | ------------ | ---------- | -------------------------------- |
| 0001 | `use-rag` – 質問応答に RAG パターンを採用          | **Accepted** | 2025-06-03 | GPT だけでは引用付与が難しいため |
| 0002 | `free-tier-only` – Dev 環境は Azure 無料枠限定 | **Accepted** | 2025-06-03 | コスト抑制と学習目的             |
| 0003 | `use-graphql` – API を GraphQL に統一       | **Accepted** | 2025-06-03 | オーバーフェッチ回避と型安全     |
| 0004 | `use-cosmos-postgresql` – Cosmos DB for PostgreSQL 採用 | **Accepted** | 2025-06-03 | 無料枠でリレーショナル機能が必要 |
| 0005 | `streaming-approach` – ストリーミングに SSE 採用 | **Accepted** | 2025-06-03 | WebSocket より軽量で GraphQL 統合しやすい |
| 0006 | `agent-architecture` – Deep Research Agent にループベース設計 | **Accepted** | 2025-06-03 | 複雑すぎず実装・デバッグが容易 |

> **ステータス**: `Proposed` / `Accepted` / `Superseded` / `Deprecated` のいずれか。

---

## 2. ADR の書き方（テンプレート）

ファイル名: `docs/adr/NNNN-title.md` （NNNN = 4 桁連番）。

```markdown
# NNNN – 短いタイトル

*Status*: Proposed / Accepted / Superseded / Deprecated
*Date*: YYYY‑MM‑DD

## 背景
- なぜこの決定が必要か。

## 決定
- 採用するオプションと理由。

## 根拠 / 代替案
- 比較した他案と却下理由。

## 影響範囲
- コード / インフラ / ドキュメントへの影響。

## フォローアップ
- 将来見直す条件、TODO など。
```

### 手順

1. `NNNN-title.md` を作成しテンプレートを記入。
2. Pull Request でチームレビュー ➜ マージで **Status を Accepted** に更新。
3. 変更があれば既存 ADR を *Superseded* にし、新しい ADR を追加。

---

## 3. 参考

* [Michael Nygard – Documenting Architecture Decisions](https://c4model.com/#adr)（原典）
* ThoughtWorks Tech Radar「ADR の推奨」

---

*Last updated: 2025‑06‑03*
