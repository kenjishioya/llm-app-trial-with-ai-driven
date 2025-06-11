#!/bin/bash
set -e

# PostgreSQL初期化スクリプト（シェル版）
# QRAI プロジェクト用データベース設定

echo "🔧 PostgreSQL初期化開始..."

# SQLコマンドを実行する関数
execute_sql() {
    psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "$1"
}

# 必要な拡張機能を有効化
execute_sql "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
execute_sql "CREATE EXTENSION IF NOT EXISTS \"pg_trgm\";"

# 接続文字エンコーディング確認
execute_sql "SELECT current_setting('server_encoding') as server_encoding;"

# タイムゾーン設定
execute_sql "SET timezone = 'Asia/Tokyo';"

# ユーザーパスワードをSCRAM-SHA-256形式で再設定（認証方式統一）
# 環境変数POSTGRES_PASSWORDを安全に使用
execute_sql "ALTER USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';"

echo "✅ PostgreSQL database initialized for QRAI project"
echo "📊 Database: $POSTGRES_DB"
echo "👤 User: $POSTGRES_USER (SCRAM-SHA-256 password set)"
echo "🔧 Extensions: uuid-ossp, pg_trgm"
echo "🌏 Timezone: Asia/Tokyo"
