# === リソースグループ出力 ===
output "resource_group_name" {
  description = "作成されたリソースグループ名"
  value       = azurerm_resource_group.main.name
}

output "resource_group_location" {
  description = "リソースグループの場所"
  value       = azurerm_resource_group.main.location
}

# === Cosmos DB 出力 ===
output "cosmos_cluster_name" {
  description = "Cosmos DB for PostgreSQL クラスタ名"
  value       = azurerm_cosmosdb_postgresql_cluster.main.name
}

output "cosmos_database_name" {
  description = "作成されたデータベース名（デフォルト）"
  value       = "citus" # Cosmos DB for PostgreSQLのデフォルトデータベース名
}

output "cosmos_connection_string" {
  description = "Cosmos DB PostgreSQL 接続文字列（機密情報）"
  value       = "postgresql://citus:${random_password.cosmos_password.result}@c.${azurerm_cosmosdb_postgresql_cluster.main.name}.postgres.cosmos.azure.com:5432/citus?sslmode=require"
  sensitive   = true
}

# === Container Apps 出力 ===
output "container_app_url" {
  description = "Container App の公開URL"
  value       = "https://${azurerm_container_app.api.latest_revision_fqdn}"
}

output "container_app_name" {
  description = "Container App 名"
  value       = azurerm_container_app.api.name
}

# === Log Analytics 出力 ===
output "log_analytics_workspace_id" {
  description = "Log Analytics ワークスペースID"
  value       = azurerm_log_analytics_workspace.main.workspace_id
}

output "log_analytics_name" {
  description = "Log Analytics ワークスペース名"
  value       = azurerm_log_analytics_workspace.main.name
}

# === コスト管理出力 ===
output "budget_name" {
  description = "作成された予算名"
  value       = azurerm_consumption_budget_resource_group.main.name
}

# === Bicep連携用の出力 ===
output "terraform_outputs_for_bicep" {
  description = "Bicepで使用するTerraform出力値"
  value = {
    resource_group_name        = azurerm_resource_group.main.name
    location                   = azurerm_resource_group.main.location
    log_analytics_workspace_id = azurerm_log_analytics_workspace.main.workspace_id
    cosmos_host                = "c.${azurerm_cosmosdb_postgresql_cluster.main.name}.postgres.cosmos.azure.com"
    cosmos_database            = "citus" # デフォルトデータベース名
  }
}

# === 環境変数設定用の出力（開発用） ===
output "env_vars_sample" {
  description = "アプリケーション用環境変数サンプル（LLMプロバイダー対応）"
  value = {
    # LLM プロバイダー設定（Key Vault経由で取得）
    LLM_PRIMARY_PROVIDER   = "openrouter"
    LLM_FALLBACK_PROVIDERS = "google_ai,azure_openai"

    # Bicepで管理されるリソース（データソースから取得）
    AZURE_KEYVAULT_URL    = var.bicep_key_vault_name != "" ? data.azurerm_key_vault.bicep_kv[0].vault_uri : ""
    AZURE_SEARCH_ENDPOINT = var.bicep_search_endpoint

    # Terraformで管理されるリソース
    COSMOS_PG_HOST             = "c.${azurerm_cosmosdb_postgresql_cluster.main.name}.postgres.cosmos.azure.com"
    COSMOS_PG_PORT             = "5432"
    COSMOS_PG_DATABASE         = "citus" # デフォルトデータベース名
    COSMOS_PG_USER             = "citus"
    LOG_ANALYTICS_WORKSPACE_ID = azurerm_log_analytics_workspace.main.workspace_id

    # アプリケーション設定
    ENVIRONMENT  = var.environment
    PROJECT_NAME = var.project_name
  }
  sensitive = false
}

# === 機密情報（Key Vault経由での取得方法） ===
output "sensitive_keys_info" { // pragma: allowlist secret
  description = "機密情報の取得方法（LLMプロバイダー対応）"
  value = {
    openrouter_key_cmd = var.bicep_key_vault_name != "" ? "az keyvault secret show --vault-name ${var.bicep_key_vault_name} --name openrouter-api-key --query value -o tsv" : ""
    google_ai_key_cmd  = var.bicep_key_vault_name != "" ? "az keyvault secret show --vault-name ${var.bicep_key_vault_name} --name google-ai-api-key --query value -o tsv" : ""
    search_key_cmd     = var.bicep_key_vault_name != "" ? "az keyvault secret show --vault-name ${var.bicep_key_vault_name} --name aisearch-api-key --query value -o tsv" : ""
    cosmos_password    = "terraform output -raw cosmos_connection_string"
  }
}
