"""
LLM プロバイダー ファクトリ
"""

from typing import Optional, List, Dict, Any
import asyncio
import structlog
from .base import ILLMProvider
from config import settings  # type: ignore[attr-defined]
from .mock import MockLLMProvider
from .openrouter import OpenRouterProvider
from .google_ai import GoogleAIProvider

logger = structlog.get_logger(__name__)


class LLMProviderFactory:
    """LLM プロバイダー ファクトリ - 拡張版"""

    _providers = {
        "mock": MockLLMProvider,
        "openrouter": OpenRouterProvider,
        "google_ai": GoogleAIProvider,
    }

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """利用可能なプロバイダー一覧を取得"""
        return list(cls._providers.keys())

    @classmethod
    def create_provider(cls, provider_name: str) -> Optional[ILLMProvider]:
        """指定されたプロバイダーのインスタンスを作成"""
        if provider_name not in cls._providers:
            logger.warning("Unknown provider requested", provider=provider_name)
            return None

        provider_class = cls._providers[provider_name]

        try:
            # プロバイダー固有の設定
            if provider_name == "mock":
                mock_provider: ILLMProvider = provider_class()
                return mock_provider
            elif provider_name == "openrouter":
                if not settings.openrouter_api_key:
                    logger.warning("OpenRouter API key not configured")
                    return None
                openrouter_provider: ILLMProvider = provider_class(
                    api_key=settings.openrouter_api_key,
                    base_url="https://openrouter.ai/api/v1",
                )
                return openrouter_provider
            elif provider_name == "google_ai":
                if not settings.google_ai_api_key:
                    logger.warning("Google AI API key not configured")
                    return None
                google_provider: ILLMProvider = provider_class(
                    api_key=settings.google_ai_api_key
                )
                return google_provider

        except Exception as e:
            logger.error(
                "Failed to create provider", provider=provider_name, error=str(e)
            )
            return None

        return None

    @classmethod
    async def get_healthy_provider(cls) -> Optional[ILLMProvider]:
        """ヘルスチェック済みの利用可能なプロバイダーを取得"""
        provider_names = cls._get_provider_priority_order()

        for provider_name in provider_names:
            try:
                provider = cls.create_provider(provider_name)
                if provider and await cls._health_check_provider(provider):
                    logger.info("Selected healthy provider", provider=provider_name)
                    return provider
                else:
                    logger.warning(
                        "Provider health check failed", provider=provider_name
                    )
            except Exception as e:
                logger.error(
                    "Provider initialization failed",
                    provider=provider_name,
                    error=str(e),
                )
                continue

        logger.error("No healthy providers available, falling back to mock")
        return MockLLMProvider()

    @classmethod
    def get_available_provider(cls) -> Optional[str]:
        """利用可能な最初のプロバイダーを取得（優先順位順）"""
        provider_names = cls._get_provider_priority_order()

        for provider_name in provider_names:
            provider = cls.create_provider(provider_name)
            if provider and cls._is_provider_available(provider, provider_name):
                logger.info("Selected available provider", provider=provider_name)
                return provider_name

        logger.warning("No providers available, falling back to mock")
        return "mock"

    @classmethod
    def _get_provider_priority_order(cls) -> List[str]:
        """プロバイダーの優先順位リストを取得"""
        order = []

        # プライマリプロバイダー
        primary = settings.llm_primary_provider.strip().lower()
        if primary in cls._providers:
            order.append(primary)

        # フォールバックプロバイダー
        fallbacks = [
            f.strip().lower() for f in settings.llm_fallback_providers.split(",")
        ]
        for fallback in fallbacks:
            if fallback in cls._providers and fallback not in order:
                order.append(fallback)

        # 最後にモック（開発環境用）
        if "mock" not in order:
            order.append("mock")

        return order

    @classmethod
    async def _health_check_provider(cls, provider: ILLMProvider) -> bool:
        """プロバイダーのヘルスチェック"""
        try:
            # タイムアウト付きでヘルスチェック実行
            health_result = await asyncio.wait_for(provider.health_check(), timeout=5.0)
            return (
                health_result.get("status") == "ok"
                if isinstance(health_result, dict)
                else False
            )
        except asyncio.TimeoutError:
            logger.warning("Provider health check timeout")
            return False
        except Exception as e:
            logger.warning("Provider health check failed", error=str(e))
            return False

    @classmethod
    def _is_provider_available(
        cls, provider: Optional[ILLMProvider], provider_name: str
    ) -> bool:
        """プロバイダーが利用可能かチェック"""
        if not provider:
            return False

        if provider_name == "mock":
            return True

        # 実際のプロバイダーの場合、APIキーが設定されているかチェック
        if provider_name == "openrouter":
            return bool(settings.openrouter_api_key)
        elif provider_name == "google_ai":
            return bool(settings.google_ai_api_key)

        return False

    @classmethod
    def get_provider_config(cls) -> Dict[str, Any]:
        """プロバイダー設定の詳細情報を取得"""
        return {
            "primary_provider": settings.llm_primary_provider,
            "fallback_providers": settings.llm_fallback_providers.split(","),
            "available_providers": cls.get_available_providers(),
            "priority_order": cls._get_provider_priority_order(),
            "provider_status": {
                name: cls._is_provider_available(cls.create_provider(name), name)
                for name in cls._providers.keys()
            },
        }

    @staticmethod
    def create_providers() -> List[ILLMProvider]:
        """設定に基づいてプロバイダーリストを作成"""
        providers: List[ILLMProvider] = []

        # プライマリプロバイダー
        primary = settings.llm_primary_provider.lower()
        if primary == "openrouter" and settings.openrouter_api_key:
            providers.append(
                OpenRouterProvider(
                    api_key=settings.openrouter_api_key,
                    base_url="https://openrouter.ai/api/v1",
                )
            )
        elif primary == "google_ai" and settings.google_ai_api_key:
            providers.append(GoogleAIProvider(settings.google_ai_api_key))

        # フォールバックプロバイダー
        fallbacks = settings.llm_fallback_providers.split(",")
        for fallback in fallbacks:
            fallback = fallback.strip().lower()
            if fallback == "google_ai" and settings.google_ai_api_key:
                providers.append(GoogleAIProvider(settings.google_ai_api_key))
            elif fallback == "openrouter" and settings.openrouter_api_key:
                providers.append(
                    OpenRouterProvider(
                        api_key=settings.openrouter_api_key,
                        base_url="https://openrouter.ai/api/v1",
                    )
                )

        # フォールバック: モックプロバイダー
        if not providers:
            providers.append(MockLLMProvider())

        return providers
