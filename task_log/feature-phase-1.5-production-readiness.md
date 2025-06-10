# Phase 1.5: 本番運用準備 実行計画

> **目的**: Phase 1 で残存した本番運用準備の課題を解決し、テスト環境分離・データベース移行・CI/CD整備・環境設定強化を実施する

## 背景・課題

Phase 1 完了時に判明した本番運用準備不足の課題：
- ❌ **テスト環境分離**: tests/test_api.py が本番DBに直接書き込み（開発用SQLiteだが問題）
- ❌ **テストデータ汚染**: テスト実行でセッションが大量作成される問題を確認
- ❌ **データベース設定**: 開発環境でもSQLite使用、本番PostgreSQL移行準備不足
- ❌ **CI/CD未整備**: GitHub Actions, pre-commit hooks未実装
- ❌ **環境変数管理**: .env管理、本番シークレット分離未対応

## 実行計画

### A. テスト環境改善 (優先度: 最高)

#### A1. テストDB完全分離
**タスク**: `backend/tests/conftest.py` 強化・テスト分離設定
```python
# 実装内容：
# - pytest.fixture で in-memory SQLite 設定
# - 各テスト後の自動データクリーンアップ
# - テスト専用 engine/session 設定
```

**ファイル**:
- `backend/tests/conftest.py` (既存ファイル強化)
- `backend/tests/test_database.py` (分離テスト確認)

#### A2. モックLLM実装
**タスク**: テスト時のLLM API呼び出し回避
```python
# 実装内容：
# - pytest-mock 使用、固定レスポンス返却
# - LLMService.ask_question() モック化
# - 実際のAPI消費回避、テスト速度向上
```

**ファイル**:
- `backend/tests/mocks/llm_mock.py` (新規作成)
- `backend/tests/test_services.py` (新規作成・モック適用)

#### A3. テストカテゴリ分離
**タスク**: unit/integration/e2e の明確化
```bash
# 実装内容：
# - backend/tests/unit/ : 純粋ユニットテスト (モック使用)
# - backend/tests/integration/ : DB連携テスト (テスト用DB)
# - tests/e2e/ : エンドツーエンドテスト
# - frontend/__tests__/ : フロントエンドテスト
```

**ディレクトリ構造**:
```
backend/tests/           # バックエンド専用テスト
├── conftest.py (既存)
├── test_api.py (既存)
├── test_providers.py (既存)
├── unit/
│   ├── test_services.py
│   └── test_models.py
├── integration/
│   ├── test_database.py
│   └── test_graphql.py
└── mocks/
    └── llm_mock.py

frontend/__tests__/      # フロントエンド専用テスト
├── components/
├── pages/
└── setup.ts

tests/e2e/              # 全体E2Eテスト
└── test_full_flow.py
```

#### A4. フィクスチャ強化
**タスク**: 自動クリーンアップ・データ準備
```python
# 実装内容：
# - @pytest.fixture(autouse=True) でDB初期化
# - テストデータ投入・削除の自動化
# - 各テスト間の完全分離保証
```

### B. データベース本番準備 (優先度: 高)

