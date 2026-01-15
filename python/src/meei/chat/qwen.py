"""
Alibaba Qwen (通義千問) Chat Provider

Qwen API 文檔: https://help.aliyun.com/zh/model-studio/

支援模型:
- qwen-turbo: 快速版
- qwen-plus: 增強版
- qwen-max: 最強版
- qwen-long: 長文本版 (1M tokens)
- qwen-coder-turbo: 程式碼專用

價格 (per 1M tokens, 人民幣):
- qwen-turbo: Input ¥0.3, Output ¥0.6
- qwen-plus: Input ¥0.8, Output ¥2.0
- qwen-max: Input ¥20.0, Output ¥60.0

注意: Qwen 使用 DashScope API，與 OpenAI 格式類似但有些差異
"""

from typing import Dict, Any, List, Optional

from meei.chat.base import ChatProvider


class QwenChat(ChatProvider):
    """Alibaba Qwen Chat Provider"""

    PROVIDER_NAME = "qwen"
    DEFAULT_MODEL = "qwen-turbo"
    BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"

    # 預設價格 (per 1K tokens, 轉換為 USD) - qwen-turbo
    # 匯率約 7.2，所以 ¥0.3/1M ≈ $0.042/1M = $0.000042/1K
    PRICE_INPUT = 0.000042
    PRICE_OUTPUT = 0.000083

    # 模型別名對照
    MODEL_ALIASES = {
        "turbo": "qwen-turbo",
        "plus": "qwen-plus",
        "max": "qwen-max",
        "long": "qwen-long",
        "coder": "qwen-coder-turbo",
    }

    # 各模型價格 (per 1K tokens, USD)
    MODEL_PRICES = {
        "qwen-turbo": {"input": 0.000042, "output": 0.000083},
        "qwen-plus": {"input": 0.00011, "output": 0.00028},
        "qwen-max": {"input": 0.0028, "output": 0.0083},
        "qwen-long": {"input": 0.00007, "output": 0.00028},
        "qwen-coder-turbo": {"input": 0.00028, "output": 0.00083},
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
def qwen(
    prompt: str,
    model: str = None,
    system: str = None,
    temperature: float = None,
    max_tokens: int = None,
    stream: bool = False,
):
    """
    Qwen 快捷函數

    用法:
        from meei.chat.qwen import qwen

        # 簡單對話
        response = qwen("你好")

        # 指定模型
        response = qwen("寫篇長文", model="long")

        # 程式碼生成
        response = qwen("寫個快速排序", model="coder")

        # 最強模型
        response = qwen("複雜推理問題", model="max")
    """
    provider = QwenChat()
    return provider.chat(
        prompt=prompt,
        model=model,
        system=system,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=stream,
    )
