#!/bin/bash
set -euo pipefail

# QRAI LLMプロバイダー対応デプロイスクリプト
# =============================================
# Azure OpenAI依存を除去し、OpenRouter/Google AI Studio対応のインフラをデプロイします。

# スクリプト設定
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
LOG_FILE="${PROJECT_ROOT}/deploy-llm-${TIMESTAMP}.log"

# カラー出力設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ログ関数
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    case $level in
        "INFO")
            echo -e "${BLUE}[${timestamp}] ℹ️ ${message}${NC}" | tee -a "${LOG_FILE}"
            ;;
        "SUCCESS")
            echo -e "${GREEN}[${timestamp}] ✅ ${message}${NC}" | tee -a "${LOG_FILE}"
            ;;
        "WARNING")
            echo -e "${YELLOW}[${timestamp}] ⚠️ ${message}${NC}" | tee -a "${LOG_FILE}"
            ;;
        "ERROR")
            echo -e "${RED}[${timestamp}] ❌ ${message}${NC}" | tee -a "${LOG_FILE}"
            ;;
    esac
}

# エラーハンドリング
handle_error() {
    local exit_code=$?
    local line_number=$1
    log "ERROR" "スクリプトがライン ${line_number} でエラー終了しました (終了コード: ${exit_code})"
    log "ERROR" "詳細なログ: ${LOG_FILE}"
    exit $exit_code
}
trap 'handle_error $LINENO' ERR

# 使用方法表示
show_usage() {
    cat << EOF
QRAI LLMプロバイダー対応デプロイスクリプト
=====================================

使用方法:
    $0 [OPTIONS]

オプション:
    -h, --help              この使用方法を表示
    -e, --environment ENV   環境名 (dev|staging|prod) [デフォルト: dev]
    -r, --resource-group RG リソースグループ名
    -o, --openrouter-key KEY OpenRouter APIキー (必須)
    -g, --google-ai-key KEY  Google AI Studio APIキー (必須)
    -a, --azure-openai-key KEY Azure OpenAI APIキー (オプション)
    --azure-openai-endpoint URL Azure OpenAI エンドポイント (オプション)
    --dry-run               実際のデプロイを行わず、設定確認のみ
    --skip-tests            デプロイ後のテストをスキップ

例:
    # 基本的なデプロイ
    $0 -o "sk-or-v1-xxx" -g "AIzaSyxxx"

    # 本番環境デプロイ
    $0 -e prod -r qrai-prod-rg -o "sk-or-v1-xxx" -g "AIzaSyxxx"

    # 設定確認のみ
    $0 --dry-run -o "sk-or-v1-xxx" -g "AIzaSyxxx"

EOF
}

# デフォルト設定
ENVIRONMENT="dev"
RESOURCE_GROUP=""
OPENROUTER_API_KEY=""
GOOGLE_AI_API_KEY=""
AZURE_OPENAI_API_KEY=""
AZURE_OPENAI_ENDPOINT=""
DRY_RUN=false
SKIP_TESTS=false

# コマンドライン引数解析
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -r|--resource-group)
            RESOURCE_GROUP="$2"
            shift 2
            ;;
        -o|--openrouter-key)
            OPENROUTER_API_KEY="$2"
            shift 2
            ;;
        -g|--google-ai-key)
            GOOGLE_AI_API_KEY="$2"
            shift 2
            ;;
        -a|--azure-openai-key)
            AZURE_OPENAI_API_KEY="$2"
            shift 2
            ;;
        --azure-openai-endpoint)
            AZURE_OPENAI_ENDPOINT="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        *)
            log "ERROR" "不明なオプション: $1"
            show_usage
            exit 1
            ;;
    esac
done

# 必須パラメータチェック
if [[ -z "$OPENROUTER_API_KEY" ]]; then
    log "ERROR" "OpenRouter APIキーが必要です (-o オプション)"
    exit 1
fi

if [[ -z "$GOOGLE_AI_API_KEY" ]]; then
    log "ERROR" "Google AI Studio APIキーが必要です (-g オプション)"
    exit 1
fi

# 環境別設定
case $ENVIRONMENT in
    "dev")
        RESOURCE_GROUP="${RESOURCE_GROUP:-qrai-dev-rg}"
        LOCATION="westeurope"
        ;;
    "staging")
        RESOURCE_GROUP="${RESOURCE_GROUP:-qrai-staging-rg}"
        LOCATION="eastus2"
        ;;
    "prod")
        RESOURCE_GROUP="${RESOURCE_GROUP:-qrai-prod-rg}"
        LOCATION="eastus2"
        ;;
    *)
        log "ERROR" "不明な環境: $ENVIRONMENT (dev|staging|prod)"
        exit 1
        ;;