#### B1. PostgreSQL Docker統合
**タスク**: 開発環境PostgreSQL設定
```yaml
# docker-compose.yml 更新内容：
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: qrai_dev
      POSTGRES_USER: qrai_user
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

**ファイル**:
- `docker-compose.yml` (更新)
- `backend/config.py` (DATABASE_URL設定)

#### B2. Alembic本番運用設定
**タスク**: マイグレーション検証・自動化
```python
# alembic.ini 設定：
# - 環境別マイグレーション設定
# - 自動マイグレーション実行
# - ロールバック手順確認
```

**ファイル**:
- `backend/alembic.ini` (環境対応)
- `backend/migrations/env.py` (動的設定)
- `scripts/migrate.sh` (自動化スクリプト)

#### B3. 接続プール設定
**タスク**: SQLAlchemy async pool最適化
```python
# 実装内容：
# - pool_size=10, max_overflow=20 設定
# - 接続タイムアウト設定
# - ヘルスチェック機能
```

**ファイル**:
- `backend/database.py` (pool設定)
- `backend/deps.py` (接続管理)

#### B4. バックアップ戦略
**タスク**: pg_dump自動化・復旧手順
```bash
# スクリプト内容：
# - 日次バックアップ自動実行
# - Azure Blob Storage保存
# - 復旧テスト自動化
```

**ファイル**:
- `scripts/backup_database.sh` (新規作成)
- `scripts/restore_database.sh` (新規作成)
- `docs/operational_runbook.md` (手順書更新)

### C. CI/CD実装 (優先度: 高)

#### C1. GitHub Actions設定
**タスク**: 完全なCI/CDパイプライン構築
```yaml
# .github/workflows/ci.yml 内容：
name: CI/CD Pipeline
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test_password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
      - name: Run tests
        run: |
          cd backend
          python -m pytest tests/ --cov=. --cov-report=xml --cov-fail-under=80
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

**ファイル**:
- `.github/workflows/ci.yml` (新規作成)
- `backend/requirements.txt` (テスト依存関係追記)

#### C2. Pre-commit hooks設定
**タスク**: コミット前品質チェック
```yaml
# .pre-commit-config.yaml 更新：
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        args: [--line-length=88]
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-r, backend/, -f, json, -o, bandit-report.json]
  - repo: https://github.com/pyupio/safety
    rev: 2.3.5
    hooks:
      - id: safety
```

**ファイル**:
- `.pre-commit-config.yaml` (更新)
- `scripts/setup-dev.sh` (開発環境セットアップ)

#### C3. セキュリティスキャン統合
**タスク**: bandit, safety, secrets検出
```bash
# GitHub Actions セキュリティステップ：
      - name: Security scan
        run: |
          bandit -r backend/ -f json -o bandit-report.json
          safety check --json
          detect-secrets scan --all-files
```

#### C4. カバレッジ強制
**タスク**: 80%未満でCI失敗設定
```bash
# pytest設定：
cd backend && python -m pytest tests/ --cov=. --cov-report=term-missing --cov-fail-under=80
```

**ファイル**:
- `backend/pyproject.toml` (pytest設定)
- `backend/.coveragerc` (カバレッジ設定)

### D. 環境設定強化 (優先度: 中)

#### D1. .env管理改善
**タスク**: 環境別設定ファイル整備
```bash
# ファイル構成：
.env.sample          # サンプル設定
.env.development     # 開発環境
.env.test           # テスト環境
.env.production     # 本番環境 (Git管理外)
```

**内容例**:
```bash
# .env.sample
DATABASE_URL=postgresql://user:password@localhost:5432/qrai_dev  # pragma: allowlist secret
OPENROUTER_API_KEY=sk-or-xxxxxxxx
GOOGLE_AI_API_KEY=AIzaSyxxxxxxxx
AZURE_KEYVAULT_URL=https://qrai-kv-dev.vault.azure.net/
LOG_LEVEL=INFO
ENVIRONMENT=development
```

**ファイル**:
- `.env.sample` (新規作成)
- `.env.development` (新規作成)
- `.env.test` (新規作成)
- `backend/config.py` (環境別設定ロード)

#### D2. 設定検証機能
**タスク**: 起動時環境変数チェック
```python
# backend/config.py 実装：
class Settings(BaseSettings):
    database_url: str
    openrouter_api_key: str
    google_ai_api_key: str
    environment: str = "development"

    @validator('database_url')
    def validate_database_url(cls, v):
        if not v.startswith(('postgresql://', 'sqlite://')):
            raise ValueError('Invalid database URL format')
        return v

    @validator('openrouter_api_key')
    def validate_openrouter_key(cls, v):
        if not v.startswith('sk-or-'):
            raise ValueError('Invalid OpenRouter API key format')
        return v

def validate_environment():
    """起動時設定検証"""
    try:
        settings = Settings()
        logger.info("Environment validation passed")
        return settings
    except ValidationError as e:
        logger.error(f"Environment validation failed: {e}")
        raise
```

