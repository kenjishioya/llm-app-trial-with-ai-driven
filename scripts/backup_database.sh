#!/bin/bash
# PostgreSQL データベースバックアップスクリプト
# QRAI プロジェクト用

set -e  # エラー時即座に終了

# 設定
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${PROJECT_ROOT}/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# 環境変数読み込み
if [ -f "$PROJECT_ROOT/.env" ]; then
    source "$PROJECT_ROOT/.env"
fi

# デフォルト設定
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-qrai_dev}"
DB_USER="${DB_USER:-qrai_user}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-7}"

# バックアップディレクトリ作成
mkdir -p "$BACKUP_DIR"

echo "🗃️  Starting PostgreSQL backup..."
echo "Database: $DB_NAME@$DB_HOST:$DB_PORT"
echo "Timestamp: $TIMESTAMP"

# バックアップファイル名
BACKUP_FILE="$BACKUP_DIR/qrai_backup_${TIMESTAMP}.sql"
BACKUP_COMPRESSED="$BACKUP_FILE.gz"

# PostgreSQL バックアップ実行
echo "📦 Creating database dump..."
if command -v docker &> /dev/null && docker ps | grep -q "qrai_postgres"; then
    # Docker環境の場合
    echo "Using Docker PostgreSQL container..."
    docker exec qrai_postgres pg_dump -h localhost -p 5432 -U "$DB_USER" -d "$DB_NAME" \
        --verbose --clean --if-exists --create > "$BACKUP_FILE"
else
    # ローカルPostgreSQLの場合
    echo "Using local PostgreSQL..."
    PGPASSWORD="$POSTGRES_PASSWORD" pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        --verbose --clean --if-exists --create > "$BACKUP_FILE"
fi

# 圧縮
echo "🗜️  Compressing backup..."
gzip "$BACKUP_FILE"

# バックアップサイズ確認
BACKUP_SIZE=$(du -h "$BACKUP_COMPRESSED" | cut -f1)
echo "✅ Backup created: $BACKUP_COMPRESSED ($BACKUP_SIZE)"

# 古いバックアップ削除
echo "🧹 Cleaning old backups (older than $BACKUP_RETENTION_DAYS days)..."
find "$BACKUP_DIR" -name "qrai_backup_*.sql.gz" -mtime +$BACKUP_RETENTION_DAYS -delete

# 残存バックアップ確認
REMAINING_BACKUPS=$(find "$BACKUP_DIR" -name "qrai_backup_*.sql.gz" | wc -l)
echo "📁 Remaining backups: $REMAINING_BACKUPS"

# 正常終了
echo "🎉 Backup completed successfully!"
echo "Backup file: $BACKUP_COMPRESSED"

# Azure Blob Storage アップロード（オプション）
if [ -n "$AZURE_STORAGE_CONNECTION_STRING" ] && command -v az &> /dev/null; then
    echo "☁️  Uploading to Azure Blob Storage..."
    BLOB_NAME="backups/$(basename "$BACKUP_COMPRESSED")"

    az storage blob upload \
        --connection-string "$AZURE_STORAGE_CONNECTION_STRING" \
        --container-name "qrai-backups" \
        --name "$BLOB_NAME" \
        --file "$BACKUP_COMPRESSED" \
        --overwrite

    echo "✅ Uploaded to Azure: $BLOB_NAME"
else
    echo "⚠️  Azure CLI not configured, skipping cloud upload"
fi

echo "📊 Backup Summary:"
echo "  - File: $BACKUP_COMPRESSED"
echo "  - Size: $BACKUP_SIZE"
echo "  - Retention: $BACKUP_RETENTION_DAYS days"
echo "  - Local backups: $REMAINING_BACKUPS"
