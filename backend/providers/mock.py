"""
テスト用モックLLMプロバイダー
"""

from typing import AsyncGenerator, Optional
import asyncio
import structlog

from .base import ILLMProvider, LLMResponse, LLMError

logger = structlog.get_logger(__name__)


class MockLLMProvider(ILLMProvider):
    """テスト用モックLLMプロバイダー"""

    def __init__(self, api_key: str = "mock_key", **kwargs):
        super().__init__(api_key, **kwargs)
        self.fail_requests = kwargs.get("fail_requests", False)
        self.response_delay = kwargs.get("response_delay", 0.1)

    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def default_model(self) -> str:
        return "mock-model-v1"

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs,
    ) -> LLMResponse:
        """モックテキスト生成"""
        if self.fail_requests:
            raise LLMError("Mock provider failure")

        await asyncio.sleep(self.response_delay)

        # プロンプトに基づいた簡単な応答生成
        mock_content = f"これは「{prompt[:50]}...」に対するモック応答です。"

        return LLMResponse(
            content=mock_content,
            provider=self.provider_name,
            model=model or self.default_model,
            usage={
                "prompt_tokens": len(prompt),
                "completion_tokens": len(mock_content),
            },
            metadata={"mock": True, "response_id": "mock_123"},
        )

    async def stream_generate(  # type: ignore[override]
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """モックストリーミングテキスト生成"""
        if self.fail_requests:
            raise LLMError("Mock provider streaming failure")

        mock_content = (
            f"これは「{prompt[:30]}...」に対するストリーミングモック応答です。"
        )

        # 文字単位でストリーミング
        for char in mock_content:
            await asyncio.sleep(self.response_delay / len(mock_content))
            char_content: str = char
            yield char_content

    async def is_available(self) -> bool:
        """プロバイダーが利用可能かチェック"""
        return True  # モックは常に利用可能

    async def health_check(self) -> bool:
        """ヘルスチェック"""
        return await self.is_available()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
