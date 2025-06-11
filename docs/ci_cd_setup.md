# 🚀 Phase 1.5 CI/CD設定ガイド

## 概要

Phase 1.5本番準備のための包括的なCI/CDパイプライン設定です。

## 🏗️ CI/CDパイプライン構成

### パイプライン段階

1. **🏗️ Setup & Validation** - プロジェクト構造検証
2. **🛡️ Security Scan** - セキュリティスキャン（SAST、依存関係）
3. **🐍 Backend Quality & Testing** - バックエンド品質・テスト
4. **⚛️ Frontend Quality & Build** - フロントエンド品質・ビルド
5. **🐳 Docker Integration Test** - Docker統合テスト
6. **🚪 Quality Gate** - 品質ゲート判定

### 自動実行条件

- **Push**: `main`, `develop`, `feature/*` ブランチ
- **Pull Request**: `main`, `develop` ブランチ向け
- **除外パス**: `infra/**`, `docs/**`, `*.md`

## 🔐 GitHub Secrets設定

### 必須環境変数

リポジトリ設定 > Secrets and variables > Actions で以下を設定：

```bash
# データベース（本番環境）
DATABASE_URL=postgresql+asyncpg://user:password@hostname:5432/qrai_prod  # pragma: allowlist secret

# LLM API Keys
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxx
GOOGLE_AI_API_KEY=AIxxxxxxxxxxxxxxxxxxxxxxxxxx
AZURE_OPENAI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxx
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# Azure Search
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxx

# 環境設定
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### セキュリティベストプラクティス

- ✅ **API Keys をコードに含めない**
- ✅ **環境ごとに異なるSecrets設定**
- ✅ **定期的なキーローテーション**
- ✅ **最小権限の原則適用**

## 🧪 テスト戦略

### バックエンドテスト

```bash
# ユニットテスト（カバレッジ要求: 80%以上）
pytest tests/unit/ --cov=. --cov-report=xml

# 統合テスト（PostgreSQL使用）
pytest tests/integration/ --tb=short
```

### フロントエンドテスト

```bash
# Linting
pnpm lint

# 型チェック
pnpm type-check

# ユニットテスト
pnpm test:unit

# ビルド検証
pnpm build
```

### Docker統合テスト

```bash
# Docker Compose設定検証
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

## 🛡️ セキュリティスキャン

### 実行内容

1. **機密情報検出**: `detect-secrets`
2. **依存関係脆弱性**: `pip-audit`, `npm audit`
3. **SAST**: `bandit` (Python)
4. **コード品質**: `ruff`, `eslint`

### 許容基準

- ❌ **Critical脆弱性**: 0件必須
- ⚠️ **High脆弱性**: 要対応検討
- ✅ **Medium以下**: 許容

## 📊 品質ゲート

### 通過条件

すべてのジョブが `success` ステータスである必要があります：

- ✅ セキュリティスキャン
- ✅ バックエンド品質・テスト
- ✅ フロントエンド品質・ビルド
- ✅ Docker統合テスト

### 失敗時対応

1. **ログ確認**: GitHub Actions > Failed Job > 詳細ログ
2. **ローカル再現**: 同等コマンドをローカル実行
3. **修正・再プッシュ**: 問題修正後に再実行

## 🚀 デプロイメント自動化

### 段階的デプロイ

```mermaid
graph LR
    A[CI/CD Pass] --> B[Staging Deploy]
    B --> C[Integration Test]
    C --> D[Production Deploy]
    D --> E[Health Check]
```

### ロールバック戦略

```bash
# 直前バージョンへのロールバック
git revert HEAD
git push origin main

# 特定バージョンへのロールバック
git revert <commit-hash>
git push origin main
```

## 📈 監視・アラート

### CI/CD メトリクス

- **成功率**: 目標 95% 以上
- **実行時間**: 目標 10分以内
- **MTTR**: 目標 30分以内

### アラート設定

GitHub Actions の Workflow runs で以下を監視：

- 連続失敗: 3回以上
- 実行時間超過: 15分以上
- セキュリティスキャン失敗: 即座に通知

## 🔧 トラブルシューティング

### よくある問題

#### 1. テスト失敗

```bash
# ローカルでテスト実行
cd backend
pytest tests/ -v

# カバレッジ確認
pytest tests/ --cov=. --cov-report=html
```

#### 2. Docker ビルド失敗

```bash
# ローカルでDocker検証
docker compose -f docker-compose.test.yml build
docker compose -f docker-compose.test.yml up
```

#### 3. セキュリティスキャン失敗

```bash
# 機密情報チェック
detect-secrets scan --baseline .secrets.baseline

# 依存関係脆弱性チェック
pip-audit --desc
```

### ログ分析

```bash
# GitHub CLI でログ取得
gh run list --repo owner/repo
gh run view <run-id> --log
```

## 📋 チェックリスト

### CI/CD設定完了確認

- [ ] GitHub Actions ワークフロー作成
- [ ] Secrets 設定完了
- [ ] pre-commit hooks 設定
- [ ] テスト環境構築
- [ ] セキュリティスキャン設定
- [ ] 品質ゲート設定
- [ ] 監視・アラート設定

### デプロイ前確認

- [ ] すべてのテスト通過
- [ ] セキュリティスキャン クリア
- [ ] カバレッジ目標達成 (80%+)
- [ ] ロードテスト実行
- [ ] ロールバック手順確認

## 🎯 Phase 1.5 完了基準

- ✅ **CI/CD自動化**: GitHub Actions 完全稼働
- ✅ **品質保証**: テスト・スキャン 100% 自動化
- ✅ **セキュリティ**: SAST・依存関係チェック自動化
- ✅ **監視**: パフォーマンス・エラー監視設定
- ✅ **ドキュメント**: 運用手順完全文書化

---

## 🔗 関連リンク

- [GitHub Actions ドキュメント](https://docs.github.com/en/actions)
- [Pre-commit Hooks](https://pre-commit.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [PostgreSQL](https://www.postgresql.org/docs/)
