"""
アプリケーション設定
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """アプリケーション設定"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # 未定義の環境変数を無視
    )

    # 基本設定
    debug: bool = Field(default=False, description="デバッグモード")
    environment: str = Field(
        default="development", description="環境", alias="ENVIRONMENT"
    )

    # データベース設定
    database_url: str = Field(
        default="sqlite+aiosqlite:///./app.db",
        description="データベース接続URL",
        alias="DATABASE_URL",
    )

    # LLM設定
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

    # API Keys
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

    # Azure Search
    azure_search_endpoint: str = Field(
        default="",
        description="Azure Search エンドポイント",
        alias="AZURE_SEARCH_ENDPOINT",
    )
    azure_search_api_key: str = Field(
        default="", description="Azure Search APIキー", alias="AZURE_SEARCH_API_KEY"
    )

    # ログ設定
    log_level: str = Field(default="INFO", description="ログレベル", alias="LOG_LEVEL")


def get_settings() -> Settings:
    """設定インスタンス取得（キャッシュ対応）"""
    return Settings()


# 設定インスタンス（後方互換性）
settings = get_settings()
