# 環境設定ガイド – QRAI

> **目的** — 開発・ステージング・本番環境の設定差分、環境変数管理、Azure リソース命名規則を体系化し、環境間の一貫性とセキュリティを確保する。チーム全体が同じ手順で環境を構築・維持できるよう標準化する。

---

## 1. 環境区分と特徴

| 環境            | 目的                | インフラ制約                | データ                   | アクセス制限             |
| ------------- | ----------------- | --------------------- | --------------------- | ------------------ |
| **development** | 個人開発・ユニットテスト      | 無料枠のみ、リソース最小構成        | ダミーデータ、テスト用社内文書       | 開発者個人アカウント         |
| **staging**   | 統合テスト・デモ・QA      | 無料枠 + 一部有料SKU         | 本番類似データ（個人情報マスキング済み） | チームメンバー + QA担当者     |
| **production** | 本番運用（将来）          | パフォーマンス重視、HA構成、有料SKU | 本番データ                 | 限定管理者 + AAD認証ユーザー |

---

## 2. Azure リソース命名規則

### 2-1 命名パターン

```
{service}-{app}-{environment}-{region}-{instance}
```

**例**:
- `rg-qrai-dev-eastus-01` (リソースグループ)
- `st-qrai-dev-eastus-01` (ストレージアカウント)
- `kv-qrai-prod-eastus-01` (Key Vault)

### 2-2 サービス略称

| サービス                     | 略称    | 例                           |
| ------------------------ | ----- | --------------------------- |
| Resource Group           | `rg`  | `rg-qrai-dev-eastus-01`     |
| Storage Account          | `st`  | `stqraideveastus01` (-)不可   |
| Key Vault                | `kv`  | `kv-qrai-dev-eastus-01`     |
| Cosmos DB                | `cosmos` | `cosmos-qrai-dev-eastus-01` |
| AI Search                | `srch` | `srch-qrai-dev-eastus-01`   |
| OpenAI                   | `oai` | `oai-qrai-dev-eastus-01`    |
| Container App            | `ca`  | `ca-qrai-dev-eastus-01`     |
| Static Web App           | `swa` | `swa-qrai-dev-eastus-01`    |
| Log Analytics Workspace | `law` | `law-qrai-dev-eastus-01`    |

### 2-3 環境・リージョン略称

| 環境       | 略称     | リージョン     | 略称      |
| -------- | ------ | --------- | ------- |
| 開発       | `dev`  | East US   | `eastus` |
| ステージング | `stg`  | West US 2 | `westus2` |
| 本番       | `prod` | East US 2 | `eastus2` |

---

## 3. 環境変数管理

### 3-1 `.env` ファイル構造

```bash
# === QRAI 環境設定 ===
# 環境識別
ENVIRONMENT=development  # development | staging | production
APP_NAME=qrai
VERSION=1.0.0

# === Azure サービス ===
# OpenAI
AZURE_OPENAI_API_KEY=your-openai-key
AZURE_OPENAI_ENDPOINT=https://oai-qrai-dev-eastus-01.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-06-01

# AI Search
AZURE_SEARCH_ENDPOINT=https://srch-qrai-dev-eastus-01.search.windows.net
AZURE_SEARCH_KEY=your-search-key
AZURE_SEARCH_INDEX=qrai-documents

# Cosmos DB for PostgreSQL
COSMOS_POSTGRES_HOST=cosmos-qrai-dev-eastus-01.postgres.cosmos.azure.com
COSMOS_POSTGRES_PORT=5432
COSMOS_POSTGRES_USER=citus
COSMOS_POSTGRES_PASSWORD=your-cosmos-password
COSMOS_POSTGRES_DATABASE=qrai

# === アプリケーション設定 ===
# FastAPI
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
FASTAPI_DEBUG=true  # development only
FASTAPI_RELOAD=true  # development only

# RAG パラメータ
RAG_TOP_K=3
RAG_TEMPERATURE=0.2
RAG_MAX_TOKENS=1024

# Deep Research
DEEP_RESEARCH_MAX_CYCLES=3
DEEP_RESEARCH_TIMEOUT=120

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=20
RATE_LIMIT_BURST=5

# === セキュリティ ===
# JWT (将来用)
JWT_SECRET_KEY=your-super-secret-jwt-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# CORS
CORS_ORIGINS=http://localhost:3000,https://swa-qrai-dev-eastus-01.azurestaticapps.net
CORS_CREDENTIALS=true

# === 監視・ログ ===
LOG_LEVEL=DEBUG  # DEBUG | INFO | WARNING | ERROR
STRUCTURED_LOGGING=true
AZURE_MONITOR_CONNECTION_STRING=InstrumentationKey=your-app-insights-key

# === 機能フラグ ===
ENABLE_AUTH=false  # development only
ENABLE_CACHE=false  # Redis未実装
ENABLE_TELEMETRY=true
```

