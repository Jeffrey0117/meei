"""
meei 測試腳本 - 測試所有 Provider

用法:
    python test_all.py

執行前先設定 API key:
    meei config set deepseek.api_key sk-xxx
    meei config set openai.api_key sk-xxx
    meei config set gemini.api_key xxx
    meei config set qwen.api_key sk-xxx
    meei config set groq.api_key gsk-xxx
"""

import sys
import os

# 加入 python/src 到 path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python", "src"))

from meei.chat import chat
from meei.config import config

# 測試用 prompt
TEST_PROMPT = "用一句話介紹你自己"

# 要測試的 providers
PROVIDERS = [
    ("deepseek", "deepseek-chat"),
    ("openai", "gpt-4o-mini"),
    ("gemini", "gemini-2.0-flash"),
    ("qwen", "qwen-turbo"),
    ("groq", "llama-3.3-70b-versatile"),
]


def test_provider(pv: str, model: str):
    """測試單一 provider"""
    print(f"\n{'='*50}")
    print(f"測試: {pv} ({model})")
    print(f"{'='*50}")

    # 檢查 API key
    api_key = config.get(f"{pv}.api_key")
    if not api_key:
        print(f"⚠️  跳過 - 未設定 {pv}.api_key")
        return False

    try:
        response = chat.ask(TEST_PROMPT, pv=pv, model=model)
        print(f"✅ 成功!")
        print(f"回應: {response[:200]}...")
        return True
    except Exception as e:
        print(f"❌ 失敗: {e}")
        return False


def main():
    print("meei Provider 測試")
    print("=" * 50)
    print(f"測試 Prompt: {TEST_PROMPT}")

    results = {}
    for pv, model in PROVIDERS:
        results[pv] = test_provider(pv, model)

    # 總結
    print("\n" + "=" * 50)
    print("測試結果總結")
    print("=" * 50)
    for pv, success in results.items():
        status = "✅ 通過" if success else "❌ 失敗/跳過"
        print(f"  {pv}: {status}")

    passed = sum(1 for s in results.values() if s)
    print(f"\n通過: {passed}/{len(PROVIDERS)}")


if __name__ == "__main__":
    main()
