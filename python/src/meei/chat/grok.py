"""
xAI Grok Chat Provider

Grok API 文檔: https://docs.x.ai/

支援模型:
- grok-2: 最新版
- grok-2-mini: 輕量版
- grok-beta: Beta 版

價格 (per 1M tokens, 2024):
- grok-2: Input $2.00, Output $10.00
- grok-2-mini: Input $0.20, Output $1.00
"""

from typing import Dict, Any, List, Optional

from meei.chat.base import ChatProvider


class GrokChat(ChatProvider):
    """xAI Grok Chat Provider"""

    PROVIDER_NAME = "grok"
    DEFAULT_MODEL = "grok-2"
    BASE_URL = "https://api.x.ai/v1"

    # 預設價格 (per 1K tokens) - grok-2
    PRICE_INPUT = 0.002
    PRICE_OUTPUT = 0.01

    # 模型別名對照
    MODEL_ALIASES = {
        "2": "grok-2",
        "mini": "grok-2-mini",
        "beta": "grok-beta",
    }

    # 各模型價格 (per 1K tokens)
    MODEL_PRICES = {
        "grok-2": {"input": 0.002, "output": 0.01},
        "grok-2-mini": {"input": 0.0002, "output": 0.001},
        "grok-beta": {"input": 0.002, "output": 0.01},
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
def grok(
    prompt: str,
    model: str = None,
    system: str = None,
    temperature: float = None,
    max_tokens: int = None,
    stream: bool = False,
):
    """
    Grok 快捷函數

    用法:
        from meei.chat.grok import grok

        # 簡單對話
        response = grok("你好")

        # 使用輕量版
        response = grok("簡單問題", model="mini")

        # 串流輸出
        for chunk in grok("講個故事", stream=True):
            print(chunk, end="")
    """
    provider = GrokChat()
    return provider.chat(
        prompt=prompt,
        model=model,
        system=system,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=stream,
    )