### 3-2 環境別設定差分

#### Development 環境
```bash
ENVIRONMENT=development
FASTAPI_DEBUG=true
FASTAPI_RELOAD=true
LOG_LEVEL=DEBUG
ENABLE_AUTH=false
RATE_LIMIT_REQUESTS_PER_MINUTE=100  # 緩い制限

# Azure無料枠リソース
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
RAG_TOP_K=3
```

#### Staging 環境
```bash
ENVIRONMENT=staging
FASTAPI_DEBUG=false
FASTAPI_RELOAD=false
LOG_LEVEL=INFO
ENABLE_AUTH=true
RATE_LIMIT_REQUESTS_PER_MINUTE=50

# より多くのリソース
AZURE_OPENAI_DEPLOYMENT=gpt-4o
RAG_TOP_K=5
```

#### Production 環境
```bash
ENVIRONMENT=production
FASTAPI_DEBUG=false
FASTAPI_RELOAD=false
LOG_LEVEL=WARNING
ENABLE_AUTH=true
RATE_LIMIT_REQUESTS_PER_MINUTE=20

# 本番グレードリソース
AZURE_OPENAI_DEPLOYMENT=gpt-4o
RAG_TOP_K=3
ENABLE_CACHE=true
```

---

## 4. シークレット管理戦略

### 4-1 環境別シークレット保管

| 環境       | シークレット保管方法               | アクセス方法                      |
| -------- | ------------------------ | --------------------------- |
| **開発**   | `.env` ファイル（個人PC）         | 直接読み込み                      |
| **ステージング** | Azure Key Vault          | Managed Identity            |
| **本番**   | Azure Key Vault + 暗号化    | Managed Identity + RBAC    |

### 4-2 Key Vault 設計

```bash
# シークレット命名規則: {app}-{service}-{environment}
qrai-openai-dev-key          # AZURE_OPENAI_API_KEY
qrai-search-dev-key          # AZURE_SEARCH_KEY  
qrai-cosmos-dev-password     # COSMOS_POSTGRES_PASSWORD
qrai-jwt-dev-secret          # JWT_SECRET_KEY

# 接続文字列
qrai-cosmos-dev-connstr      # 完全な接続文字列
qrai-monitor-dev-connstr     # Azure Monitor接続文字列
```

### 4-3 Container App での環境変数注入

```yaml
# Container App 環境変数設定
apiVersion: 2022-10-01
properties:
  configuration:
    secrets:
      - name: openai-key
        keyVaultUrl: https://kv-qrai-prod-eastus-01.vault.azure.net/secrets/qrai-openai-prod-key
      - name: search-key  
        keyVaultUrl: https://kv-qrai-prod-eastus-01.vault.azure.net/secrets/qrai-search-prod-key
    
  template:
    containers:
      - name: qrai-api
        env:
          - name: AZURE_OPENAI_API_KEY
            secretRef: openai-key
          - name: AZURE_SEARCH_KEY
            secretRef: search-key
          - name: ENVIRONMENT
            value: production
```

---

## 5. 開発環境セットアップ手順

### 5-1 必須ツール

```bash
# Node.js 20.x
node --version  # v20.x.x

# Python 3.12
python --version  # Python 3.12.x

# Azure CLI 2.60+
az version

# Docker Desktop
docker --version

# (Optional) pyenv for Python version management
pyenv install 3.12.2
pyenv local 3.12.2
```

### 5-2 初回セットアップ

```bash
# 1. リポジトリクローン
git clone git@github.com:yourname/llm-app-trial-with-ai-driven.git
cd llm-app-trial-with-ai-driven

# 2. Python環境構築
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r backend/requirements-dev.txt

# 3. Node.js環境構築
cd frontend
pnpm install
cd ..

# 4. 環境変数設定
cp .env.sample .env
# .envファイルを編集してAzureのキーを設定

# 5. Azure CLI ログイン
az login
az account set --subscription "your-subscription-id"

# 6. ローカル開発サーバー起動
docker compose up --build
```

