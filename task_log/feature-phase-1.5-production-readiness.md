# Phase 1.5: 本番運用準備 実行計画

> **目的**: Phase 1 で残存した本番運用準備の課題を解決し、テスト環境分離・データベース移行・CI/CD整備・環境設定強化を実施する

## 背景・課題

Phase 1 完了時に判明した本番運用準備不足の課題：
- ✅ **テスト環境分離**: tests/test_api.py が本番DBに直接書き込み（開発用SQLiteだが問題）→ **完了**
- ✅ **テストデータ汚染**: テスト実行でセッションが大量作成される問題を確認 → **完了**
- ✅ **データベース設定**: 開発環境でもSQLite使用、本番PostgreSQL移行準備不足 → **完了**
- ❌ **CI/CD未整備**: GitHub Actions, pre-commit hooks未実装 → **進行中**
- ❌ **環境変数管理**: .env管理、本番シークレット分離未対応 → **未着手**

## 実行計画

### ✅ A. テスト環境改善 (優先度: 最高) - **完了 2025-06-10**

**結果**: 47/47テスト成功 (100%), カバレッジ80%達成

#### ✅ A1. テストDB完全分離
- 一時ファイルベースSQLite使用で各テスト独立化
- `create_test_engine()`関数で独立エンジン作成
- 自動クリーンアップ機能実装（テスト後のDB削除）

#### ✅ A2. モックLLM実装
- `backend/tests/mocks/llm_mock.py`作成
- 動的回答生成機能（プロンプト内容に基づく応答）
- 実際のAPI呼び出し回避、テスト高速化

#### ✅ A3. テストカテゴリ分離
- `backend/tests/unit/` - 純粋ユニットテスト（11個成功）
- `backend/tests/integration/` - DB連携テスト（18個成功）
- `backend/tests/mocks/` - モック実装ライブラリ

#### ✅ A4. フィクスチャ強化
- pytest標準パターンによる堅牢なフィクスチャ実装
- 各テスト間の完全分離保証
- 自動リソース管理・クリーンアップ

### ✅ B. データベース本番準備 (優先度: 高) - **完了 2025-06-10**

**結果**: PostgreSQL完全統合、SQLite → PostgreSQL移行完了

#### ✅ B1. PostgreSQL Docker統合
- `qrai_postgres`コンテナで稼働（postgres:15-alpine）
- データベース: `qrai_dev`、ユーザー: `qrai_user`
- ヘルスチェック・依存関係管理
- **確認**: GraphQL API経由でPostgreSQLにデータ保存成功

#### ✅ B2. Alembic本番運用設定
- 環境変数`DATABASE_URL`から動的設定取得
- マイグレーション自動生成・実行成功
- Black統合による自動コードフォーマット

#### ✅ B3. 接続プール設定
- 非同期エンジン（asyncpg）による高性能接続
- プール最適化: 基本10接続、最大30接続
- ヘルスチェック・自動再接続機能

#### ✅ B4. バックアップ戦略
- `scripts/backup_database.sh` - 自動バックアップ
- `scripts/restore_database.sh` - 復旧機能
- 7日間自動ローテーション、Azure Blob Storage対応

### 🔄 C. CI/CD実装 (優先度: 高) - **進行中**

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

### ✅ D. 環境設定強化 (優先度: 中) - **完了 2025-06-10**

**結果**: D1-D4完全実装、Key Vault統合・構造化ログ・環境設定一貫化達成

#### ✅ D1. .env管理改善
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

#### ✅ D2. 設定検証機能
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

#### ✅ D3. Key Vault統合準備
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

#### ✅ D4. ログ設定改善
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
