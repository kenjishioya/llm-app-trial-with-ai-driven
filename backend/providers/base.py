"""
LLM Provider基底クラス
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class LLMError(Exception):
    """LLMプロバイダーエラー"""

    pass


class LLMProviderType(Enum):
    """LLMプロバイダータイプ"""

    OPENROUTER = "openrouter"
    GOOGLE_AI = "google_ai"
    AZURE_OPENAI = "azure_openai"


@dataclass
class LLMResponse:
    """LLM応答データクラス"""

    content: str
    provider: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class ILLMProvider(ABC):
    """LLMプロバイダーインターフェース"""

    def __init__(self, api_key: str = "", **kwargs):
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> LLMResponse:
        """テキスト生成"""
        pass

    @abstractmethod
    async def stream_generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """ストリーミングテキスト生成"""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """プロバイダーが利用可能かチェック"""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """プロバイダー名"""
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        """デフォルトモデル名"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """ヘルスチェック"""
        pass
