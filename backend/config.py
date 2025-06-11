"""
Phase 1.5 環境設定検証機能付きアプリケーション設定
"""

import logging
from typing import List, Dict, Any
from urllib.parse import urlparse
from pydantic import Field, validator, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    環境変数検証機能付きアプリケーション設定
    Phase 1.5D2: 設定検証機能実装
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # 未定義の環境変数を無視
    )

    # =============================================================================
    # 基本設定
    # =============================================================================
    app_name: str = Field(
        default="QRAI", description="アプリケーション名", alias="APP_NAME"
    )
    app_version: str = Field(
        default="1.5.0", description="アプリケーションバージョン", alias="APP_VERSION"
    )
    debug: bool = Field(default=False, description="デバッグモード")
    environment: str = Field(
        default="development", description="環境識別子", alias="ENVIRONMENT"
    )

    # サーバー設定
    host: str = Field(default="0.0.0.0", description="ホストアドレス", alias="HOST")
    port: int = Field(default=8000, description="ポート番号", alias="PORT")
    reload: bool = Field(default=True, description="自動リロード", alias="RELOAD")

    # =============================================================================
    # データベース設定
    # =============================================================================
    database_url: str = Field(
        default="sqlite+aiosqlite:///./app.db",
        description="データベース接続URL",
        alias="DATABASE_URL",
    )
    db_pool_size: int = Field(
        default=10, description="データベース接続プールサイズ", alias="DB_POOL_SIZE"
    )
    db_max_overflow: int = Field(
        default=30, description="最大接続数", alias="DB_MAX_OVERFLOW"
    )
    db_pool_timeout: int = Field(
        default=30, description="接続タイムアウト", alias="DB_POOL_TIMEOUT"
    )
    sql_debug: bool = Field(
        default=False, description="SQLデバッグ出力", alias="SQL_DEBUG"
    )

    # =============================================================================
    # LLM API設定
    # =============================================================================
    llm_primary_provider: str = Field(
        default="openrouter",
        description="主要LLMプロバイダ",
        alias="LLM_PRIMARY_PROVIDER",
    )
    llm_fallback_providers: str = Field(
        default="google_ai,azure_openai",
        description="フォールバックLLMプロバイダ",
        alias="LLM_FALLBACK_PROVIDERS",
    )
    llm_request_timeout: int = Field(
        default=60, description="LLMリクエストタイムアウト", alias="LLM_REQUEST_TIMEOUT"
    )
    llm_max_retries: int = Field(
        default=3, description="最大リトライ回数", alias="LLM_MAX_RETRIES"
    )
    llm_rate_limit_per_minute: int = Field(
        default=60,
        description="1分あたりのレート制限",
        alias="LLM_RATE_LIMIT_PER_MINUTE",
    )

    # =============================================================================
    # API Keys
    # =============================================================================
    openrouter_api_key: str = Field(
        default="", description="OpenRouter APIキー", alias="OPENROUTER_API_KEY"
    )
    google_ai_api_key: str = Field(
        default="", description="Google AI APIキー", alias="GOOGLE_AI_API_KEY"
    )
    azure_openai_api_key: str = Field(
        default="", description="Azure OpenAI APIキー", alias="AZURE_OPENAI_API_KEY"
    )
    azure_openai_endpoint: str = Field(
        default="",
        description="Azure OpenAI エンドポイント",
        alias="AZURE_OPENAI_ENDPOINT",
    )
    azure_openai_api_version: str = Field(
        default="2024-05-01-preview",
        description="Azure OpenAI APIバージョン",
        alias="AZURE_OPENAI_API_VERSION",
    )

    # =============================================================================
    # Azure Services
    # =============================================================================
    azure_search_endpoint: str = Field(
        default="",
        description="Azure Search エンドポイント",
        alias="AZURE_SEARCH_ENDPOINT",
    )
    azure_search_api_key: str = Field(
        default="", description="Azure Search APIキー", alias="AZURE_SEARCH_API_KEY"
    )
    azure_search_index_name: str = Field(
        default="qrai-knowledge-base",
        description="Azure Search インデックス名",
        alias="AZURE_SEARCH_INDEX_NAME",
    )

    # Azure Key Vault
    azure_keyvault_url: str = Field(
        default="",
        description="Azure Key Vault URL",
        alias="AZURE_KEYVAULT_URL",
    )
    azure_client_id: str = Field(
        default="",
        description="Azure Client ID",
        alias="AZURE_CLIENT_ID",
    )
    azure_client_secret: str = Field(
        default="",
        description="Azure Client Secret",
        alias="AZURE_CLIENT_SECRET",
    )
    azure_tenant_id: str = Field(
        default="",
        description="Azure Tenant ID",
        alias="AZURE_TENANT_ID",
    )

    # =============================================================================
    # セキュリティ設定
    # =============================================================================
    jwt_secret_key: str = Field(
        default="dev-jwt-secret-change-in-production",
        description="JWT署名キー",
        alias="JWT_SECRET_KEY",
    )
    jwt_algorithm: str = Field(
        default="HS256", description="JWTアルゴリズム", alias="JWT_ALGORITHM"
    )
    jwt_expire_minutes: int = Field(
        default=60, description="JWT有効期限（分）", alias="JWT_EXPIRE_MINUTES"
    )
    session_secret_key: str = Field(
        default="dev-session-secret-change-in-production",
        description="セッション署名キー",
        alias="SESSION_SECRET_KEY",
    )

    # =============================================================================
    # CORS・ネットワーク設定
    # =============================================================================
    allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        description="許可するCORSオリジン",
        alias="ALLOWED_ORIGINS",
    )
    frontend_url: str = Field(
        default="http://localhost:3000",
        description="フロントエンドURL",
        alias="FRONTEND_URL",
    )
    backend_url: str = Field(
        default="http://localhost:8000",
        description="バックエンドURL",
        alias="BACKEND_URL",
    )

    # =============================================================================
    # ログ・監視設定
    # =============================================================================
    log_level: str = Field(default="INFO", description="ログレベル", alias="LOG_LEVEL")
    azure_application_insights_connection_string: str = Field(
        default="",
        description="Application Insights接続文字列",
        alias="AZURE_APPLICATION_INSIGHTS_CONNECTION_STRING",
    )
    enable_profiling: bool = Field(
        default=False, description="プロファイリング有効化", alias="ENABLE_PROFILING"
    )

    # =============================================================================
    # パフォーマンス・キャッシュ設定
    # =============================================================================
    cache_ttl_seconds: int = Field(
        default=3600, description="キャッシュTTL", alias="CACHE_TTL_SECONDS"
    )
    cache_max_size: int = Field(
        default=1000, description="キャッシュ最大サイズ", alias="CACHE_MAX_SIZE"
    )

    # =============================================================================
    # バリデーター
    # =============================================================================

    @validator("environment")
    def validate_environment(cls, v):
        """環境識別子の検証"""
        valid_environments = ["development", "test", "staging", "production"]
        if v not in valid_environments:
            raise ValueError(
                f"環境は {valid_environments} のいずれかである必要があります"
            )
        return v

    @validator("database_url")
    def validate_database_url(cls, v):
        """データベースURL形式の検証"""
        if not v:
            raise ValueError("DATABASE_URLは必須です")

        valid_schemes = ["postgresql+asyncpg", "sqlite+aiosqlite", "mysql+aiomysql"]

        if not any(v.startswith(scheme) for scheme in valid_schemes):
            raise ValueError(
                f"データベースURLは {valid_schemes} のいずれかで始まる必要があります"
            )

        return v

    @validator("openrouter_api_key")
    def validate_openrouter_key(cls, v, values):
        """OpenRouter APIキーの検証"""
        if values.get("environment") == "production" and not v:
            raise ValueError("本番環境ではOpenRouter APIキーが必須です")

        if v and not v.startswith("sk-or-v1-"):
            logger.warning("OpenRouter APIキーの形式が正しくない可能性があります")

        return v

    @validator("google_ai_api_key")
    def validate_google_ai_key(cls, v):
        """Google AI APIキーの検証"""
        if v and not v.startswith("AIzaSy"):
            logger.warning("Google AI APIキーの形式が正しくない可能性があります")

        return v

    @validator("azure_openai_endpoint", "azure_search_endpoint", "azure_keyvault_url")
    def validate_azure_urls(cls, v):
        """Azure URLの検証"""
        if v and not v.startswith("https://"):
            raise ValueError("Azure URLはHTTPSで始まる必要があります")

        return v

    @validator("log_level")
    def validate_log_level(cls, v):
        """ログレベルの検証"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(
                f"ログレベルは {valid_levels} のいずれかである必要があります"
            )

        return v.upper()

    @validator("port")
    def validate_port(cls, v):
        """ポート番号の検証"""
        if not 1 <= v <= 65535:
            raise ValueError("ポート番号は1-65535の範囲である必要があります")

        return v

    @validator("jwt_secret_key", "session_secret_key")
    def validate_secret_keys(cls, v, values):
        """シークレットキーの強度検証"""
        environment = values.get("environment", "development")

        if environment == "production":
            if len(v) < 32:
                raise ValueError("本番環境では32文字以上のシークレットキーが必要です")

            if v in [
                "dev-jwt-secret-change-in-production",
                "dev-session-secret-change-in-production",
            ]:
                raise ValueError(
                    "本番環境ではデフォルトのシークレットキーは使用できません"
                )

        return v

    # =============================================================================
    # ヘルパーメソッド
    # =============================================================================

    def get_allowed_origins_list(self) -> List[str]:
        """CORS許可オリジンをリストで取得"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    def get_fallback_providers_list(self) -> List[str]:
        """フォールバックプロバイダーをリストで取得"""
        return [provider.strip() for provider in self.llm_fallback_providers.split(",")]

    def is_production(self) -> bool:
        """本番環境かどうか判定"""
        return self.environment == "production"

    def is_development(self) -> bool:
        """開発環境かどうか判定"""
        return self.environment == "development"

    def is_test(self) -> bool:
        """テスト環境かどうか判定"""
        return self.environment == "test"

    def get_database_info(self) -> Dict[str, Any]:
        """データベース接続情報を取得"""
        parsed = urlparse(self.database_url)
        return {
            "scheme": parsed.scheme,
            "hostname": parsed.hostname,
            "port": parsed.port,
            "database": parsed.path.lstrip("/") if parsed.path else None,
            "username": parsed.username,
        }

    def validate_api_keys(self) -> Dict[str, bool]:
        """APIキーの設定状況を確認"""
        return {
            "openrouter": bool(self.openrouter_api_key),
            "google_ai": bool(self.google_ai_api_key),
            "azure_openai": bool(
                self.azure_openai_api_key and self.azure_openai_endpoint
            ),
            "azure_search": bool(
                self.azure_search_api_key and self.azure_search_endpoint
            ),
            "azure_keyvault": bool(self.azure_keyvault_url),
        }


