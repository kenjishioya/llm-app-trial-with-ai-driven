# Contributing Guide – QRAI

> **ようこそ！** このリポジトリへのコントリビュート方法をまとめています。初めてでも PR をスムーズに出せるよう、セットアップからレビューまでの流れを網羅しました。

---

## 👋 新規開発者の方へ

初回セットアップとプロジェクト概要は **[developer_onboarding.md](developer_onboarding.md)** を参照してください。技術分野別のガイドと15分以内での初回コントリビュートまでの手順を提供しています。

このドキュメントは、すでにオンボーディングを完了した開発者向けのコントリビューション詳細ガイドです。

---

## 1. 開発環境セットアップ

詳細な環境変数設定、Azure リソース設定、CI/CD設定については **[environment_setup.md](environment_setup.md)** を参照してください。

基本セットアップ：

```bash
# クローン
git clone https://github.com/yourname/llm-app-trial-with-ai-driven.git
cd llm-app-trial-with-ai-driven

# Dev コンテナ (VS Code) 推奨
# もしくはローカル
make dev-setup   # lint/commit hooks 自動セット
```

### pre-commit フック

`pre-commit install` 済み。コミット前に以下が自動実行されます:

* **Black** / **isort** / **ruff**（Python）
* **Prettier** / **ESLint**（TypeScript）
* **markdownlint**
* **detect-secrets** – 秘密情報誤コミット防止

---

## 2. ブランチ戦略

| ブランチ       | 用途            | 保護設定                        |
| ---------- | ------------- | --------------------------- |
| `main`     | リリースタグ & デモ環境 | 強制 PR、CI 必須、管理者でも直接 push 不可 |
| `feature/*` | 機能開発          | 任意作成、PR で `main` にマージ       |
| `docs/*`   | ドキュメントのみ      | CI: lint + spellcheck       |
| `hotfix/*` | 本番障害修正        | main 直 PR、レビュー 2 名          |

> **TL;DR** — `git switch -c feature/your-feature` で開発 → PR to `main` → GitHub Actions green → レビューOK → squash merge。

---

## 3. コミット規約 (Conventional Commits)

```
<type>(scope): <subject>

<body>

<footer>
```

| type         | 用途         |
| ------------ | ---------- |
| **feat**     | 新機能        |
| **fix**      | バグ修正       |
| **docs**     | ドキュメントのみ   |
| **refactor** | 内部リファクタリング |
| **chore**    | ビルド・依存更新   |
| **ci**       | CI/CD 設定   |

例:

```
feat(api): add streaming SSE for RAG answers
```

コミットは **1 つの目的に絞る** こと！

---

## 4. Pull Request テンプレ

* **概要**: 何を・なぜ変更したか（Issue link）
* **スクリーンショット / 動画**（UI 変更時）
* **テスト**: `pytest` 追加 or UI Storybook 追加
* **TODO**: レビュワーに聞きたい点

自動チェック

1. `pnpm test` & `cd backend && pytest -q`
2. `prettier --check`, `ruff --fix-diff`
3. `terraform plan -detailed-exitcode`
4. `az deployment what-if` (Bicep)

全て緑でマージ可能。

---

## 5. コードスタイル概要

### Backend (Python)

* FastAPI + Strawberry GraphQL
* **PEP‑8 + Ruff**
* async/await, `httpx.AsyncClient`

### Frontend (TypeScript)

* Next.js 14 App Router + SWR
* **ESLint AirBnB + Prettier**
* Tailwind CSS (utility-first)

---

## 6. Issue ラベル

| ラベル                | 意味     |
| ------------------ | ------ |
| `good first issue` | 初心者向け  |
| `help wanted`      | ヘルプ募集  |
| `bug`              | 不具合    |
| `enhancement`      | 改善     |
| `infra`            | IaC 関連 |

---

## 7. FAQ

**Q. Windows で動きません** → WSL2 + Docker Desktop 使用を推奨。詳細は [developer_onboarding.md#前提ツールインストール](developer_onboarding.md#前提ツールインストール) を参照。

**Q. OpenAI のキーは？** → `secrets.GPT_KEY` を個人 fork に設定し CI で注入。環境変数の詳細管理は [environment_setup.md](environment_setup.md) を参照。

---

### 5. テスト追加時のガイドライン

詳細なテスト戦略・実装ガイドは **[architecture/test_strategy.md](architecture/test_strategy.md)** を参照してください。

PR 作成時の最小要件：
- **Python**: 新規機能には `pytest` テスト追加、カバレッジ 80% 以上維持
- **TypeScript**: UI コンポーネントには Vitest + Testing Library テスト追加
- **統合テスト**: 外部 API 連携機能には integration test 追加

### 6. Pull Request チェックリスト

PR 作成前に以下を確認してください：

1. `pnpm test` & `cd backend && pytest -q`
2. `pre-commit run --all-files`
3. コンフリクト解消済み

---

Happy coding! 🎉

*Last updated: 2025-06-03*

## PR 作成フロー

1. ブランチ作成: `git checkout -b feature/your-feature`
2. 実装: 機能追加、修正、テスト追加
3. テスト: `pnpm test` & `cd backend && pytest -q`
4. Lint: `pnpm lint` & `ruff check --fix`
5. コミット: `git commit -m "type(scope): short description"`
6. プッシュ: `git push origin feature/your-feature`
7. GitHub で PR 作成 → レビュー → マージ

---

## 技術別ガイドライン

### Python (Backend)
- **Python**: 新規機能には `pytest` テスト追加、カバレッジ 80% 以上維持
- **FastAPI**: OpenAPI schema 自動生成、/docs 確認
- **SQLAlchemy**: migration作成時は必ず `alembic revision --autogenerate`
- **GraphQL**: Strawberry型定義、リゾルバ単体テスト

### TypeScript (Frontend)
- **Next.js**: App Routerを使用、pages は使わない
- **React**: コンポーネント設計は shadcn/ui に倣う
- **Tailwind**: カスタムCSSクラスではなくユーティリティクラス使用

---

## コミット前チェック

1. `pnpm test` & `cd backend && pytest -q`
2. `pnpm lint` & `ruff check --fix`
