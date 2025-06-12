"""
LLMサービス
"""

from typing import Optional, AsyncGenerator, Dict, Any
from providers import LLMProviderFactory, ILLMProvider, LLMResponse, LLMError


class LLMService:
    """LLMサービス"""

    def __init__(self) -> None:
        self.provider: Optional[ILLMProvider] = None
        self._initialize_provider()

    def _initialize_provider(self) -> None:
        """プロバイダーを初期化"""
        provider_name = LLMProviderFactory.get_available_provider()
        if provider_name:
            self.provider = LLMProviderFactory.create_provider(provider_name)

    async def generate_response(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """レスポンスを生成"""
        if not self.provider:
            raise LLMError("No LLM provider available")

        return await self.provider.generate(
            prompt=prompt,
            system_message=system_message,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    async def stream_response(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> AsyncGenerator[LLMResponse, None]:
        """ストリーミングレスポンスを生成"""
        if not self.provider:
            raise LLMError("No LLM provider available")

        stream_gen = self.provider.stream(
            prompt=prompt,
            system_message=system_message,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        async for chunk in stream_gen:
            yield chunk

    async def health_check(self) -> bool:
        """ヘルスチェック"""
        if not self.provider:
            return False

        try:
            return await self.provider.health_check()
        except Exception:
            return False

    def get_provider_info(self) -> Dict[str, Any]:
        """プロバイダー情報を取得"""
        if not self.provider:
            return {"provider": None, "available": False}

        return {"provider": self.provider.__class__.__name__, "available": True}
