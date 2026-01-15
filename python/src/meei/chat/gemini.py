"""
Google Gemini Chat Provider

Gemini API 文檔: https://ai.google.dev/gemini-api/docs

支援模型:
- gemini-1.5-pro: 最強多模態
- gemini-1.5-flash: 快速版
- gemini-2.0-flash-exp: 實驗版
- gemini-1.0-pro: 舊版

價格 (per 1M tokens, 2024):
- gemini-1.5-pro: Input $1.25, Output $5.00
- gemini-1.5-flash: Input $0.075, Output $0.30
- gemini-2.0-flash-exp: 免費 (實驗版)

注意: Gemini API 使用不同的 endpoint 結構，需特殊處理
"""

from typing import Dict, Any, List, Optional

import httpx

from meei.chat.base import ChatProvider
from meei.config import config
from meei.exceptions import AuthenticationError


class GeminiChat(ChatProvider):
    """Google Gemini Chat Provider"""

    PROVIDER_NAME = "gemini"
    DEFAULT_MODEL = "gemini-2.0-flash"
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    # 預設價格 (per 1K tokens) - gemini-2.0-flash
    PRICE_INPUT = 0.0
    PRICE_OUTPUT = 0.0

    # 模型別名對照
    MODEL_ALIASES = {
        "pro": "gemini-1.5-pro",
        "flash": "gemini-2.0-flash",
        "2.0": "gemini-2.0-flash",
        "1.5": "gemini-1.5-flash",
        "1.0": "gemini-1.0-pro",
    }

    # 各模型價格 (per 1K tokens)
    MODEL_PRICES = {
        "gemini-2.0-flash": {"input": 0.0, "output": 0.0},
        "gemini-1.5-pro": {"input": 0.00125, "output": 0.005},
        "gemini-1.5-flash": {"input": 0.000075, "output": 0.0003},
        "gemini-1.0-pro": {"input": 0.0005, "output": 0.0015},
    }

    def _resolve_model(self, model: str) -> str:
        """解析模型名稱（支援別名）"""
        return self.MODEL_ALIASES.get(model, model)

    def _get_headers(self) -> Dict[str, str]:
        """Gemini 使用 URL 參數傳遞 API key"""
        return {"Content-Type": "application/json"}

    @property
    def client(self) -> httpx.Client:
        """取得 HTTP client（不含 base_url，因為 Gemini 需要動態構建）"""
        if not self._client:
            self._client = httpx.Client(
                headers=self._get_headers(),
                timeout=120.0,
            )
        return self._client

    def _calculate_cost(self, input_tokens: int, output_tokens: int, model: str = None) -> float:
        """根據模型計算花費"""
        model = model or self.DEFAULT_MODEL
        prices = self.MODEL_PRICES.get(model, {"input": self.PRICE_INPUT, "output": self.PRICE_OUTPUT})
        return (input_tokens * prices["input"] + output_tokens * prices["output"]) / 1000

    def _convert_messages_to_gemini(self, messages: List[Dict[str, str]]) -> tuple:
        """
        將標準 messages 轉換為 Gemini 格式

        Returns:
            (contents, system_instruction)
        """
        contents = []
        system_instruction = None

        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")

            if role == "system":
                system_instruction = content
            elif role == "user":
                contents.append({"role": "user", "parts": [{"text": content}]})
            elif role == "assistant":
                contents.append({"role": "model", "parts": [{"text": content}]})

        return contents, system_instruction

    def _build_payload(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: Optional[float],
        max_tokens: Optional[int],
        stream: bool,
    ) -> Dict[str, Any]:
        """建立請求 payload (Gemini 格式)"""
        contents, system_instruction = self._convert_messages_to_gemini(messages)

        payload = {"contents": contents}

        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        generation_config = {}
        if temperature is not None:
            generation_config["temperature"] = temperature
        if max_tokens is not None:
            generation_config["maxOutputTokens"] = max_tokens

        if generation_config:
            payload["generationConfig"] = generation_config

        return payload

    def _parse_response(self, data: Dict[str, Any]) -> tuple:
        """
        解析回應

        Returns:
            (content, input_tokens, output_tokens, model)
        """
        candidates = data.get("candidates", [{}])
        if not candidates:
            return "", 0, 0, self.DEFAULT_MODEL

        content_parts = candidates[0].get("content", {}).get("parts", [])
        content = "".join(part.get("text", "") for part in content_parts)

        usage = data.get("usageMetadata", {})
        input_tokens = usage.get("promptTokenCount", 0)
        output_tokens = usage.get("candidatesTokenCount", 0)
        model = data.get("modelVersion", self.DEFAULT_MODEL)

        return content, input_tokens, output_tokens, model

    def conversation(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        system: str = None,
        temperature: float = None,
        max_tokens: int = None,
        stream: bool = False,
    ) -> str:
        """多輪對話 - 覆寫以使用 Gemini API"""
        import time
        from meei.tracker import track

        model = self._resolve_model(model or self.DEFAULT_MODEL)

        if system and (not messages or messages[0].get("role") != "system"):
            messages = [{"role": "system", "content": system}] + messages

        payload = self._build_payload(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
        )

        # Gemini endpoint 格式
        endpoint = f"{self.base_url}/models/{model}:generateContent?key={self.api_key}"

        start_time = time.time()
        response = self.client.post(endpoint, json=payload)
        latency_ms = int((time.time() - start_time) * 1000)

        if response.status_code != 200:
            self._handle_error(response)

        data = response.json()
        content, input_tokens, output_tokens, used_model = self._parse_response(data)

        track(
            provider=self.PROVIDER_NAME,
            type="chat",
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=self._calculate_cost(input_tokens, output_tokens, model),
            latency_ms=latency_ms,
            prompt=messages[-1].get("content", ""),
        )

        return content


# 便捷函數
def gemini(
    prompt: str,
    model: str = None,
    system: str = None,
    temperature: float = None,
    max_tokens: int = None,
    stream: bool = False,
):
    """
    Gemini 快捷函數

    用法:
        from meei.chat.gemini import gemini

        # 簡單對話
        response = gemini("你好")

        # 指定模型
        response = gemini("解釋相對論", model="pro")

        # 使用最新實驗版
        response = gemini("寫個程式", model="2.0")
    """
    provider = GeminiChat()
    return provider.chat(
        prompt=prompt,
        model=model,
        system=system,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=stream,
    )
