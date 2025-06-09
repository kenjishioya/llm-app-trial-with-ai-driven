"""
LLM プロバイダー ファクトリ
"""

from typing import Optional, List
from .base import ILLMProvider
from config import settings  # type: ignore[attr-defined]
from .mock import MockLLMProvider
from .openrouter import OpenRouterProvider
from .google_ai import GoogleAIProvider


class LLMProviderFactory:
    """LLM プロバイダー ファクトリ"""

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
            return None

        provider_class = cls._providers[provider_name]

        # プロバイダー固有の設定
        if provider_name == "mock":
            return provider_class()
        elif provider_name == "openrouter":
            return provider_class(
                api_key=settings.openrouter_api_key,
                base_url="https://openrouter.ai/api/v1",
            )
        elif provider_name == "google_ai":
            return provider_class(api_key=settings.google_ai_api_key)

        return None

    @classmethod
    def get_available_provider(cls) -> Optional[str]:
        """利用可能な最初のプロバイダーを取得（優先順位順）"""
        # 優先順位: primary -> fallbacks -> mock
        primary = settings.llm_primary_provider
        fallbacks = settings.llm_fallback_providers.split(",")

        # プライマリプロバイダーをチェック
        if primary in cls._providers:
            provider = cls.create_provider(primary)
            if provider and cls._is_provider_available(provider, primary):
                return primary

        # フォールバックプロバイダーをチェック
        for fallback in fallbacks:
            fallback = fallback.strip()
            if fallback in cls._providers:
                provider = cls.create_provider(fallback)
                if provider and cls._is_provider_available(provider, fallback):
                    return fallback

        # 最後にモックプロバイダー
        if "mock" in cls._providers:
            return "mock"

        return None

    @classmethod
    def _is_provider_available(cls, provider: ILLMProvider, provider_name: str) -> bool:
        """プロバイダーが利用可能かチェック"""
        if provider_name == "mock":
            return True

        # 実際のプロバイダーの場合、APIキーが設定されているかチェック
        if provider_name == "openrouter":
            return bool(settings.openrouter_api_key)
        elif provider_name == "google_ai":
            return bool(settings.google_ai_api_key)

        return False

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
