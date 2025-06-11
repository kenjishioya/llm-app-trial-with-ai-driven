"""
テスト用LLMモック実装
"""

from typing import AsyncGenerator, Optional, Dict, Any
from unittest.mock import AsyncMock


class MockLLMResponse:
    """モックLLMレスポンス"""

    def __init__(
        self,
        content: str = "これはテスト用のモック回答です。",
        provider: str = "mock",
        model: str = "mock-model-v1",
        usage: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.content = content
        self.provider = provider
        self.model = model
        self.usage = usage or {"prompt_tokens": 10, "completion_tokens": 20}
        self.metadata = metadata or {"mock": True, "test_id": "test_123"}


class MockLLMService:
    """テスト用LLMサービスモック"""

    def __init__(
        self, fixed_response: Optional[str] = None, response_delay: float = 0.1
    ):
        self.fixed_response = fixed_response or "これはテスト用のモック回答です。"
        self.response_delay = response_delay
        self.call_count = 0
        self.last_prompt: str = ""  # Noneの代わりに空文字列を初期値に
        self.provider = None

    async def generate_response(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> MockLLMResponse:
        """モック回答生成"""
        self.call_count += 1
        self.last_prompt = prompt

        # プロンプトに基づいた動的回答（テスト用）
        if "こんにちは" in prompt:
            content = "こんにちは！元気です。テスト用の回答です。"
        elif "質問" in prompt or "?" in prompt or "？" in prompt:
            content = f"「{prompt[:30]}...」への回答: これはテスト用のモック回答です。"
        else:
            content = self.fixed_response

        return MockLLMResponse(
            content=content,
            provider="mock",
            model="mock-test-model",
            usage={
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(content.split()),
            },
            metadata={
                "mock": True,
                "call_count": self.call_count,
                "test_prompt": prompt[:50],
            },
        )

    async def stream_response(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> AsyncGenerator[MockLLMResponse, None]:
        """モックストリーミング回答"""
        response = await self.generate_response(
            prompt, system_message, max_tokens, temperature
        )

        # 文字単位でストリーミングをシミュレート
        words = response.content.split()
        for i, word in enumerate(words):
            chunk_content = word + (" " if i < len(words) - 1 else "")
            yield MockLLMResponse(
                content=chunk_content,
                provider=response.provider,
                model=response.model,
                usage=response.usage,
                metadata={
                    **response.metadata,
                    "chunk": i + 1,
                    "total_chunks": len(words),
                },
            )

    async def health_check(self) -> bool:
        """モックヘルスチェック"""
        return True

    def get_provider_info(self) -> Dict[str, Any]:
        """モックプロバイダー情報"""
        return {
            "provider": "MockLLMService",
            "available": True,
            "call_count": self.call_count,
            "last_prompt": self.last_prompt,
        }


def create_mock_llm_service(fixed_response: Optional[str] = None) -> MockLLMService:
    """テスト用LLMサービスモックを作成"""
    return MockLLMService(fixed_response)


def create_async_mock(**kwargs) -> AsyncMock:
    """非同期関数用のモックを作成"""
    mock = AsyncMock(**kwargs)
    return mock


# pytest用のフィクスチャヘルパー
async def mock_generate_response(prompt: str, **kwargs) -> MockLLMResponse:
    """pytest用のモック関数"""
    service = create_mock_llm_service()
    return await service.generate_response(prompt, **kwargs)


async def mock_stream_response(
    prompt: str, **kwargs
) -> AsyncGenerator[MockLLMResponse, None]:
    """pytest用のストリーミングモック関数"""
    service = create_mock_llm_service()
    async for chunk in service.stream_response(prompt, **kwargs):
        yield chunk
