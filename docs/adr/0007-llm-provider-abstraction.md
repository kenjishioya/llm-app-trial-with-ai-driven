# ADR-0007: LLMプロバイダー抽象化パターンの採用

## ステータス
承認済み

## 背景
Azure OpenAIのクォータ制限により、複数のLLMプロバイダーに対応できるクリーンアーキテクチャの必要性が生じた。

### 問題
- Azure OpenAI無料枠でのクォータ制限（TPM = 0）
- 特定プロバイダーへの依存によるベンダーロックイン
- 異なるAPIフォーマットによる実装の複雑化

### 要件
- Azure OpenAI、OpenRouter、Google AI Studio等への対応
- 既存コードへの影響最小化
- 将来的なプロバイダー追加の容易性

## 決定
以下のクリーンアーキテクチャパターンを採用する：

### 1. LLMプロバイダーインターフェース
```python
from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, Dict, Any

class ILLMProvider(ABC):
    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        pass

    @abstractmethod
    async def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> AsyncGenerator[str, None]:
        pass
```

### 2. プロバイダー実装
- `AzureOpenAIProvider`: Azure OpenAI実装
- `OpenRouterProvider`: OpenRouter実装
- `GoogleAIProvider`: Google AI Studio実装

### 3. ファクトリーパターン
環境変数に基づく自動プロバイダー選択

### 4. 設定管理
```yaml
llm:
  primary_provider: "openrouter"
  fallback_providers: ["google_ai", "azure_openai"]
  providers:
    openrouter:
      api_key: "${OPENROUTER_API_KEY}"
      models:
        chat: "deepseek/deepseek-r1:free"
        embedding: "text-embedding-ada-002"
```

## 結果
### ポジティブ
- ✅ ベンダーロックイン回避
- ✅ クォータ制限の分散
- ✅ コスト最適化（無料モデル利用）
- ✅ 既存コードへの影響最小化

### ネガティブ
- ⚠️ 初期実装コストの増加
- ⚠️ テスト対象の拡大
- ⚠️ 設定管理の複雑化

## インパクト
### アーキテクチャ
- `src/llm/`: LLMプロバイダー実装ディレクトリ
- `src/config/`: プロバイダー設定管理
- `src/services/`: プロバイダー選択ロジック

### インフラストラクチャ
- Bicepテンプレート: Azure OpenAI依存の除去
- 環境変数: 複数プロバイダーのAPIキー管理
- CI/CD: 複数プロバイダーでのテスト追加

## 参考資料
- [OpenRouter API Documentation](https://openrouter.ai/docs)
- [Google AI Studio API](https://ai.google.dev/docs)
- [Azure OpenAI Service](https://docs.microsoft.com/azure/ai-services/openai/)