esac

# 初期化
log "INFO" "QRAI LLMプロバイダー対応デプロイ開始"
log "INFO" "環境: $ENVIRONMENT"
log "INFO" "リソースグループ: $RESOURCE_GROUP"
log "INFO" "ロケーション: $LOCATION"
log "INFO" "ログファイル: $LOG_FILE"

# Azure CLI ログイン確認
check_azure_login() {
    log "INFO" "Azure CLI認証確認中..."

    if ! az account show &>/dev/null; then
        log "ERROR" "Azure CLIにログインしていません"
        log "INFO" "以下のコマンドでログインしてください: az login"
        exit 1
    fi

    local subscription_name=$(az account show --query name -o tsv)
    local subscription_id=$(az account show --query id -o tsv)
    log "SUCCESS" "Azure ログイン確認完了"
    log "INFO" "サブスクリプション: $subscription_name ($subscription_id)"
}

# 必要なツール確認
check_dependencies() {
    log "INFO" "必要なツール確認中..."

    local missing_tools=()

    if ! command -v az &> /dev/null; then
        missing_tools+=("azure-cli")
    fi

    if ! command -v python3 &> /dev/null; then
        missing_tools+=("python3")
    fi

    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log "ERROR" "以下のツールがインストールされていません: ${missing_tools[*]}"
        exit 1
    fi

    log "SUCCESS" "必要なツール確認完了"
}

# リソースグループ作成/確認
ensure_resource_group() {
    log "INFO" "リソースグループ確認中: $RESOURCE_GROUP"

    if az group show --name "$RESOURCE_GROUP" &>/dev/null; then
        log "INFO" "リソースグループが既に存在します: $RESOURCE_GROUP"
    else
        log "INFO" "リソースグループを作成します: $RESOURCE_GROUP"
        if [[ "$DRY_RUN" == "false" ]]; then
            az group create \
                --name "$RESOURCE_GROUP" \
                --location "$LOCATION" \
                --tags \
                    Project=QRAI \
                    Environment="$ENVIRONMENT" \
                    ManagedBy=bicep \
                    LLMStrategy=multi-provider
            log "SUCCESS" "リソースグループ作成完了: $RESOURCE_GROUP"
        else
            log "INFO" "[DRY RUN] リソースグループ作成をスキップ"
        fi
    fi
}

# Key Vault アクセス権限用のオブジェクトID取得
get_keyvault_object_id() {
    log "INFO" "Key Vault アクセス権限用オブジェクトID取得中..."

    local object_id=$(az ad signed-in-user show --query id -o tsv)
    if [[ -z "$object_id" ]]; then
        log "ERROR" "オブジェクトID取得に失敗しました"
        exit 1
    fi

    log "SUCCESS" "オブジェクトID取得完了: $object_id"
    echo "$object_id"
}

