"""
DeepSeek Chat Provider

DeepSeek API 文檔: https://platform.deepseek.com/api-docs/

支援模型:
- deepseek-chat: 通用對話模型
- deepseek-coder: 程式碼專用模型
- deepseek-reasoner: 推理模型 (R1)

價格 (per 1M tokens, 2024):
- deepseek-chat: Input $0.14, Output $0.28
- deepseek-coder: Input $0.14, Output $0.28
- deepseek-reasoner: Input $0.55, Output $2.19
"""

from typing import Dict, Any, List, Optional

from meei.chat.base import ChatProvider


class DeepSeekChat(ChatProvider):
    """DeepSeek Chat Provider"""

    PROVIDER_NAME = "deepseek"
    DEFAULT_MODEL = "deepseek-chat"
    BASE_URL = "https://api.deepseek.com"

    # 價格 (per 1K tokens) - deepseek-chat
    PRICE_INPUT = 0.00014
    PRICE_OUTPUT = 0.00028

    # 模型別名對照
    MODEL_ALIASES = {
        "chat": "deepseek-chat",
        "coder": "deepseek-coder",
        "reasoner": "deepseek-reasoner",
        "r1": "deepseek-reasoner",
    }

    # 各模型價格 (per 1K tokens)
    MODEL_PRICES = {
        "deepseek-chat": {"input": 0.00014, "output": 0.00028},
        "deepseek-coder": {"input": 0.00014, "output": 0.00028},
        "deepseek-reasoner": {"input": 0.00055, "output": 0.00219},
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
def deepseek(
    prompt: str,
    model: str = None,
    system: str = None,
    temperature: float = None,
    max_tokens: int = None,
    stream: bool = False,
):
    """
    DeepSeek 快捷函數

    用法:
        from meei.chat.deepseek import deepseek

        # 簡單對話
        response = deepseek("你好")

        # 指定模型
        response = deepseek("寫個快速排序", model="coder")

        # 使用 R1 推理模型
        response = deepseek("解釋量子糾纏", model="r1")

        # 串流輸出
        for chunk in deepseek("講個故事", stream=True):
            print(chunk, end="")
    """
    provider = DeepSeekChat()
    return provider.chat(
        prompt=prompt,
        model=model,
        system=system,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=stream,
    )
