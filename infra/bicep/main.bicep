// ============================================================================
// QRAI Phase 0 - Bicep Resources (AI Search, Static Web Apps)
// ============================================================================

@description('プロジェクト名')
param projectName string = 'qrai'

@description('環境名')
param environment string = 'dev'

@description('デプロイ先リージョン（メイン）')
param location string = resourceGroup().location

@description('AI Search専用リージョン')
param searchLocation string = 'eastus2'

@description('無料枠使用フラグ')
param isFreeTier bool = true

@description('AI Search SKU')
@allowed(['free', 'basic'])
param searchSku string = 'free'

@description('Key Vault アクセス許可対象のオブジェクトID')
param keyVaultAccessObjectId string

@description('GitHubリポジトリURL')
param gitHubRepositoryUrl string = 'https://github.com/your-username/your-repository'

@description('OpenRouter API Key（セキュア）')
@secure()
param openRouterApiKey string = ''

@description('Google AI Studio API Key（セキュア）')
@secure()
param googleAiApiKey string = ''

@description('Azure OpenAI API Key（セキュア・オプション）')
@secure()
param azureOpenAiApiKey string = ''

@description('Azure OpenAI Endpoint（オプション）')
param azureOpenAiEndpoint string = ''

@description('共通タグ')
param commonTags object = {
  Project: 'QRAI'
  Environment: environment
  FreeTier: string(isFreeTier)
  ManagedBy: 'bicep'
}

// ============================================================================
// Local Variables
// ============================================================================

var namePrefix = '${projectName}-${environment}'
var searchName = '${namePrefix}-search'
var swaName = '${namePrefix}-swa'
var keyVaultName = '${namePrefix}kv${uniqueString(resourceGroup().id)}'

// ============================================================================
// Key Vault (セキュリティ中核)
// ============================================================================

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  tags: commonTags
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: tenant().tenantId
    enabledForDeployment: true
    enabledForTemplateDeployment: true
    enabledForDiskEncryption: false
    enableRbacAuthorization: false
    accessPolicies: [
      {
        tenantId: tenant().tenantId
        objectId: keyVaultAccessObjectId
        permissions: {
          keys: ['get', 'list']
          secrets: ['get', 'list', 'set', 'delete']
          certificates: ['get', 'list']
        }
      }
    ]
    networkAcls: {
      defaultAction: 'Allow'
      bypass: 'AzureServices'
    }
    publicNetworkAccess: 'Enabled'
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
  }
}

// ============================================================================
// LLM Provider API Keys Storage
// ============================================================================

// OpenRouter API キーをKey Vaultに保存
resource openRouterKeySecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = if (!empty(openRouterApiKey)) {
  parent: keyVault
  name: 'openrouter-api-key'
  properties: {
    value: openRouterApiKey
    attributes: {
      enabled: true
    }
    contentType: 'OpenRouter API Key'
  }
}

// Google AI Studio API キーをKey Vaultに保存
resource googleAiKeySecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = if (!empty(googleAiApiKey)) {
  parent: keyVault
  name: 'google-ai-api-key'
  properties: {
    value: googleAiApiKey
    attributes: {
      enabled: true
    }
    contentType: 'Google AI Studio API Key'
  }
}

// Azure OpenAI API キーをKey Vaultに保存（オプション）
resource azureOpenAiKeySecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = if (!empty(azureOpenAiApiKey)) {
  parent: keyVault
  name: 'azure-openai-api-key'
  properties: {
    value: azureOpenAiApiKey
    attributes: {
      enabled: true
    }
    contentType: 'Azure OpenAI API Key'
  }
}

// Azure OpenAI エンドポイントをKey Vaultに保存（オプション）
resource azureOpenAiEndpointSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = if (!empty(azureOpenAiEndpoint)) {
  parent: keyVault
  name: 'azure-openai-endpoint'
  properties: {
    value: azureOpenAiEndpoint
    attributes: {
      enabled: true
    }
    contentType: 'Azure OpenAI Endpoint URL'
  }
}

// ============================================================================
// Azure AI Search Service (Vector Search for RAG)
// ============================================================================

resource searchService 'Microsoft.Search/searchServices@2024-03-01-preview' = {
  name: searchName
  location: searchLocation
  tags: union(commonTags, {
    Service: 'AISearch'
    Region: searchLocation
    Purpose: 'RAG-VectorSearch'
  })
  sku: {
    name: searchSku
  }
  properties: {
    replicaCount: 1
    partitionCount: 1
    hostingMode: 'default'
    publicNetworkAccess: 'enabled'
    networkRuleSet: {
      ipRules: []  // 開発環境では全IP許可（空配列で全許可）
    }
    authOptions: {
      apiKeyOnly: {}
    }
    disableLocalAuth: false
    semanticSearch: isFreeTier ? 'disabled' : 'free'
  }
}

// AI Search API キーをKey Vaultに保存
resource searchKeySecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'aisearch-api-key'
  properties: {
    value: searchService.listAdminKeys().primaryKey
    attributes: {
      enabled: true
    }
    contentType: 'Azure AI Search Admin API Key'
  }
}

// ============================================================================
// Static Web Apps (Next.js Frontend)
// ============================================================================

resource staticWebApp 'Microsoft.Web/staticSites@2023-01-01' = {
  name: swaName
  location: location
  tags: union(commonTags, {
    Service: 'StaticWebApp'
    Region: location
    Purpose: 'NextJS-Frontend'
  })
  sku: {
    name: 'Free'
    tier: 'Free'
  }
  properties: {
    repositoryUrl: gitHubRepositoryUrl
    branch: 'main'
    buildProperties: {
      appLocation: '/frontend'
      apiLocation: ''
      outputLocation: 'out'
    }
    stagingEnvironmentPolicy: 'Enabled'
    allowConfigFileUpdates: true
    enterpriseGradeCdnStatus: 'Disabled'
  }
}

// ============================================================================
// Outputs (セキュア: Key Vault参照のみ)
// ============================================================================

@description('Key Vault 名')
output keyVaultName string = keyVault.name

@description('Key Vault URI')
output keyVaultUri string = keyVault.properties.vaultUri

@description('AI Search エンドポイント')
output searchEndpoint string = 'https://${searchService.name}.search.windows.net'

@description('AI Search サービス名')
output searchServiceName string = searchService.name

@description('Static Web App URL')
output staticWebAppUrl string = staticWebApp.properties.defaultHostname

@description('Static Web App 名')
output staticWebAppName string = staticWebApp.name

@description('リージョン配置情報')
output regionDeployment object = {
  keyVault: location
  aiSearch: searchLocation
  staticWebApp: location
}

@description('LLM Provider設定情報（セキュア: Key Vault参照）')
output llmProviderConfig object = {
  // Key Vault参照情報（セキュア）
  keyVaultName: keyVault.name
  keyVaultUri: keyVault.properties.vaultUri
  openRouterKeySecretName: !empty(openRouterApiKey) ? openRouterKeySecret.name : ''
  googleAiKeySecretName: !empty(googleAiApiKey) ? googleAiKeySecret.name : ''
  azureOpenAiKeySecretName: !empty(azureOpenAiApiKey) ? azureOpenAiKeySecret.name : ''
  azureOpenAiEndpointSecretName: !empty(azureOpenAiEndpoint) ? azureOpenAiEndpointSecret.name : ''

  // AI Search情報
  searchEndpoint: 'https://${searchService.name}.search.windows.net'
  searchKeySecretName: searchKeySecret.name

  // リージョン情報
  searchRegion: searchLocation
}