# APIキー設定確認
validate_api_keys() {
    log "INFO" "APIキー設定確認中..."

    # OpenRouter APIキー確認
    if [[ ${#OPENROUTER_API_KEY} -lt 50 ]]; then
        log "WARNING" "OpenRouter APIキーが短すぎる可能性があります"
    fi

    # Google AI APIキー確認
    if [[ ${#GOOGLE_AI_API_KEY} -lt 30 ]]; then
        log "WARNING" "Google AI Studio APIキーが短すぎる可能性があります"
    fi

    # APIキー接続テスト (オプション)
    if command -v python3 &> /dev/null && [[ "$DRY_RUN" == "false" ]]; then
        log "INFO" "APIキー接続テスト実行中..."
        if python3 "${SCRIPT_DIR}/check_llm_config.py" --provider openrouter; then
            log "SUCCESS" "OpenRouter接続確認完了"
        else
            log "WARNING" "OpenRouter接続テストに失敗しました"
        fi
    fi

    log "SUCCESS" "APIキー設定確認完了"
}

# Bicepデプロイ実行
deploy_infrastructure() {
    log "INFO" "インフラストラクチャデプロイ開始..."

    local object_id=$(get_keyvault_object_id)
    local bicep_file="${PROJECT_ROOT}/infra/bicep/main.bicep"
    local param_file="${PROJECT_ROOT}/infra/bicep/main.bicepparam"

    if [[ ! -f "$bicep_file" ]]; then
        log "ERROR" "Bicepテンプレートが見つかりません: $bicep_file"
        exit 1
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        log "INFO" "[DRY RUN] Bicepデプロイをスキップ"
        log "INFO" "デプロイ設定:"
        log "INFO" "  テンプレート: $bicep_file"
        log "INFO" "  パラメータ: $param_file"
        log "INFO" "  OpenRouter APIキー: ${OPENROUTER_API_KEY:0:10}..."
        log "INFO" "  Google AI APIキー: ${GOOGLE_AI_API_KEY:0:10}..."
        return
    fi

    # デプロイ実行
    local deployment_name="qrai-llm-deploy-${TIMESTAMP}"

    log "INFO" "Bicepデプロイ実行中... (デプロイ名: $deployment_name)"

    az deployment group create \
        --resource-group "$RESOURCE_GROUP" \
        --template-file "$bicep_file" \
        --parameters "@${param_file}" \
        --parameters \
            keyVaultAccessObjectId="$object_id" \
            openRouterApiKey="$OPENROUTER_API_KEY" \
            googleAiApiKey="$GOOGLE_AI_API_KEY" \
            azureOpenAiApiKey="$AZURE_OPENAI_API_KEY" \
            azureOpenAiEndpoint="$AZURE_OPENAI_ENDPOINT" \
        --name "$deployment_name" \
        --verbose

    log "SUCCESS" "Bicepデプロイ完了"

    # デプロイ結果取得
    local outputs=$(az deployment group show \
        --resource-group "$RESOURCE_GROUP" \
        --name "$deployment_name" \
        --query 'properties.outputs' \
        -o json)

    log "INFO" "デプロイ結果:"
    echo "$outputs" | jq -r 'to_entries[] | "  \(.key): \(.value.value)"' | while read -r line; do
        log "INFO" "$line"
    done
}

# デプロイ後テスト
run_post_deploy_tests() {
    if [[ "$SKIP_TESTS" == "true" ]]; then
        log "INFO" "デプロイ後テストをスキップしました"
        return
    fi

    log "INFO" "デプロイ後テスト実行中..."

    # 環境変数設定
    export OPENROUTER_API_KEY="$OPENROUTER_API_KEY"
    export GOOGLE_AI_API_KEY="$GOOGLE_AI_API_KEY"
    if [[ -n "$AZURE_OPENAI_API_KEY" ]]; then
        export AZURE_OPENAI_API_KEY="$AZURE_OPENAI_API_KEY"
        export AZURE_OPENAI_ENDPOINT="$AZURE_OPENAI_ENDPOINT"
    fi

    # 基本接続テスト
    if python3 "${SCRIPT_DIR}/check_llm_config.py"; then
        log "SUCCESS" "LLMプロバイダー接続テスト完了"
    else
        log "WARNING" "LLMプロバイダー接続テストに失敗しました"
    fi

    # 詳細テスト（オプション）
    if python3 "${SCRIPT_DIR}/test_llm_providers.py" --test chat; then
        log "SUCCESS" "詳細テスト完了"
    else
        log "WARNING" "詳細テストに失敗しました"
    fi
}

# クリーンアップ関数
cleanup() {
    log "INFO" "クリーンアップ実行中..."
    # 必要に応じてクリーンアップ処理を追加
}

# メイン処理
main() {
    log "INFO" "=== QRAI LLMプロバイダー対応デプロイ開始 ==="

    # 事前確認
    check_dependencies
    check_azure_login
    validate_api_keys

    # インフラデプロイ
    ensure_resource_group
    deploy_infrastructure

    # 事後テスト
    run_post_deploy_tests

    log "SUCCESS" "=== デプロイ完了 ==="
    log "INFO" "詳細ログ: $LOG_FILE"

    # 次のステップ表示
    cat << EOF

🎉 QRAI LLMプロバイダー対応デプロイが完了しました！

次のステップ:
1. 環境変数設定: docs/environment_setup.md を参照
2. LangChain設定: config/llm_providers.yml を確認
3. 動作確認: python scripts/check_llm_config.py
4. 詳細テスト: python scripts/test_llm_providers.py

設定ファイル:
- Bicep: infra/bicep/main.bicep
- LLM設定: config/llm_providers.yml
- 環境変数: .env (作成が必要)

ドキュメント:
- 環境設定: docs/environment_setup.md
- アーキテクチャ: docs/architecture/component_api.md
- ADR: docs/adr/0007-llm-provider-abstraction.md

EOF
}

# トラップ設定
trap cleanup EXIT

# メイン処理実行
main "$@"
