# === Cosmos DB for PostgreSQL（単一ノード無料枠） ===
resource "azurerm_cosmosdb_postgresql_cluster" "main" {
  name                = local.cosmos_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  # 管理者認証情報
  administrator_login_password = random_password.cosmos_password.result

  # 単一ノード構成（無料枠）
  coordinator_storage_quota_in_mb = var.cosmos_pg_storage_mb
  coordinator_vcore_count         = 1
  node_count                      = 0 # ワーカーノードなし

  # SKU設定
  sql_version = "15"

  tags = local.common_tags
}

# === PostgreSQL管理者パスワード生成 ===
resource "random_password" "cosmos_password" {
  length  = 16
  special = true

  # パスワード要件に従う
  min_upper   = 1
  min_lower   = 1
  min_numeric = 1
  min_special = 1
}

# === ファイアウォール設定（開発環境: 全IP許可） ===
resource "azurerm_cosmosdb_postgresql_firewall_rule" "allow_all" {
  name       = "AllowAllIPs"
  cluster_id = azurerm_cosmosdb_postgresql_cluster.main.id

  start_ip_address = "0.0.0.0"
  end_ip_address   = "255.255.255.255"
}

# === データベース作成（ノート：cluster作成時に自動作成されるため、手動作成は不要） ===
# Cosmos DB for PostgreSQLでは、クラスタ作成時にdefaultデータベースが自動作成される
# 追加データベースが必要な場合は、接続後にCREATE DATABASEクエリを実行

# === パスワードをKey Vaultに保存（オプション、後で追加） ===
# resource "azurerm_key_vault_secret" "cosmos_password" {
#   name         = "cosmos-db-password"
#   value        = random_password.cosmos_password.result
#   key_vault_id = azurerm_key_vault.main.id
#   depends_on   = [azurerm_key_vault_access_policy.current_user]
# }
