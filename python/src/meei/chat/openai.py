"""
OpenAI Chat Provider

OpenAI API 文檔: https://platform.openai.com/docs/api-reference

支援模型:
- gpt-4o: 最新多模態模型
- gpt-4o-mini: 輕量版
- gpt-4-turbo: GPT-4 Turbo
- gpt-3.5-turbo: GPT-3.5

價格 (per 1M tokens, 2024):
- gpt-4o: Input $2.50, Output $10.00
- gpt-4o-mini: Input $0.15, Output $0.60
- gpt-4-turbo: Input $10.00, Output $30.00
- gpt-3.5-turbo: Input $0.50, Output $1.50
"""

from typing import Dict, Any, List, Optional

from meei.chat.base import ChatProvider


class OpenAIChat(ChatProvider):
    """OpenAI Chat Provider"""

    PROVIDER_NAME = "openai"
    DEFAULT_MODEL = "gpt-4o-mini"
    BASE_URL = "https://api.openai.com/v1"

    # 預設價格 (per 1K tokens) - gpt-4o-mini
    PRICE_INPUT = 0.00015
    PRICE_OUTPUT = 0.0006

    # 模型別名對照
    MODEL_ALIASES = {
        "4o": "gpt-4o",
        "4o-mini": "gpt-4o-mini",
        "4-turbo": "gpt-4-turbo",
        "3.5": "gpt-3.5-turbo",
        "turbo": "gpt-3.5-turbo",
    }

    # 各模型價格 (per 1K tokens)
    MODEL_PRICES = {
        "gpt-4o": {"input": 0.0025, "output": 0.01},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    }

    def _resolve_model(self, model: str) -> str:
        """解析模型名稱（支援別名）"""
        return self.MODEL_ALIASES.get(model, model)

    def _calculate_cost(self, input_tokens: int, output_tokens: int, model: str = None) -> float:
        """根據模型計算花費"""
        model = model or self.DEFAULT_MODEL
        prices = self.MODEL_PRICES.get(model, {"input": self.PRICE_INPUT, "output": self.PRICE_OUTPUT})
        return (input_tokens * prices["input"] + output_tokens * prices["output"]) / 1000

    def _build_payload(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: Optional[float],
        max_tokens: Optional[int],
        stream: bool,
    ) -> Dict[str, Any]:
        """建立請求 payload"""
        model = self._resolve_model(model)

        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
        }

        if temperature is not None:
            payload["temperature"] = temperature

        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        return payload

    def _parse_response(self, data: Dict[str, Any]) -> tuple:
        """
        解析回應

        Returns:
            (content, input_tokens, output_tokens, model)
        """
        choice = data.get("choices", [{}])[0]
        message = choice.get("message", {})
        content = message.get("content", "")

        usage = data.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        model = data.get("model", self.DEFAULT_MODEL)

        return content, input_tokens, output_tokens, model


# 便捷函數
def openai(
    prompt: str,
    model: str = None,
    system: str = None,
    temperature: float = None,
    max_tokens: int = None,
    stream: bool = False,
):
    """
    OpenAI 快捷函數

    用法:
        from meei.chat.openai import openai

        # 簡單對話
        response = openai("你好")

        # 指定模型
        response = openai("解釋量子力學", model="4o")

        # 串流輸出
        for chunk in openai("講個故事", stream=True):
            print(chunk, end="")
    """
    provider = OpenAIChat()
    return provider.chat(
        prompt=prompt,
        model=model,
        system=system,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=stream,
    )
