"""
設定 API Keys

用法:
    python set_keys.py

或直接改下面的值然後執行
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python", "src"))

from meei.config import config

# ===== 在這裡填入你的 API Keys =====

KEYS = {
    "deepseek": "",   # https://platform.deepseek.com/
    "openai": "",     # https://platform.openai.com/
    "gemini": "",     # https://aistudio.google.com/
    "qwen": "",       # https://dashscope.console.aliyun.com/
    "groq": "",       # https://console.groq.com/
}

# ===================================


def main():
    print("設定 API Keys")
    print("=" * 40)

    for provider, key in KEYS.items():
        if key:
            config.set(f"{provider}.api_key", key)
            print(f"✅ {provider}: 已設定")
        else:
            existing = config.get(f"{provider}.api_key")
            if existing:
                print(f"⏭️  {provider}: 已有 key (跳過)")
            else:
                print(f"⚠️  {provider}: 未填寫")

    print()
    print("完成! 現在可以執行:")
    print("  python test_all.py")
    print("  python quick_test.py deepseek '你好'")


if __name__ == "__main__":
    main()
