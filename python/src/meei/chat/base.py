"""
Chat Provider 基礎類別
"""

import os
import time
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Generator, Union

import httpx

from meei.config import config
from meei.tracker import track
from meei.exceptions import AuthenticationError, RateLimitError, APIError

# 環境變數名稱對照
ENV_KEY_MAP = {
    "deepseek": "DEEPSEEK_API_KEY",
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "qwen": "QWEN_API_KEY",
    "groq": "GROQ_API_KEY",
}


class ChatProvider(ABC):
    """Chat Provider 抽象基礎類別"""

    # 子類別需覆寫
    PROVIDER_NAME: str = ""
    DEFAULT_MODEL: str = ""
    BASE_URL: str = ""

    # 價格 (per 1K tokens)
    PRICE_INPUT: float = 0.0
    PRICE_OUTPUT: float = 0.0

    def __init__(self):
        self._client: Optional[httpx.Client] = None
        self._async_client: Optional[httpx.AsyncClient] = None

    @property
    def api_key(self) -> str:
        """取得 API key（優先順序：meei config > 環境變數）"""
        # 1. 先從 meei config 取得
        try:
            key = config.get(f"{self.PROVIDER_NAME}.api_key")
            if key:
                return key
        except Exception:
            pass

        # 2. Fallback 到環境變數
        env_name = ENV_KEY_MAP.get(self.PROVIDER_NAME)
        if env_name:
            key = os.environ.get(env_name)
            if key:
                return key

        raise AuthenticationError(
            self.PROVIDER_NAME,
            f"未設定 API key，請執行: meei config set {self.PROVIDER_NAME}.api_key YOUR_KEY\n"
            f"或設定環境變數: {ENV_KEY_MAP.get(self.PROVIDER_NAME, self.PROVIDER_NAME.upper() + '_API_KEY')}",
        )
        return key

    @property
    def base_url(self) -> str:
        """取得 Base URL（可自訂）"""
        return config.get(f"{self.PROVIDER_NAME}.base_url") or self.BASE_URL

    @property
    def client(self) -> httpx.Client:
        """取得 HTTP client"""
        if not self._client:
            self._client = httpx.Client(
                base_url=self.base_url,
                headers=self._get_headers(),
                timeout=120.0,
            )
        return self._client

    @property
    def async_client(self) -> httpx.AsyncClient:
        """取得非同步 HTTP client"""
        if not self._async_client:
            self._async_client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self._get_headers(),
                timeout=120.0,
            )
        return self._async_client

    def _get_headers(self) -> Dict[str, str]:
        """取得請求標頭"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """計算花費"""
        return (input_tokens * self.PRICE_INPUT + output_tokens * self.PRICE_OUTPUT) / 1000

    def _handle_error(self, response: httpx.Response):
        """處理錯誤回應"""
        if response.status_code == 401:
            raise AuthenticationError(self.PROVIDER_NAME, "API key 無效")
        elif response.status_code == 429:
            raise RateLimitError(self.PROVIDER_NAME, "超過請求限制，請稍後再試")
        elif response.status_code >= 400:
            try:
                error_msg = response.json().get("error", {}).get("message", response.text)
            except Exception:
                error_msg = response.text
            raise APIError(self.PROVIDER_NAME, response.status_code, error_msg)

    @abstractmethod
    def _build_payload(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: Optional[float],
        max_tokens: Optional[int],
        stream: bool,
    ) -> Dict[str, Any]:
        """建立請求 payload"""
        pass

    @abstractmethod
    def _parse_response(self, data: Dict[str, Any]) -> tuple:
        """
        解析回應

        Returns:
            (content, input_tokens, output_tokens, model)
        """
        pass

    def chat(
        self,
        prompt: str,
        model: str = None,
        system: str = None,
        temperature: float = None,
        max_tokens: int = None,
        stream: bool = False,
    ) -> Union[str, Generator[str, None, None]]:
        """發送聊天請求"""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        return self.conversation(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
        )

    def conversation(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        system: str = None,
        temperature: float = None,
        max_tokens: int = None,
        stream: bool = False,
    ) -> Union[str, Generator[str, None, None]]:
        """多輪對話"""
        model = model or self.DEFAULT_MODEL

        # 如果有 system 且 messages 第一條不是 system
        if system and (not messages or messages[0].get("role") != "system"):
            messages = [{"role": "system", "content": system}] + messages

        payload = self._build_payload(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
        )

        start_time = time.time()

        if stream:
            return self._stream_response(payload, prompt=messages[-1].get("content", ""))

        response = self.client.post("/chat/completions", json=payload)
        latency_ms = int((time.time() - start_time) * 1000)

        if response.status_code != 200:
            self._handle_error(response)

        data = response.json()
        content, input_tokens, output_tokens, used_model = self._parse_response(data)

        # 記錄用量
        track(
            provider=self.PROVIDER_NAME,
            type="chat",
            model=used_model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=self._calculate_cost(input_tokens, output_tokens),
            latency_ms=latency_ms,
            prompt=messages[-1].get("content", ""),
        )

        return content

    def _stream_response(self, payload: Dict, prompt: str) -> Generator[str, None, None]:
        """串流回應"""
        start_time = time.time()
        total_content = ""

        with self.client.stream("POST", "/chat/completions", json=payload) as response:
            if response.status_code != 200:
                self._handle_error(response)

            for line in response.iter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        import json

                        chunk = json.loads(data)
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            total_content += content
                            yield content
                    except Exception:
                        continue

        latency_ms = int((time.time() - start_time) * 1000)

        # 記錄用量（串流模式無法取得精確 token 數）
        track(
            provider=self.PROVIDER_NAME,
            type="chat",
            model=payload.get("model"),
            latency_ms=latency_ms,
            prompt=prompt,
        )

    async def chat_async(
        self,
        prompt: str,
        model: str = None,
        system: str = None,
        temperature: float = None,
        max_tokens: int = None,
    ) -> str:
        """非同步聊天請求"""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        model = model or self.DEFAULT_MODEL

        payload = self._build_payload(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
        )

        start_time = time.time()
        response = await self.async_client.post("/chat/completions", json=payload)
        latency_ms = int((time.time() - start_time) * 1000)

        if response.status_code != 200:
            self._handle_error(response)

        data = response.json()
        content, input_tokens, output_tokens, used_model = self._parse_response(data)

        track(
            provider=self.PROVIDER_NAME,
            type="chat",
            model=used_model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=self._calculate_cost(input_tokens, output_tokens),
            latency_ms=latency_ms,
            prompt=prompt,
        )

        return content
