variable "project_name" {
  description = "プロジェクト名（リソース名プレフィックス用）"
  type        = string
  default     = "qrai"

  validation {
    condition     = can(regex("^[a-z][a-z0-9]{1,10}$", var.project_name))
    error_message = "プロジェクト名は小文字英数字、2-11文字で指定してください。"
  }
}

variable "environment" {
  description = "環境名（dev, stg, prod）"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "stg", "prod"], var.environment)
    error_message = "環境名はdev, stg, prodのいずれかを指定してください。"
  }
}

variable "location" {
  description = "Azureリージョン"
  type        = string
  default     = "Japan East"

  validation {
    condition = contains([
      "East Asia", "Southeast Asia", "Japan East", "Japan West"
    ], var.location)
    error_message = "Asian-Pacific リージョンを指定してください。"
  }
}

variable "is_free_tier" {
  description = "無料枠のみ使用するかどうか"
  type        = bool
  default     = true
}

# === Bicepから渡される値（LLMプロバイダー対応） ===
variable "bicep_key_vault_name" {
  description = "BicepでデプロイされたKey Vault名"
  type        = string
  default     = ""
}

variable "bicep_search_endpoint" {
  description = "BicepでデプロイされたAI Searchエンドポイント"
  type        = string
  default     = ""
}

variable "bicep_search_key_secret_name" {
  description = "Key VaultのAI Search APIキーシークレット名"
  type        = string
  default     = "aisearch-api-key"
}

variable "bicep_static_web_app_url" {
  description = "BicepでデプロイされたStatic Web Apps URL"
  type        = string
  default     = ""
}

# === LLMプロバイダー設定 ===
variable "llm_primary_provider" {
  description = "プライマリLLMプロバイダー"
  type        = string
  default     = "openrouter"

  validation {
    condition = contains([
      "openrouter", "google_ai", "azure_openai"
    ], var.llm_primary_provider)
    error_message = "プライマリプロバイダーはopenrouter, google_ai, azure_openaiのいずれかを指定してください。"
  }
}

variable "llm_fallback_providers" {
  description = "フォールバックLLMプロバイダーリスト"
  type        = list(string)
  default     = ["google_ai", "azure_openai"]
}

# === Cosmos DB 設定 ===
variable "cosmos_pg_sku" {
  description = "Cosmos DB for PostgreSQL SKU"
  type        = string
  default     = "GP_Gen5_1"
}

variable "cosmos_pg_storage_mb" {
  description = "Cosmos DB ストレージ (MB)"
  type        = number
  default     = 32768 # 32GB
}

# === Container Apps 設定 ===
variable "container_min_replicas" {
  description = "Container Apps 最小レプリカ数（0=完全停止でコスト削減）"
  type        = number
  default     = 0
}

variable "container_max_replicas" {
  description = "Container Apps 最大レプリカ数"
  type        = number
  default     = 1
}

# === コスト管理 ===
variable "budget_amount" {
  description = "月額予算上限 (USD)"
  type        = number
  default     = 5
}

variable "budget_alert_threshold" {
  description = "予算アラート閾値 (%)"
  type        = number
  default     = 80
}

# === タグ ===
variable "common_tags" {
  description = "全リソースに適用される共通タグ"
  type        = map(string)
  default = {
    Project     = "QRAI"
    Owner       = "Individual"
    Environment = "Development"
    ManagedBy   = "Terraform"
  }
}
