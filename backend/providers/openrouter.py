"""
OpenRouter LLMプロバイダー実装
"""

import httpx
from typing import AsyncGenerator, Optional
import json
import structlog

from .base import ILLMProvider, LLMResponse, LLMError

logger = structlog.get_logger(__name__)


class OpenRouterProvider(ILLMProvider):
    """OpenRouter LLMプロバイダー"""

    def __init__(self, api_key: str, base_url: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://qrai.app",  # OpenRouter要件
                "X-Title": "QRAI MVP",
            },
            timeout=30.0,
        )

    @property
    def provider_name(self) -> str:
        return "openrouter"

    @property
    def default_model(self) -> str:
        return "anthropic/claude-3-haiku"

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs,
    ) -> LLMResponse:
        """テキスト生成"""
        try:
            payload = {
                "model": model or self.default_model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens or 1000,
                "temperature": temperature or 0.7,
                "stream": False,
            }

            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()

            data = response.json()
            content = data["choices"][0]["message"]["content"]

            return LLMResponse(
                content=content,
                provider=self.provider_name,
                model=model or self.default_model,
                usage=data.get("usage"),
                metadata={"response_id": data.get("id")},
            )

        except httpx.HTTPStatusError as e:
            logger.error(
                "OpenRouter HTTP error",
                status_code=e.response.status_code,
                response=e.response.text,
            )
            raise LLMError(f"OpenRouter API error: {e.response.status_code}")
        except Exception as e:
            logger.error("OpenRouter unexpected error", error=str(e))
            raise LLMError(f"OpenRouter error: {str(e)}")

    async def stream(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs,
    ) -> AsyncGenerator[LLMResponse, None]:
        """ストリーミングレスポンス生成（LLMServiceインターフェース準拠）"""
        try:
            # システムメッセージと組み合わせたメッセージリスト作成
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": model or self.default_model,
                "messages": messages,
                "max_tokens": max_tokens or 1000,
                "temperature": temperature or 0.7,
                "stream": True,
            }

            async with self.client.stream(
                "POST", "/chat/completions", json=payload
            ) as response:
                response.raise_for_status()

                full_content = ""
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]  # "data: " を除去
                        if data_str.strip() == "[DONE]":
                            break

                        try:
                            data = json.loads(data_str)
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    content: str = delta["content"]
                                    full_content += content

                                    # LLMResponseとして返却
                                    yield LLMResponse(
                                        content=content,
                                        provider=self.provider_name,
                                        model=model or self.default_model,
                                        usage=None,  # ストリーミング中は使用量不明
                                        metadata={"chunk": True},
                                    )
                        except json.JSONDecodeError:
                            continue

        except httpx.HTTPStatusError as e:
            logger.error(
                "OpenRouter streaming HTTP error", status_code=e.response.status_code
            )
            raise LLMError(f"OpenRouter streaming error: {e.response.status_code}")
        except Exception as e:
            logger.error("OpenRouter streaming unexpected error", error=str(e))
            raise LLMError(f"OpenRouter streaming error: {str(e)}")

    async def stream_generate(  # type: ignore[override]
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """ストリーミングテキスト生成"""
        try:
            payload = {
                "model": model or self.default_model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens or 1000,
                "temperature": temperature or 0.7,
                "stream": True,
            }

            async with self.client.stream(
                "POST", "/chat/completions", json=payload
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]  # "data: " を除去
                        if data_str.strip() == "[DONE]":
                            break

                        try:
                            data = json.loads(data_str)
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    content: str = delta["content"]
                                    yield content
                        except json.JSONDecodeError:
                            continue

        except httpx.HTTPStatusError as e:
            logger.error(
                "OpenRouter streaming HTTP error", status_code=e.response.status_code
            )
            raise LLMError(f"OpenRouter streaming error: {e.response.status_code}")
        except Exception as e:
            logger.error("OpenRouter streaming unexpected error", error=str(e))
            raise LLMError(f"OpenRouter streaming error: {str(e)}")

    async def is_available(self) -> bool:
        """プロバイダーが利用可能かチェック"""
        try:
            response = await self.client.get("/models")
            return response.status_code == 200
        except Exception:
            return False

    async def health_check(self) -> bool:
        """ヘルスチェック"""
        return await self.is_available()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
