"""
Google AI Studio プロバイダー実装
"""

import httpx
from typing import AsyncGenerator, Optional
import json
import structlog

from .base import ILLMProvider, LLMResponse, LLMError

logger = structlog.get_logger(__name__)


class GoogleAIProvider(ILLMProvider):
    """Google AI Studio プロバイダー"""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    @property
    def provider_name(self) -> str:
        return "google_ai"

    @property
    def default_model(self) -> str:
        return "gemini-pro"

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
            model_name = model or self.default_model
            url = f"/models/{model_name}:generateContent"

            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "maxOutputTokens": max_tokens or 1000,
                    "temperature": temperature or 0.7,
                },
            }

            params = {"key": self.api_key}
            response = await self.client.post(url, json=payload, params=params)
            response.raise_for_status()

            data = response.json()

            if "candidates" not in data or len(data["candidates"]) == 0:
                raise LLMError("No candidates in Google AI response")

            content = data["candidates"][0]["content"]["parts"][0]["text"]

            return LLMResponse(
                content=content,
                provider=self.provider_name,
                model=model_name,
                usage=data.get("usageMetadata"),
                metadata={"response_id": data.get("modelVersion")},
            )

        except httpx.HTTPStatusError as e:
            logger.error(
                "Google AI HTTP error",
                status_code=e.response.status_code,
                response=e.response.text,
            )
            raise LLMError(f"Google AI API error: {e.response.status_code}")
        except Exception as e:
            logger.error("Google AI unexpected error", error=str(e))
            raise LLMError(f"Google AI error: {str(e)}")

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
            model_name = model or self.default_model
            url = f"/models/{model_name}:streamGenerateContent"

            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "maxOutputTokens": max_tokens or 1000,
                    "temperature": temperature or 0.7,
                },
            }

            params = {"key": self.api_key}

            async with self.client.stream(
                "POST", url, json=payload, params=params
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if "candidates" in data and len(data["candidates"]) > 0:
                                candidate = data["candidates"][0]
                                if (
                                    "content" in candidate
                                    and "parts" in candidate["content"]
                                ):
                                    for part in candidate["content"]["parts"]:
                                        if "text" in part:
                                            text_content: str = part["text"]
                                            yield text_content
                        except json.JSONDecodeError:
                            continue

        except httpx.HTTPStatusError as e:
            logger.error(
                "Google AI streaming HTTP error", status_code=e.response.status_code
            )
            raise LLMError(f"Google AI streaming error: {e.response.status_code}")
        except Exception as e:
            logger.error("Google AI streaming unexpected error", error=str(e))
            raise LLMError(f"Google AI streaming error: {str(e)}")

    async def stream(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs,
    ) -> AsyncGenerator[LLMResponse, None]:
        """ストリーミングレスポンス生成"""
        async for content in self.stream_generate(
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        ):
            yield LLMResponse(
                content=content,
                provider=self.provider_name,
                model=model or self.default_model,
                usage=None,
                metadata={"chunk": True},
            )

    async def is_available(self) -> bool:
        """プロバイダーが利用可能かチェック"""
        try:
            # Google AI APIの場合、モデル一覧取得でヘルスチェック
            response = await self.client.get(f"/models/{self.default_model}")
            return bool(response.status_code == 200)
        except Exception:
            return False

    async def health_check(self) -> bool:
        """ヘルスチェック"""
        return await self.is_available()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
