"""
Chat 模組 - 統一聊天介面
"""

from typing import Optional, List, Dict, Any, Union
from meei.chat.base import ChatProvider
from meei.chat.deepseek import DeepSeekChat
from meei.chat.openai import OpenAIChat
from meei.chat.gemini import GeminiChat
from meei.chat.qwen import QwenChat
from meei.chat.grok import GrokChat
from meei.config import config

# Provider 映射
PROVIDERS: Dict[str, type] = {
    "deepseek": DeepSeekChat,
    "openai": OpenAIChat,
    "chatgpt": OpenAIChat,  # alias
    "gemini": GeminiChat,
    "qwen": QwenChat,
    "grok": GrokChat,
}

# 預設 provider
DEFAULT_PROVIDER = "deepseek"


class Chat:
    """Chat 統一介面"""

    def __init__(self):
        self._instances: Dict[str, ChatProvider] = {}

    def _get_provider(self, pv: str) -> ChatProvider:
        """取得或建立 provider 實例"""
        if pv not in self._instances:
            if pv not in PROVIDERS:
                available = ", ".join(PROVIDERS.keys())
                raise ValueError(f"不支援的 provider: {pv}，可用: {available}")

            provider_class = PROVIDERS[pv]
            self._instances[pv] = provider_class()

        return self._instances[pv]

    def ask(
        self,
        prompt: str,
        pv: str = None,
        model: str = None,
        system: str = None,
        temperature: float = None,
        max_tokens: int = None,
        stream: bool = False,
    ) -> Union[str, Any]:
        """
        發送聊天請求

        Args:
            prompt: 用戶訊息
            pv: provider 名稱 (deepseek/openai/gemini/qwen/grok)
            model: 模型名稱（不指定則用 provider 預設）
            system: 系統提示詞
            temperature: 溫度 (0-2)
            max_tokens: 最大輸出 token 數
            stream: 是否串流回應

        Returns:
            回應文字，或串流時返回 generator
        """
        pv = pv or DEFAULT_PROVIDER
        provider = self._get_provider(pv)

        return provider.chat(
            prompt=prompt,
            model=model,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
        )

    async def ask_async(
        self,
        prompt: str,
        pv: str = None,
        model: str = None,
        system: str = None,
        temperature: float = None,
        max_tokens: int = None,
    ) -> str:
        """非同步聊天請求"""
        pv = pv or DEFAULT_PROVIDER
        provider = self._get_provider(pv)

        return await provider.chat_async(
            prompt=prompt,
            model=model,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def conversation(
        self,
        messages: List[Dict[str, str]],
        pv: str = None,
        model: str = None,
        system: str = None,
        temperature: float = None,
        max_tokens: int = None,
    ) -> str:
        """
        多輪對話

        Args:
            messages: 對話歷史 [{"role": "user", "content": "..."}, ...]
            pv: provider 名稱
            ...
        """
        pv = pv or DEFAULT_PROVIDER
        provider = self._get_provider(pv)

        return provider.conversation(
            messages=messages,
            model=model,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens,
        )


# 全域實例
chat = Chat()
