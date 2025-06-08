# ローカル値の計算
locals {
  # リソース名の命名規則: {project}-{resource}-{environment}
  resource_group_name = "${var.project_name}-rg-${var.environment}"

  # 共通名前プレフィックス
  name_prefix = "${var.project_name}-${var.environment}"

  # 無料枠ガードレール
  openai_name    = "${local.name_prefix}-openai"
  search_name    = "${local.name_prefix}-search"
  cosmos_name    = "${local.name_prefix}-cosmos"
  container_name = "${local.name_prefix}-api"
  logs_name      = "${local.name_prefix}-logs"

  # 全リソース共通タグ
  common_tags = merge(var.common_tags, {
    ResourceGroup = local.resource_group_name
    CreatedBy     = "terraform"
    FreeTierOnly  = tostring(var.is_free_tier)
  })
}

# === Bicep連携データソース ===
# Bicepでデプロイされたリソースの参照
data "azurerm_key_vault" "bicep_kv" {
  count               = var.bicep_key_vault_name != "" ? 1 : 0
  name                = var.bicep_key_vault_name
  resource_group_name = local.resource_group_name
}

# Key VaultからAI Search APIキーを取得
data "azurerm_key_vault_secret" "search_key" {
  count        = var.bicep_key_vault_name != "" ? 1 : 0
  name         = var.bicep_search_key_secret_name
  key_vault_id = data.azurerm_key_vault.bicep_kv[0].id
}

# === リソースグループ ===
resource "azurerm_resource_group" "main" {
  name     = local.resource_group_name
  location = var.location

  tags = local.common_tags

  lifecycle {
    # 開発環境では削除保護を無効化
    prevent_destroy = false
  }
}

# === Log Analytics Workspace（無料枠 5GB/日） ===
resource "azurerm_log_analytics_workspace" "main" {
  name                = local.logs_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  # 無料枠: 5GB/日、7日保持
  sku               = "Free"
  retention_in_days = 7

  tags = local.common_tags
}

# === データ収集ルール（OpenTelemetry用） ===
resource "azurerm_monitor_data_collection_rule" "otel" {
  name                = "${local.name_prefix}-otel-dcr"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  destinations {
    log_analytics {
      workspace_resource_id = azurerm_log_analytics_workspace.main.id
      name                  = "destination-log"
    }
  }

  data_flow {
    streams      = ["Microsoft-InsightsMetrics"]
    destinations = ["destination-log"]
  }

  data_sources {
    performance_counter {
      streams                       = ["Microsoft-InsightsMetrics"]
      sampling_frequency_in_seconds = 60
      counter_specifiers            = ["\\Processor(_Total)\\% Processor Time"]
      name                          = "perfCounterDataSource60"
    }
  }

  tags = local.common_tags
}
