# === Azure Cost Management Budget ===
data "azurerm_client_config" "current" {}

resource "azurerm_consumption_budget_resource_group" "main" {
  name              = "${local.name_prefix}-budget"
  resource_group_id = azurerm_resource_group.main.id

  amount     = var.budget_amount
  time_grain = "Monthly"

  time_period {
    start_date = formatdate("YYYY-MM-01T00:00:00Z", timestamp())
    end_date   = formatdate("YYYY-MM-01T00:00:00Z", timeadd(timestamp(), "8760h")) # 1年後
  }

  # 80%でアラート
  notification {
    enabled        = true
    threshold      = var.budget_alert_threshold
    operator       = "GreaterThan"
    threshold_type = "Actual"

    contact_emails = [] # 実際のメールアドレスを後で追加
  }

  # 90%で追加アラート
  notification {
    enabled        = true
    threshold      = 90
    operator       = "GreaterThan"
    threshold_type = "Actual"

    contact_emails = [] # 実際のメールアドレスを後で追加
  }

  # 100%予測でアラート
  notification {
    enabled        = true
    threshold      = 100
    operator       = "GreaterThan"
    threshold_type = "Forecasted"

    contact_emails = [] # 実際のメールアドレスを後で追加
  }
}

# === コスト監視用のLog Analyticsクエリ（後で使用） ===
resource "azurerm_log_analytics_saved_search" "daily_cost" {
  name                       = "DailyCostAnalysis"
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  category                   = "Cost Management"
  display_name               = "Daily Cost Analysis"

  query = <<-EOT
    AzureActivity
    | where TimeGenerated >= ago(1d)
    | where CategoryValue == "Administrative"
    | summarize count() by bin(TimeGenerated, 1h), ResourceGroup
    | render timechart
  EOT
}

# === アラート用のAction Group（オプション） ===
resource "azurerm_monitor_action_group" "cost_alert" {
  name                = "${local.name_prefix}-cost-alerts"
  resource_group_name = azurerm_resource_group.main.name
  short_name          = "qraicost"

  # メール通知（実際のアドレスを後で設定）
  # email_receiver {
  #   name          = "admin"
  #   email_address = "admin@example.com"
  # }

  # Webhook通知（Slack等）
  # webhook_receiver {
  #   name        = "slack"
  #   service_uri = "https://hooks.slack.com/services/..."
  # }

  tags = local.common_tags
}
