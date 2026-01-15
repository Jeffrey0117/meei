"""
Groq Chat Provider

Groq API 文檔: https://console.groq.com/docs/quickstart

支援模型:
- llama-3.3-70b-versatile: Llama 3.3 70B
- llama-3.1-8b-instant: Llama 3.1 8B (快速)
- mixtral-8x7b-32768: Mixtral 8x7B
- gemma2-9b-it: Gemma 2 9B

Groq 提供超快推理速度，適合需要低延遲的場景
"""

from typing import Dict, Any, List, Optional

from meei.chat.base import ChatProvider


class GroqChat(ChatProvider):
    """Groq Chat Provider"""

    PROVIDER_NAME = "groq"
    DEFAULT_MODEL = "llama-3.3-70b-versatile"
    BASE_URL = "https://api.groq.com/openai/v1"

    # 預設價格 (per 1K tokens)
    PRICE_INPUT = 0.00059
    PRICE_OUTPUT = 0.00079

    # 模型別名對照
    MODEL_ALIASES = {
        "llama": "llama-3.3-70b-versatile",
        "llama70b": "llama-3.3-70b-versatile",
        "llama8b": "llama-3.1-8b-instant",
        "mixtral": "mixtral-8x7b-32768",
        "gemma": "gemma2-9b-it",
    }

    # 各模型價格 (per 1K tokens)
    MODEL_PRICES = {
        "llama-3.3-70b-versatile": {"input": 0.00059, "output": 0.00079},
        "llama-3.1-8b-instant": {"input": 0.00005, "output": 0.00008},
        "mixtral-8x7b-32768": {"input": 0.00024, "output": 0.00024},
        "gemma2-9b-it": {"input": 0.0002, "output": 0.0002},
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
def groq(
    prompt: str,
    model: str = None,
    system: str = None,
    temperature: float = None,
    max_tokens: int = None,
    stream: bool = False,
):
    """
    Groq 快捷函數

    用法:
        from meei.chat.groq import groq

        # 簡單對話 (預設 Llama 3.3 70B)
        response = groq("你好")

        # 快速模型
        response = groq("快速回答", model="llama8b")

        # Mixtral
        response = groq("解釋問題", model="mixtral")
    """
    provider = GroqChat()
    return provider.chat(
        prompt=prompt,
        model=model,
        system=system,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=stream,
    )
