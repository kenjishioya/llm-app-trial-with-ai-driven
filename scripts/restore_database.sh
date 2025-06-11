#!/bin/bash
# PostgreSQL データベース復旧スクリプト
# QRAI プロジェクト用

set -e  # エラー時即座に終了

# 設定
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${PROJECT_ROOT}/backups"

# 環境変数読み込み
if [ -f "$PROJECT_ROOT/.env" ]; then
    source "$PROJECT_ROOT/.env"
fi

# デフォルト設定
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-qrai_dev}"
DB_USER="${DB_USER:-qrai_user}"

# ヘルプ表示
show_help() {
    cat << EOF
PostgreSQL データベース復旧スクリプト

使用方法:
    $0 [OPTIONS] BACKUP_FILE

引数:
    BACKUP_FILE     復旧するバックアップファイル (.sql.gz または .sql)

オプション:
    -h, --help      このヘルプを表示
    -l, --list      利用可能なバックアップファイル一覧
    -c, --confirm   確認なしで実行（危険）
    --dry-run       実際には実行せず、コマンドのみ表示

例:
    $0 backups/qrai_backup_20240610_143000.sql.gz
    $0 --list
    $0 --dry-run backups/qrai_backup_20240610_143000.sql.gz

EOF
}

# バックアップファイル一覧表示
list_backups() {
    echo "📁 利用可能なバックアップファイル:"
    echo

    if [ ! -d "$BACKUP_DIR" ]; then
        echo "❌ バックアップディレクトリが見つかりません: $BACKUP_DIR"
        exit 1
    fi

    # バックアップファイル検索
    BACKUP_FILES=$(find "$BACKUP_DIR" -name "qrai_backup_*.sql*" -type f | sort -r)

    if [ -z "$BACKUP_FILES" ]; then
        echo "⚠️  バックアップファイルが見つかりません"
        exit 1
    fi

    echo "ファイル名                        | サイズ  | 作成日時"
    echo "--------------------------------|---------|------------------"

    while IFS= read -r file; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            size=$(du -h "$file" | cut -f1)
            date=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$file" 2>/dev/null || stat -c "%y" "$file" 2>/dev/null | cut -d' ' -f1,2 | cut -d'.' -f1)
            printf "%-32s | %-7s | %s\n" "$filename" "$size" "$date"
        fi
    done <<< "$BACKUP_FILES"

    echo
    echo "💡 復旧するには:"
    echo "   $0 $BACKUP_DIR/[ファイル名]"
}

# 確認プロンプト
confirm_restore() {
    local backup_file="$1"

    echo "⚠️  データベース復旧の確認"
    echo
    echo "復旧対象:"
    echo "  - データベース: $DB_NAME@$DB_HOST:$DB_PORT"
    echo "  - バックアップファイル: $(basename "$backup_file")"
    echo "  - ファイルサイズ: $(du -h "$backup_file" | cut -f1)"
    echo
    echo "🚨 警告: 現在のデータベース内容は完全に置き換えられます！"
    echo
    read -p "続行しますか？ (yes/no): " confirm

    if [ "$confirm" != "yes" ]; then
        echo "❌ 復旧をキャンセルしました"
        exit 1
    fi
}

# データベース復旧実行
restore_database() {
    local backup_file="$1"
    local dry_run="$2"

    echo "🔄 データベース復旧を開始..."
    echo "バックアップファイル: $backup_file"

    # ファイル存在確認
    if [ ! -f "$backup_file" ]; then
        echo "❌ バックアップファイルが見つかりません: $backup_file"
        exit 1
    fi

    # 展開が必要かチェック
    if [[ "$backup_file" == *.gz ]]; then
        echo "📦 圧縮ファイルを展開中..."
        temp_file="/tmp/qrai_restore_$(date +%s).sql"

        if [ "$dry_run" = "true" ]; then
            echo "[DRY RUN] gunzip -c '$backup_file' > '$temp_file'"
        else
            gunzip -c "$backup_file" > "$temp_file"
        fi

        restore_file="$temp_file"
    else
        restore_file="$backup_file"
    fi

    # 復旧実行
    echo "🔨 データベースを復旧中..."

    if command -v docker &> /dev/null && docker ps | grep -q "qrai_postgres"; then
        # Docker環境の場合
        echo "Using Docker PostgreSQL container..."
        restore_cmd="docker exec -i qrai_postgres psql -h localhost -p 5432 -U '$DB_USER' -d postgres < '$restore_file'"
    else
        # ローカルPostgreSQLの場合
        echo "Using local PostgreSQL..."
        restore_cmd="PGPASSWORD='$POSTGRES_PASSWORD' psql -h '$DB_HOST' -p '$DB_PORT' -U '$DB_USER' -d postgres < '$restore_file'"
    fi

    if [ "$dry_run" = "true" ]; then
        echo "[DRY RUN] $restore_cmd"
    else
        if command -v docker &> /dev/null && docker ps | grep -q "qrai_postgres"; then
            docker exec -i qrai_postgres psql -h localhost -p 5432 -U "$DB_USER" -d postgres < "$restore_file"
        else
            PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres < "$restore_file"
        fi
    fi

    # 一時ファイル削除
    if [[ "$backup_file" == *.gz ]] && [ -f "$temp_file" ]; then
        if [ "$dry_run" = "true" ]; then
            echo "[DRY RUN] rm '$temp_file'"
        else
            rm "$temp_file"
        fi
    fi

    if [ "$dry_run" = "true" ]; then
        echo "🧪 DRY RUN 完了（実際の復旧は実行されませんでした）"
    else
        echo "✅ データベース復旧が完了しました！"
    fi
}

# オプション解析
DRY_RUN=false
SKIP_CONFIRM=false
BACKUP_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -l|--list)
            list_backups
            exit 0
            ;;
        -c|--confirm)
            SKIP_CONFIRM=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            if [ -z "$BACKUP_FILE" ]; then
                BACKUP_FILE="$1"
            else
                echo "❌ 複数のバックアップファイルが指定されました"
                show_help
                exit 1
            fi
            shift
            ;;
    esac
done

# 引数確認
if [ -z "$BACKUP_FILE" ]; then
    echo "❌ バックアップファイルが指定されていません"
    echo
    show_help
    exit 1
fi

# 確認プロンプト
if [ "$SKIP_CONFIRM" = "false" ] && [ "$DRY_RUN" = "false" ]; then
    confirm_restore "$BACKUP_FILE"
fi

# 復旧実行
restore_database "$BACKUP_FILE" "$DRY_RUN"