def validate_environment() -> Settings:
    """
    環境設定の検証とインスタンス作成

    Returns:
        Settings: 検証済み設定インスタンス

    Raises:
        ValidationError: 設定検証エラー
        EnvironmentError: 環境エラー
    """
    try:
        settings = Settings()

        # 基本検証
        logger.info(f"🔧 環境設定検証開始: {settings.environment}")
        logger.info(f"📊 アプリケーション: {settings.app_name} v{settings.app_version}")

        # データベース接続確認
        db_info = settings.get_database_info()
        logger.info(f"💾 データベース: {db_info['scheme']} ({db_info['hostname']})")

        # APIキー設定確認
        api_status = settings.validate_api_keys()
        configured_apis = [api for api, status in api_status.items() if status]
        logger.info(f"🔑 API設定済み: {', '.join(configured_apis)}")

        # 本番環境特別チェック
        if settings.is_production():
            logger.info("🚀 本番環境設定検証中...")

            # 必須APIキーチェック
            if not settings.openrouter_api_key:
                raise EnvironmentError("本番環境ではOpenRouter APIキーが必須です")

            # セキュリティチェック
            if settings.debug:
                logger.warning("⚠️  本番環境でデバッグモードが有効です")

            if "localhost" in settings.allowed_origins:
                logger.warning("⚠️  本番環境でlocalhostが許可されています")

        # 開発環境推奨設定チェック
        elif settings.is_development():
            logger.info("🛠️  開発環境設定確認")

            if not any(api_status.values()):
                logger.warning(
                    "⚠️  APIキーが設定されていません（開発用モックが使用されます）"
                )

        logger.info("✅ 環境設定検証完了")
        return settings

    except ValidationError as e:
        logger.error("❌ 環境設定検証エラー:")
        for error in e.errors():
            field = error["loc"][0] if error["loc"] else "unknown"
            message = error["msg"]
            logger.error(f"  - {field}: {message}")
        raise

    except Exception as e:
        logger.error(f"❌ 環境設定エラー: {str(e)}")
        raise


def get_settings() -> Settings:
    """設定インスタンス取得（キャッシュ対応）"""
    return validate_environment()


# 設定インスタンス（後方互換性）
settings = validate_environment()