**ファイル**:
- `backend/config.py` (設定検証)
- `scripts/validate_env.py` (検証スクリプト)

#### D3. Key Vault統合準備
**タスク**: Azure Key Vault接続テスト
```python
# backend/services/keyvault_service.py 実装：
class KeyVaultService:
    def __init__(self, vault_url: str):
        credential = DefaultAzureCredential()
        self.client = SecretClient(vault_url=vault_url, credential=credential)

    async def get_secret(self, secret_name: str) -> str:
        try:
            secret = self.client.get_secret(secret_name)
            return secret.value
        except Exception as e:
            logger.error(f"Failed to get secret {secret_name}: {e}")
            raise
```

**ファイル**:
- `backend/services/keyvault_service.py` (新規作成)
- `backend/requirements.txt` (azure-keyvault-secrets追加)

#### D4. ログ設定改善
**タスク**: 構造化ログ・レベル制御
```python
# backend/utils/logging.py 実装：
import structlog

def setup_logging(log_level: str = "INFO", environment: str = "development"):
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if environment == "production"
            else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
```

**ファイル**:
- `backend/utils/logging.py` (新規作成)
- `backend/main.py` (ログ初期化)

## 実行順序

### ステップ1: テスト環境改善 (最優先)
1. `backend/tests/conftest.py` 強化
2. テストDB分離設定
3. モックLLM実装
4. 既存テストの分離・修正

### ステップ2: CI/CD基盤構築
1. GitHub Actions設定
2. Pre-commit hooks強化
3. セキュリティスキャン統合
4. カバレッジ強制設定

### ステップ3: データベース準備
1. PostgreSQL Docker統合
2. Alembic設定更新
3. 接続プール設定
4. バックアップスクリプト作成

### ステップ4: 環境設定強化
1. .env管理改善
2. 設定検証機能
3. Key Vault統合準備
4. ログ設定改善

## 完了条件

### Phase 1.5A 完了条件
```bash
# テスト環境分離確認
cd backend && pytest tests/ --create-db  # 専用DBでテスト実行、実行後自動削除
# ✅ テストDB分離、自動クリーンアップ
# ✅ モックLLM使用、実際のAPI呼び出し回避
# ✅ unit/integration分離
```

### Phase 1.5B 完了条件
```bash
# PostgreSQL確認
docker-compose up postgres
python scripts/test_postgres_connection.py  # 接続成功
# ✅ PostgreSQL統合
# ✅ Alembic自動マイグレーション
# ✅ 接続プール動作
```

### Phase 1.5C 完了条件
```bash
# CI/CD確認
git push origin main  # GitHub Actions緑、カバレッジ80%以上
pre-commit run --all-files  # 全チェック成功
# ✅ GitHub Actions完全動作
# ✅ Pre-commit hooks動作
# ✅ セキュリティスキャン実行
```

### Phase 1.5D 完了条件
```bash
# 環境設定確認
python scripts/validate_env.py  # 全必須環境変数確認
python scripts/test_keyvault.py  # Key Vault接続テスト
# ✅ 環境別設定ファイル
# ✅ 起動時設定検証
# ✅ 構造化ログ動作
```

## 期待される効果

1. **テスト品質向上**: テストDB分離でデータ汚染排除、実行速度向上
2. **開発効率向上**: CI/CD自動化で品質チェック自動化
3. **本番準備完了**: PostgreSQL移行準備、環境設定整備
4. **運用安全性**: バックアップ・復旧手順、設定検証機能

---

*Created: 2025-06-10*
*Status: Planning Phase*
