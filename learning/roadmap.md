# ソースコード理解ロードマップ

## 🎯 目的
このロードマップは、当プロジェクト（バックエンド: FastAPI + Strawberry GraphQL、フロントエンド: Next.js + React）を**コードレベルまで完全に理解**することを目的とします。以下のステップを順に進めることで、画面操作からデータベース処理までのフローを俯瞰し、各レイヤの実装とライブラリの使い方をマスターできます。

---

## 0️⃣ 前提知識チェック
| 項目 | 推奨学習リソース |
|------|------------------|
| Python 3.12 / 型ヒント | Effective Python, PEP 484 |
| FastAPI 非同期開発     | FastAPI公式ドキュメント、FastAPI実践入門 |
| Strawberry GraphQL     | Strawberry Docs、GraphQL公式 |
| SQLAlchemy Async       | SQLAlchemy 2.x Docs (AsyncIO) |
| React 18 / Hooks       | React公式ドキュメント、Epic React |
| Next.js App Router     | Next.js Docs (v13+) |
| React Testing Library  | Testing Library Docs |
| Vitest / Pytest        | Vitest & Pytest公式 |

> 上記の基礎が不足している場合は、先にキャッチアップすることで学習効率が向上します。

---

## 1️⃣ リポジトリ全体構成を俯瞰する

```bash
├── backend               # FastAPI + Strawberry GraphQL
│   ├── api               # GraphQLスキーマ & Resolver
│   ├── models            # SQLAlchemy ORMモデル
│   ├── services          # ビジネスロジック層
│   └── tests             # Pytest
├── frontend              # Next.js (App Router)
│   ├── src               # Reactコンポーネント & Hooks
│   ├── tests             # Vitest + RTL
│   └── vitest.config.ts  # テスト設定
└── docker-compose.yml    # 開発用サービス定義
```

*タスク*
1. `tree -L 2` でディレクトリを確認。
2. `README.md` / `docs/` を読み、開発ルールとCIフローを把握。

---

## 2️⃣ フロントエンド理解ステップ

| ステップ | ゴール | 参照ファイル | 主要ライブラリ | 学習ポイント |
|-----------|--------|--------------|----------------|--------------|
| 2-1 | Next.js エントリポイントを把握 | `src/app/layout.tsx` | Next.js App Router | グローバルレイアウト, metadata |
| 2-2 | UI コンポーネント階層を理解 | `src/components/**` | React 18 | props flow, hooks |
| 2-3 | 状態管理 & データ取得 | `hooks/useChatStream.ts`, `useDeepResearch.ts` | Apollo Client, React Context | GraphQL query/mutation, subscription |
| 2-4 | ルーティングとページ遷移 | `src/app/(app)/page.tsx` | Next.js | dynamic route, metadata |
| 2-5 | テスト戦略を把握 | `frontend/tests/**` | Vitest, RTL | `vi.mock`, `render`, coverage |

*チェックリスト*
- [ ] ChatWindow → InputForm → useChatStream のデータフローを追う。
- [ ] Sidebar のセッション選択が Apollo Cache と同期する仕組みを確認。
- [ ] DeepResearch ボタン操作 → `useDeepResearch` Hook → GraphQL Mutation → 進捗表示 の流れを読解。

---

## 3️⃣ バックエンド理解ステップ

| ステップ | ゴール | 参照ファイル | 主要ライブラリ | 学習ポイント |
|-----------|--------|--------------|----------------|--------------|
| 3-1 | FastAPI アプリ生成箇所を把握 | `backend/main.py` | FastAPI | ミドルウェア, CORS |
| 3-2 | GraphQL スキーマ & Resolver | `api/graphql_schema.py`, `api/resolvers/*` | Strawberry | `@strawberry.type`, `@strawberry.mutation` |
| 3-3 | サービス層の責務 | `services/session_service.py`, `services/rag_service.py` | SQLAlchemy Async | トランザクション管理, `async for db in get_db()` パターン |
| 3-4 | モデル定義 | `models/*.py` | SQLAlchemy 2.x | 型、リレーション、`Mapped` |
| 3-5 | テスト戦略 | `backend/tests/**` | Pytest, Async fixtures | Test DB, mock, coverage |

*チェックリスト*
- [ ] Mutation `ask` → RAGService → OpenAI 呼び出しフローを追う。
- [ ] Subscription `deepResearchStream` が AsyncGenerator で実装されているか確認。
- [ ] SessionService の update/create/delete シリーズで DB 操作とエラーハンドリングを把握。

---

## 4️⃣ フロント ↔ バックエンド連携をトレース
1. **画面操作シナリオ**: ChatWindow で「質問」を送信
   1. InputForm `onSubmit` → `useChatStream.ask()` (GraphQL mutation `ask`)
   2. Apollo Client が `/graphql` に POST
   3. Mutation `ask` → `RAGService.ask_question` → OpenAI
   4. 返却 `AskPayload` の `stream` URL を `useChatStream` が受信し SSE 購読
   5. Subscription からチャンク受信 → MessageList 更新 → UI 再レンダリング

2. **Deep Research シナリオ**: Sidebar で「Deep Research」を開始
   1. `useDeepResearch.start()` → GraphQL mutation `deepResearch`
   2. Mutation 内でタスク登録 → `DeepResearchPayload` 帰却
   3. `/graphql/stream` SSE で進捗更新

---

## 5️⃣ 推奨学習プラン (2 週間例)
| Day | 学習テーマ | 目標 |
|-----|-----------|------|
| 1-2 | リポジトリ構成 / README | 全体像把握 |
| 3-4 | フロントエンド UI コンポーネント | ChatWindow, Sidebar 深掘り |
| 5-6 | Apollo Client & GraphQL Hook | useChatStream, useDeepResearch |
| 7   | フロントエンドテスト | Vitest／RTL 実践 |
| 8-9 | FastAPI & Strawberry 基礎 | スキーマとResolver読解 |
| 10  | Service層とDBモデル | SessionService, models/*.py |
| 11  | バックエンドテスト | Pytest, Async fixtures |
| 12  | エンドツーエンド確認 | 画面操作→DBまでトレース |
| 13  | パフォーマンス / キャッシュ | RagService, DataLoader 等 |
| 14  | まとめ & ドキュメント更新 | 追加メモ・ADR作成 |

---

## 6️⃣ 追加リソース
- **ADR**: `docs/adr/` 内のアーキテクチャ決定記録を確認
- **Code Style Guides**: `docs/contributing.md`, `docs/architecture/**`
- **CI Config**: `.github/workflows/` ; pre-commit, coverage gate

---

### 📌 メモ
- フロントエンドは **TypeScript strict**、バックエンドは **Python 3.12 + Typing** が前提です。
- モック・スタブより **インメモリテストDB** を重視する設計です。

学習を進めながら **疑問点や改善点は Issue/Pull Request** として残すことで、ドキュメントが進化していきます。頑張ってください！
