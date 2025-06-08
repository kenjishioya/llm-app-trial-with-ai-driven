using 'main.bicep'

// プロジェクト設定
param projectName = 'qrai'
param environment = 'dev'
param location = 'japaneast'
param isFreeTier = true

// リージョン戦略
param searchLocation = 'japaneast'

// AI Search 設定
param searchSku = 'free'

// GitHubリポジトリ設定
param gitHubRepositoryUrl = 'https://github.com/kenjishioya/llm-app-trial-with-ai-driven'

// Key Vault設定（コマンドライン引数でオーバーライド）
param keyVaultAccessObjectId = ''

// LLM Provider設定（デプロイ時に --parameters で指定）
// 例: az deployment group create --parameters openRouterApiKey='sk-or-xxx' googleAiApiKey='AI...'
param openRouterApiKey = '' // pragma: allowlist secret
param googleAiApiKey = '' // pragma: allowlist secret
param azureOpenAiApiKey = '' // pragma: allowlist secret
param azureOpenAiEndpoint = ''

// タグ設定
param commonTags = {
  Project: 'QRAI'
  Environment: 'dev'
  Owner: 'individual'
  FreeTier: 'true'
  ManagedBy: 'bicep'
  LLMStrategy: 'multi-provider'
}
