# 環境設定ガイド - QRAI LLMプロバイダー対応

> **目的** — OpenRouter、Google AI Studio、Azure OpenAI（オプション）のAPIキー管理と環境変数設定を明確化し、開発・本番環境での安全な認証情報管理を実現する。

---

## 1. 概要

QRAIプロジェクトでは以下のLLMプロバイダーに対応しています：

| プロバイダー | 用途 | 無料枠 | API形式 |
|------------|------|--------|---------|
| **OpenRouter** | プライマリ（DeepSeek R1） | ✅ 有 | OpenAI互換 |
| **Google AI Studio** | フォールバック（Gemini） | ✅ 有 | Google API |
| **Azure OpenAI** | エンタープライズ | ❌ 無 | Azure API |

---

## 2. APIキー取得手順

### 2.1 OpenRouter（推奨プライマリ）

1. **アカウント作成**: [openrouter.ai](https://openrouter.ai) でサインアップ
2. **APIキー生成**: Settings > API Keys > Create New Key
3. **無料モデル有効化**: Settings > Privacy で "Model Training: ON" を設定
4. **キー形式**: `sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

#### 無料枠詳細
- DeepSeek R1 Free: 50 requests/day（デフォルト）
- $10チャージで 1,000 requests/day に拡張可能
- レート制限: 20 RPM

### 2.2 Google AI Studio（推奨セカンダリ）

1. **Google Cloud Console**: [aistudio.google.com](https://aistudio.google.com) アクセス
2. **APIキー生成**: Get API Key > Create API Key in New Project
3. **キー形式**: `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`

#### 無料枠詳細
- Gemini 2.5 Flash: 15 RPM, 1M TPM, 1,500 RPD
- 地域制限: 一部の国では利用不可

### 2.3 Azure OpenAI（オプション）

1. **Azure Portal**: [portal.azure.com](https://portal.azure.com) でリソース作成
2. **クォータ申請**: 無料枠では TPM = 0 のため有料プラン必要
3. **キー取得**: OpenAI Service > Keys and Endpoint
4. **キー形式**: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## 3. 環境変数設定

### 3.1 開発環境（.env ファイル）

プロジェクトルートに `.env` ファイルを作成：

```bash
# QRAI LLM プロバイダー設定
# =================================

# OpenRouter（プライマリ）
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Google AI Studio（セカンダリ）
GOOGLE_AI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Azure OpenAI（オプション）
AZURE_OPENAI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# LLM設定
LLM_PRIMARY_PROVIDER=openrouter
LLM_FALLBACK_PROVIDERS=google_ai,azure_openai

# Azure AI Search（ベクトル検索用）
AZURE_SEARCH_SERVICE_NAME=qrai-dev-search
AZURE_SEARCH_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AZURE_SEARCH_INDEX_NAME=documents

# Key Vault（本番環境）
AZURE_KEYVAULT_URL=https://qrai-devkvxxxxxxxx.vault.azure.net/

# デバッグ設定
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3.2 .env.example テンプレート

```bash
# QRAI LLM プロバイダー設定テンプレート
# =====================================
# このファイルをコピーして .env ファイルを作成し、実際のAPIキーを設定してください

# OpenRouter（プライマリ）- 必須
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-api-key-here

# Google AI Studio（セカンダリ）- 必須
GOOGLE_AI_API_KEY=AIzaSy-your-google-ai-api-key-here

# Azure OpenAI（オプション）
AZURE_OPENAI_API_KEY=your-azure-openai-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# プロバイダー選択
LLM_PRIMARY_PROVIDER=openrouter
LLM_FALLBACK_PROVIDERS=google_ai

# Azure AI Search
AZURE_SEARCH_SERVICE_NAME=your-search-service-name
AZURE_SEARCH_API_KEY=your-search-api-key
AZURE_SEARCH_INDEX_NAME=documents

# 開発用設定
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### 3.3 セキュリティ設定

`.gitignore` に以下を追加：

```gitignore
# 環境設定ファイル
.env
.env.local
.env.development
.env.production

# APIキー関連
**/api_keys.json
**/secrets.yml
```

---

## 4. Azure Key Vault統合（本番環境）

### 4.1 Key Vault設定

Bicepデプロイ時にAPIキーを安全に保存：

```bash
# デプロイコマンド例
az deployment group create \
  --resource-group qrai-dev-rg \
  --template-file infra/bicep/main.bicep \
  --parameters @infra/bicep/main.bicepparam \
  --parameters \
    keyVaultAccessObjectId="$(az ad signed-in-user show --query id -o tsv)" \
    openRouterApiKey="sk-or-v1-xxxxx" \
    googleAiApiKey="AIzaSyxxxxx"
```

### 4.2 Key Vault参照（Python）

```python
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
import os

def get_llm_config():
    """Key VaultからLLMプロバイダー設定を取得"""

    # 開発環境では.envファイルを使用
    if os.getenv('ENVIRONMENT') == 'development':
        return {
            'openrouter_api_key': os.getenv('OPENROUTER_API_KEY'),
            'google_ai_api_key': os.getenv('GOOGLE_AI_API_KEY'),
        }

    # 本番環境ではKey Vaultを使用
    credential = DefaultAzureCredential()
    secret_client = SecretClient(
        vault_url=os.getenv('AZURE_KEYVAULT_URL'),
        credential=credential
    )

    return {
        'openrouter_api_key': secret_client.get_secret('openrouter-api-key').value,
        'google_ai_api_key': secret_client.get_secret('google-ai-api-key').value,
    }
```

---

## 5. 環境別設定

### 5.1 開発環境（Local）

```bash
# 必須APIキー
export OPENROUTER_API_KEY=sk-or-v1-xxxxx
export GOOGLE_AI_API_KEY=AIzaSyxxxxx

# プロバイダー設定
export LLM_PRIMARY_PROVIDER=openrouter
export LLM_FALLBACK_PROVIDERS=google_ai

# デバッグ設定
export LOG_LEVEL=DEBUG
export LANGCHAIN_TRACING_V2=true
```

### 5.2 本番環境（Azure Container Apps）

```bash
# Key Vault参照
export AZURE_KEYVAULT_URL=https://qrai-devkvxxxxxxxx.vault.azure.net/

# マネージドIDを使用してKey Vaultアクセス
export AZURE_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# プロバイダー設定
export LLM_PRIMARY_PROVIDER=openrouter
export LLM_FALLBACK_PROVIDERS=google_ai,azure_openai

# 本番設定
export ENVIRONMENT=production
export LOG_LEVEL=INFO
```

---

## 6. 設定検証

### 6.1 設定確認スクリプト

```python
#!/usr/bin/env python3
"""
LLMプロバイダー設定確認スクリプト
usage: python scripts/check_llm_config.py
"""

import os
import asyncio
from openai import OpenAI
import google.generativeai as genai

async def check_openrouter():
    """OpenRouter接続確認"""
    try:
        client = OpenAI(
            api_key=os.getenv('OPENROUTER_API_KEY'),
            base_url="https://openrouter.ai/api/v1"
        )

        response = client.chat.completions.create(
            model="deepseek/deepseek-r1:free",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )

        print("✅ OpenRouter: 接続成功")
        return True
    except Exception as e:
        print(f"❌ OpenRouter: 接続失敗 - {e}")
        return False

async def check_google_ai():
    """Google AI Studio接続確認"""
    try:
        genai.configure(api_key=os.getenv('GOOGLE_AI_API_KEY'))
        model = genai.GenerativeModel('gemini-2.5-flash')

        response = model.generate_content("Hello")

        print("✅ Google AI: 接続成功")
        return True
    except Exception as e:
        print(f"❌ Google AI: 接続失敗 - {e}")
        return False

if __name__ == "__main__":
    print("🔍 LLMプロバイダー設定確認")
    print("=" * 30)

    asyncio.run(check_openrouter())
    asyncio.run(check_google_ai())
```

### 6.2 必要なPythonパッケージ

```txt
# requirements.txt（LLMプロバイダー関連）
openai>=1.52.0
google-generativeai>=0.8.3
langchain>=0.3.0
langchain-openai>=0.2.0
langchain-google-genai>=2.0.0
azure-keyvault-secrets>=4.8.0
azure-identity>=1.19.0
```

---

## 7. トラブルシューティング

### 7.1 よくあるエラー

| エラー | 原因 | 解決方法 |
|--------|------|----------|
| `Invalid API key` | APIキーが無効 | キーを再生成、環境変数を確認 |
| `Rate limit exceeded` | レート制限 | 時間をおいて再試行、有料プランを検討 |
| `Region not supported` | 地域制限 | VPN使用またはプロキシ経由 |
| `Quota exceeded` | クォータ上限 | 他のプロバイダーを使用 |

### 7.2 デバッグコマンド

```bash
# 環境変数確認
env | grep -E "(OPENROUTER|GOOGLE_AI|AZURE)"

# APIキー接続テスト
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model":"deepseek/deepseek-r1:free","messages":[{"role":"user","content":"test"}],"max_tokens":1}' \
     https://openrouter.ai/api/v1/chat/completions

# LangChainトレース確認
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

---

## 8. セキュリティベストプラクティス

### 8.1 APIキー管理
- ✅ APIキーは環境変数または Key Vault で管理
- ✅ `.env` ファイルは `.gitignore` に追加
- ✅ 定期的なローテーション（3ヶ月ごと）
- ✅ 本番環境では Azure Managed Identity 使用

### 8.2 アクセス制御
- ✅ Key Vault アクセス許可は最小権限
- ✅ IP制限の設定（可能な場合）
- ✅ APIキー使用状況の監視
- ✅ 異常なアクセスパターンのアラート設定

---

## 次のステップ

環境設定完了後、以下の確認を行ってください：

1. `python scripts/check_llm_config.py` で接続確認
2. `python scripts/test_llm_providers.py` で動作テスト
3. LangChain統合の動作確認
4. ストリーミング機能のテスト
