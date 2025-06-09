#!/bin/bash

# 重要ファイルバックアップスクリプト
# 実行前にこのスクリプトで重要ファイルをバックアップ

BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "🔄 重要ファイルをバックアップ中..."

# バックアップ対象ファイル
IMPORTANT_FILES=(
    "backend/main.py"
    "backend/config.py"
    "backend/deps.py"
    "backend/requirements.txt"
    "backend/alembic.ini"
    "backend/models/"
    "backend/services/"
    "backend/providers/"
    "backend/api/"
    "tests/"
    "docker-compose*.yml"
    "Dockerfile*"
    "run-tests.sh"
    ".env.sample"
    ".gitignore"
)

for file in "${IMPORTANT_FILES[@]}"; do
    if [[ -e "$file" ]]; then
        echo "📄 バックアップ: $file"
        rsync -a "$file" "$BACKUP_DIR/"
    fi
done

echo "✅ バックアップ完了: $BACKUP_DIR"
echo "📝 復元が必要な場合は以下を実行:"
echo "   rsync -a $BACKUP_DIR/ ./"
