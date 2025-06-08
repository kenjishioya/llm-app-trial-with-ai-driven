# === Container Apps Environment ===
resource "azurerm_container_app_environment" "main" {
  name                = "${local.name_prefix}-ca-env"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  # Log Analytics統合
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  tags = local.common_tags
}

# === Container App（FastAPI バックエンド） ===
resource "azurerm_container_app" "api" {
  name                         = local.container_name
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"

  template {
    # スケーリング設定（無料枠最適化）
    min_replicas = var.container_min_replicas # 0 = 完全停止でコスト削減
    max_replicas = var.container_max_replicas # 1 = 無料枠制限

    container {
      name   = "qrai-api"
      image  = "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest" # プレースホルダー
      cpu    = 0.25
      memory = "0.5Gi"

      # 環境変数（LLMプロバイダー対応）
      env {
        name  = "ENV"
        value = var.environment
      }

      env {
        name  = "LOG_LEVEL"
        value = "INFO"
      }

      # LLM プロバイダー設定
      env {
        name  = "LLM_PRIMARY_PROVIDER"
        value = var.llm_primary_provider
      }

      env {
        name  = "LLM_FALLBACK_PROVIDERS"
        value = join(",", var.llm_fallback_providers)
      }

      # Key Vault 統合（APIキー管理）
      env {
        name  = "AZURE_KEYVAULT_URL"
        value = var.bicep_key_vault_name != "" ? data.azurerm_key_vault.bicep_kv[0].vault_uri : ""
      }

      # AI Search 接続情報（Bicepから取得）
      env {
        name  = "AZURE_SEARCH_ENDPOINT"
        value = var.bicep_search_endpoint
      }

      # Cosmos DB 接続情報
      env {
        name  = "COSMOS_PG_HOST"
        value = "c.${azurerm_cosmosdb_postgresql_cluster.main.name}.postgres.cosmos.azure.com"
      }

      env {
        name  = "COSMOS_PG_PORT"
        value = "5432"
      }

      env {
        name  = "COSMOS_PG_DATABASE"
        value = "citus" # デフォルトデータベース名
      }

      env {
        name  = "COSMOS_PG_USER"
        value = "citus"
      }

      env {
        name        = "COSMOS_PG_PASSWORD"
        secret_name = "cosmos-db-password"
      }
    }
  }

  # HTTP入力設定
  ingress {
    allow_insecure_connections = false
    external_enabled           = true
    target_port                = 8000

    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  # シークレット設定（必要最小限）
  secret { // pragma: allowlist secret
    name  = "cosmos-db-password"
    value = random_password.cosmos_password.result
  }

  tags = local.common_tags
}
