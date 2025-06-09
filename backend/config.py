"""
アプリケーション設定
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """アプリケーション設定"""

    model_config = SettingsConfigDict(
        env_prefix="QRAI_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # 基本設定
    debug: bool = Field(default=False, description="デバッグモード")
    env: str = Field(default="development", description="環境")

    # データベース設定
    database_url: str = Field(description="データベース接続URL")

    # LLM設定
    llm_primary_provider: str = Field(
        default="openrouter", description="主要LLMプロバイダ"
    )
    llm_fallback_providers: str = Field(
        default="google_ai,azure_openai", description="フォールバックLLMプロバイダ"
    )

    # API Keys
    openrouter_api_key: str = Field(default="", description="OpenRouter APIキー")
    google_ai_api_key: str = Field(default="", description="Google AI APIキー")
    azure_openai_api_key: str = Field(default="", description="Azure OpenAI APIキー")
    azure_openai_endpoint: str = Field(
        default="", description="Azure OpenAI エンドポイント"
    )

    # Azure Search
    azure_search_endpoint: str = Field(
        default="", description="Azure Search エンドポイント"
    )
    azure_search_api_key: str = Field(default="", description="Azure Search APIキー")


# 設定インスタンス
settings = Settings()