### 5-3 環境変数検証

```bash
# 環境変数が正しく設定されているか確認
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

required_vars = [
    'AZURE_OPENAI_API_KEY',
    'AZURE_OPENAI_ENDPOINT', 
    'AZURE_SEARCH_ENDPOINT',
    'AZURE_SEARCH_KEY'
]

for var in required_vars:
    value = os.getenv(var)
    if value:
        print(f'✅ {var}: {value[:10]}...')
    else:
        print(f'❌ {var}: Not set')
"
```

---

## 6. CI/CD パイプライン環境変数

### 6-1 GitHub Actions Secrets

```yaml
# .github/workflows/deploy.yml
env:
  AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
  AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
  AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
  AZURE_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
  
  # Terraform Backend
  TF_BACKEND_STORAGE_ACCOUNT: ${{ secrets.TF_BACKEND_STORAGE_ACCOUNT }}
  TF_BACKEND_ACCESS_KEY: ${{ secrets.TF_BACKEND_ACCESS_KEY }}
  
  # アプリケーション設定
  ENVIRONMENT: ${{ github.ref == 'refs/heads/main' && 'production' || 'staging' }}
```

### 6-2 環境別ワークフロー

```yaml
jobs:
  deploy-staging:
    if: github.ref == 'refs/heads/develop'
    environment: staging
    steps:
      - name: Deploy to Staging
        run: |
          export ENVIRONMENT=staging
          terraform workspace select staging
          terraform apply -auto-approve
          
  deploy-production:
    if: github.ref == 'refs/heads/main'
    environment: production
    needs: [tests]
    steps:
      - name: Deploy to Production
        run: |
          export ENVIRONMENT=production
          terraform workspace select production
          terraform apply -auto-approve
```

---

## 7. トラブルシューティング

### 7-1 よくある環境設定エラー

| エラー                          | 原因                      | 解決方法                               |
| ---------------------------- | ----------------------- | ---------------------------------- |
| `Azure CLI not logged in`   | `az login` 未実行          | `az login` を実行してブラウザで認証           |
| `Subscription not found`    | サブスクリプションIDが間違っている    | `az account list` で正しいIDを確認        |
| `OpenAI API key invalid`    | キーが正しく設定されていない         | Azure Portal でキーを再確認、`.env` 更新    |
| `Container app startup fail` | 環境変数が不足している            | Key Vault の権限とシークレット名を確認        |
| `CORS error`                | CORS_ORIGINS が間違っている | フロントエンドのURLが正しく設定されているか確認       |

### 7-2 環境差分チェックスクリプト

```bash
#!/bin/bash
# scripts/check-env-diff.sh

echo "🔍 環境設定差分チェック"

ENVS=("development" "staging" "production")

for env in "${ENVS[@]}"; do
    echo "--- ${env} 環境 ---"
    
    # 必須環境変数チェック
    if [ -f ".env.${env}" ]; then
        source ".env.${env}"
        echo "✅ 環境ファイル: .env.${env}"
        echo "🏷️  ENVIRONMENT: ${ENVIRONMENT}"
        echo "🔧 DEBUG: ${FASTAPI_DEBUG:-false}"
        echo "🔐 AUTH: ${ENABLE_AUTH:-false}"
        echo "⚡ RATE_LIMIT: ${RATE_LIMIT_REQUESTS_PER_MINUTE:-20}"
    else
        echo "❌ 環境ファイルが見つかりません: .env.${env}"
    fi
    echo ""
done
```

---

## 8. セキュリティ考慮事項

### 8-1 環境変数セキュリティ

- ✅ **本番環境では `.env` ファイルを使用しない**
- ✅ **シークレットは Azure Key Vault に保管**
- ✅ **開発環境でも重要なキーはローカルのみ保管**
- ✅ **`.env*` ファイルは `.gitignore` に追加済み**
- ❌ **GitHub にシークレットをコミットしない**

### 8-2 アクセス制御

```bash
# Key Vault アクセスポリシー例
az keyvault set-policy \
  --name kv-qrai-prod-eastus-01 \
  --object-id <container-app-managed-identity> \
  --secret-permissions get list

# Container App Managed Identity 有効化
az containerapp identity assign \
  --name ca-qrai-prod-eastus-01 \
  --resource-group rg-qrai-prod-eastus-01 \
  --system-assigned
```

---

*Last updated: 2025-06-03* 